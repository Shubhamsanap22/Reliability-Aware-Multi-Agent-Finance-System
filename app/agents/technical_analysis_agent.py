import math
import re

import pandas as pd

from app.agents.base_agent import BaseAgent
from app.calculations.technical_metrics import (
    calculate_price_momentum,
    calculate_rsi,
    calculate_simple_moving_average,
    calculate_technical_score,
    classify_price_position,
    classify_rsi,
    classify_technical_strength,
)
from app.models.schemas import AgentState, AgentStatus


class TechnicalAnalysisAgent(BaseAgent):
    """Calculate technical indicators from historical closing prices."""

    SUPPORTED_SYMBOLS = {
        "TCS",
        "INFY",
        "RELIANCE",
        "HDFCBANK",
        "ICICIBANK",
        "SBIN",
        "AAPL",
        "MSFT",
        "GOOGL",
        "AMZN",
    }

    REQUIRED_BUDGET = 500

    def __init__(
        self,
        data_provider=None,
        local_file_path: str | None = None,
    ) -> None:
        super().__init__(
            name="Technical Analysis Agent",
            reliability=0.90,
            estimated_cost=700,
        )
        self.data_provider = data_provider
        self.local_file_path = local_file_path

    def execute(
        self,
        query: str,
        budget: int,
        market_data: pd.DataFrame | None = None,
    ) -> AgentState:
        required_budget = self.REQUIRED_BUDGET

        if budget < required_budget:
            return self._failed(budget, "Insufficient budget.")

        # Load data through the configured provider when possible.
        if market_data is None and self.data_provider is not None:
            if not self.local_file_path:
                return self._failed(
                    budget,
                    "Local data file path is not configured.",
                )

            try:
                market_data = self.data_provider.get_market_data(
                    symbol=self._get_preferred_symbol(query)
                    or "",
                    local_file_path=self.local_file_path,
                )
            except Exception as error:
                return self._failed(
                    budget,
                    f"Unable to load market data: {error}",
                )

        # Return an explicitly labelled fallback when no data source
        # has been provided. Do not fabricate technical indicators.
        if market_data is None:
            symbol = self._get_preferred_symbol(query)

            if symbol is None:
                return self._failed(
                    budget,
                    "No supported symbol found in query.",
                )

            return AgentState(
                agent_name=self.name,
                reliability=self.reliability,
                allocated_budget=budget,
                used_budget=required_budget,
                status=AgentStatus.COMPLETED,
                output=(
                    f"Technical Analysis Assessment for {symbol}\n\n"
                    "Dummy technical analysis completed.\n\n"
                    "Fallback result: no market data was supplied.\n"
                    "Technical indicators and technical score could not be calculated. "
                    "Provide historical market data to obtain an evidence-based assessment."
            ),
            )

        if not isinstance(market_data, pd.DataFrame):
            return self._failed(
                budget,
                "Market data must be a pandas DataFrame.",
            )

        if market_data.empty:
            return self._failed(budget, "Market data is empty.")

        # Validate columns before resolving a symbol against the data.
        if "symbol" not in market_data.columns:
            return self._failed(
                budget,
                "Market data does not contain a symbol column.",
            )

        if "close" not in market_data.columns:
            return self._failed(
                budget,
                "Market data does not contain a close column.",
            )

        if "date" not in market_data.columns:
            return self._failed(
                budget,
                "Market data does not contain a date column.",
            )

        available_symbols = (
            market_data["symbol"]
            .dropna()
            .astype(str)
            .str.strip()
            .str.upper()
            .unique()
            .tolist()
        )

        symbol = self._get_preferred_symbol(
            query,
            available_symbols=available_symbols,
        )

        if symbol is None:
            return self._failed(
                budget,
                "No supported symbol found in query.",
            )

        data = market_data.copy()
        data["symbol"] = (
            data["symbol"].astype(str).str.strip().str.upper()
        )
        data["date"] = pd.to_datetime(
            data["date"],
            errors="coerce",
        )
        data["close"] = pd.to_numeric(
            data["close"],
            errors="coerce",
        )

        if data[["symbol", "date", "close"]].isna().any().any():
            return self._failed(
                budget,
                "Market data contains invalid symbols, dates or prices.",
            )

        if (
            (data["close"] <= 0).any()
            or not data["close"].map(math.isfinite).all()
        ):
            return self._failed(
                budget,
                "Closing prices must be finite and greater than zero.",
            )

        symbol_data = data.loc[
            data["symbol"] == symbol.upper()
        ].sort_values("date")

        if symbol_data.empty:
            return self._failed(
                budget,
                "No supported symbol found in query.",
            )

        if symbol_data["date"].duplicated().any():
            return self._failed(
                budget,
                f"Duplicate dates found for {symbol}; clean the data first.",
            )

        prices = symbol_data["close"].astype(float)

        try:
            moving_average = calculate_simple_moving_average(
                prices,
                window=20,
            )
            momentum = calculate_price_momentum(
                prices,
                lookback=10,
            )
            rsi = calculate_rsi(
                prices,
                period=14,
            )

            latest_price = float(prices.iloc[-1])

            price_position = classify_price_position(
                latest_price,
                moving_average,
            )
            rsi_classification = classify_rsi(rsi)

            technical_score = calculate_technical_score(
                momentum,
                rsi,
                price_position,
            )
            technical_strength = classify_technical_strength(
                technical_score
            )

            values = (
                moving_average,
                momentum,
                rsi,
                latest_price,
                technical_score,
            )

            if not all(math.isfinite(value) for value in values):
                raise ValueError(
                    "Technical indicators produced a non-finite result."
                )

        except (ValueError, ZeroDivisionError) as error:
            return self._failed(budget, str(error))

        output = self._build_output(
            symbol=symbol,
            latest_price=latest_price,
            moving_average=moving_average,
            momentum=momentum,
            rsi=rsi,
            rsi_classification=rsi_classification,
            price_position=price_position,
            technical_score=technical_score,
            technical_strength=technical_strength,
        )

        return AgentState(
            agent_name=self.name,
            reliability=self.reliability,
            allocated_budget=budget,
            used_budget=required_budget,
            status=AgentStatus.COMPLETED,
            output=output,
        )

    def _failed(self, budget: int, reason: str) -> AgentState:
        return AgentState(
            agent_name=self.name,
            reliability=self.reliability,
            allocated_budget=budget,
            used_budget=0,
            status=AgentStatus.FAILED,
            failure_reason=reason,
        )

    def _get_preferred_symbol(
        self,
        query: str,
        available_symbols=None,
    ) -> str | None:
        if self.task_requirement and self.task_requirement.symbols:
            requested = [
                str(value).strip().upper()
                for value in self.task_requirement.symbols
            ]

            if available_symbols is None:
                return next(
                    (
                        symbol
                        for symbol in requested
                        if symbol in self.SUPPORTED_SYMBOLS
                    ),
                    None,
                )

            available = {
                str(value).strip().upper()
                for value in available_symbols
            }

            return next(
                (
                    symbol
                    for symbol in requested
                    if symbol in self.SUPPORTED_SYMBOLS
                    and symbol in available
                ),
                None,
            )

        return self._find_symbol_in_query(
            query,
            available_symbols,
        )

    @classmethod
    def _find_symbol_in_query(
        cls,
        query: str,
        available_symbols=None,
    ) -> str | None:
        candidates = (
            cls.SUPPORTED_SYMBOLS
            if available_symbols is None
            else {
                str(value).strip().upper()
                for value in available_symbols
            }
        )

        for symbol in sorted(candidates):
            if symbol not in cls.SUPPORTED_SYMBOLS:
                continue

            if re.search(
                rf"\b{re.escape(symbol)}\b",
                query.upper(),
            ):
                return symbol

        return None

    @staticmethod
    def _build_output(
        symbol,
        latest_price,
        moving_average,
        momentum,
        rsi,
        rsi_classification,
        price_position,
        technical_score,
        technical_strength,
    ) -> str:
        return (
            f"Technical Analysis Assessment for {symbol}\n\n"
            f"Overall Assessment: {technical_strength}\n\n"
            f"Latest closing price: {latest_price:.2f}\n"
            f"20-day moving average: {moving_average:.2f}\n"
            f"Price position: {price_position}\n"
            f"10-period price momentum: {momentum * 100:.2f}%\n"
            f"RSI (14-period): {rsi:.2f} ({rsi_classification})\n"
            f"Technical Score (project heuristic): "
            f"{technical_score:.2f}\n\n"
            "This assessment requires sufficient historical observations "
            "for the requested indicators and uses historical prices only. "
            "It is not a trading recommendation and does not guarantee "
            "future performance."
        )