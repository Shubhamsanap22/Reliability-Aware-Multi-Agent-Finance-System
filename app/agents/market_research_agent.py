import pandas as pd

from app.agents.base_agent import BaseAgent
from app.calculations.market_metrics import (
    calculate_average_volume,
    calculate_price_trend,
    calculate_total_return,
    calculate_volume_trend,
    classify_market_trend,
)
from app.calculations.risk_metrics import (
    calculate_returns,
    calculate_volatility,
)
from app.models.schemas import AgentState, AgentStatus


class MarketResearchAgent(BaseAgent):
    """Analyze historical price and trading-volume trends."""

    def __init__(
        self,
        data_provider=None,
        local_file_path: str | None = None,
    ) -> None:
        super().__init__(
            name="Market Research Agent",
            reliability=0.89,
            estimated_cost=650,
        )
        self.data_provider = data_provider
        self.local_file_path = local_file_path

    def execute(
        self,
        query: str,
        budget: int,
        market_data: pd.DataFrame | None = None,
    ) -> AgentState:
        required_budget = 450

        if budget < required_budget:
            return self._failed(budget, "Insufficient budget.")

        if market_data is None and self.data_provider is not None:
            if not self.local_file_path:
                return self._failed(
                    budget,
                    "Local data file path is not configured.",
                )

            symbol = self._get_preferred_symbol(query)

            if symbol is None:
                return self._failed(
                    budget,
                    "No supported symbol found in query.",
                )

            try:
                market_data = self.data_provider.get_market_data(
                    symbol=symbol,
                    local_file_path=self.local_file_path,
                )
            except Exception as error:
                return self._failed(
                    budget,
                    f"Unable to load market data: {error}",
                )

        if market_data is None:
            return self._failed(
                budget,
                "Market data is unavailable. Configure a provider "
                "or supply market_data.",
            )

        if market_data.empty:
            return self._failed(budget, "Market data is empty.")

        required_columns = {"symbol", "date", "close", "volume"}
        missing = required_columns.difference(market_data.columns)

        if missing:
            return self._failed(
                budget,
                f"Market data is missing required columns: {sorted(missing)}",
            )

        data = market_data.copy()
        data["symbol"] = data["symbol"].astype(str).str.upper()
        data["date"] = pd.to_datetime(data["date"], errors="coerce")

        for column in ("close", "volume"):
            data[column] = pd.to_numeric(
                data[column],
                errors="coerce",
            )

        if data[["symbol", "date", "close", "volume"]].isna().any().any():
            return self._failed(
                budget,
                "Market data contains invalid symbols, dates, prices or volumes.",
            )

        if (data["close"] <= 0).any() or (data["volume"] < 0).any():
            return self._failed(
                budget,
                "Closing prices must be positive and volumes non-negative.",
            )

        symbol = self._get_preferred_symbol(
            query,
            available_symbols=data["symbol"].unique(),
        )

        if symbol is None:
            return self._failed(
                budget,
                "No supported symbol found in query.",
            )

        symbol_data = data.loc[
            data["symbol"] == symbol.upper()
        ].copy()

        if symbol_data.empty:
            return self._failed(
                budget,
                f"No market data found for {symbol}.",
            )

        symbol_data = symbol_data.sort_values("date")

        if symbol_data["date"].duplicated().any():
            return self._failed(
                budget,
                f"Duplicate dates found for {symbol}.",
            )

        if len(symbol_data) < 3:
            return self._failed(
                budget,
                "At least three observations are required for market research.",
            )

        prices = symbol_data["close"].astype(float)
        volume = symbol_data["volume"].astype(float)

        try:
            price_trend = calculate_price_trend(prices)
            volume_trend = calculate_volume_trend(volume)

            market_trend = classify_market_trend(
                price_trend=price_trend,
                volume_trend=volume_trend,
            )

            total_return = calculate_total_return(prices)
            average_volume = calculate_average_volume(volume)

            returns = calculate_returns(prices)
            volatility = calculate_volatility(returns)

        except (ValueError, ZeroDivisionError) as error:
            return self._failed(budget, str(error))

        output = self._build_output(
            symbol=symbol,
            price_trend=price_trend,
            volume_trend=volume_trend,
            market_trend=market_trend,
            total_return=total_return,
            average_volume=average_volume,
            volatility=volatility,
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
                str(symbol).upper()
                for symbol in self.task_requirement.symbols
            ]

            if available_symbols is None:
                return requested[0]

            available_map = {
                str(symbol).upper(): str(symbol)
                for symbol in available_symbols
            }

            for symbol in requested:
                if symbol in available_map:
                    return available_map[symbol]

        return self._find_symbol_in_query(
            query,
            available_symbols,
        )

    @staticmethod
    def _find_symbol_in_query(
        query: str,
        available_symbols=None,
    ) -> str | None:
        if available_symbols is None:
            available_symbols = [
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
            ]

        import re

        query_upper = query.upper()

        for symbol in available_symbols:
            normalized = str(symbol).upper()

            if re.search(
                rf"\b{re.escape(normalized)}\b",
                query_upper,
            ):
                return normalized

        return None

    @staticmethod
    def _build_output(
        symbol: str,
        price_trend: str,
        volume_trend: str,
        market_trend: str,
        total_return: float,
        average_volume: float,
        volatility: float,
    ) -> str:
        return (
            f"Market Research Assessment for {symbol}\n\n"
            f"Overall Market Trend: {market_trend}\n\n"
            f"Price Trend: {price_trend}\n"
            f"Volume Trend: {volume_trend}\n\n"
            "Historical Performance:\n"
            f"Total return: {total_return * 100:.2f}%\n\n"
            "Trading Activity:\n"
            f"Average daily volume: {average_volume:,.0f}\n\n"
            "Risk Indicator:\n"
            f"Historical volatility: {volatility * 100:.2f}%\n\n"
            f"The historical price and volume data indicate a "
            f"{market_trend.lower()} for {symbol}.\n\n"
            "This assessment is based on historical data and does not "
            "guarantee future market performance."
        )