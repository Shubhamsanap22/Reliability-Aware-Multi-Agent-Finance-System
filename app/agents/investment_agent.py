
import math
import re

import pandas as pd

from app.agents.base_agent import BaseAgent
from app.calculations.investment_metrics import (
    calculate_annualized_return,
    calculate_average_return,
    calculate_investment_score,
)
from app.calculations.risk_metrics import (
    calculate_returns,
    calculate_sharpe_ratio,
    calculate_volatility,
)
from app.data.fallback_provider import (
    create_default_data_provider,
)
from app.models.schemas import AgentState, AgentStatus


class InvestmentAgent(BaseAgent):
    """Analyze historical investment performance for one asset."""

    SUPPORTED_SYMBOLS = [
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

    def __init__(
        self,
        data_provider=None,
        local_file_path: str | None = None,
    ) -> None:
        super().__init__(
            name="Investment Agent",
            reliability=0.92,
            estimated_cost=900,
        )

        if data_provider is None:
            data_provider, default_path = (
                create_default_data_provider()
            )
            if local_file_path is None:
                local_file_path = default_path

        self.data_provider = data_provider
        self.local_file_path = local_file_path

    def execute(
        self,
        query: str,
        budget: int,
        market_data: pd.DataFrame | None = None,
    ) -> AgentState:
        required_budget = 600

        if budget < required_budget:
            return self._failed(
                budget,
                "Insufficient budget.",
            )

        symbol = self._get_symbol(query)

        if symbol is None:
            return self._failed(
                budget,
                "No supported symbol found in query.",
            )

        if market_data is None:
            if self.data_provider is None:
                return self._failed(
                    budget,
                    "Market data is unavailable. Configure a provider "
                    "or supply market_data.",
                )

            if not self.local_file_path:
                return self._failed(
                    budget,
                    "Local data file path is not configured.",
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

        if market_data is None or market_data.empty:
            return self._failed(
                budget,
                "Market data is empty.",
            )

        required_columns = {"symbol", "date", "close"}
        missing = required_columns.difference(
            market_data.columns
        )

        if missing:
            return self._failed(
                budget,
                "Market data is missing required columns: "
                f"{sorted(missing)}",
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

        data = data.dropna(
            subset=["symbol", "date", "close"]
        )

        data = data[
            data["symbol"] == symbol.upper()
        ].copy()

        data = data.sort_values("date")

        if data.empty:
            return self._failed(
                budget,
                f"No market data available for {symbol}.",
            )

        if data["date"].duplicated().any():
            return self._failed(
                budget,
                f"Duplicate dates found for {symbol}.",
            )

        prices = data["close"].astype(float)

        if not all(
            math.isfinite(float(value))
            for value in prices
        ):
            return self._failed(
                budget,
                "Closing prices contain non-finite values.",
            )

        if (prices <= 0).any():
            return self._failed(
                budget,
                "Closing prices must be greater than zero.",
            )

        if len(prices) < 3:
            return self._failed(
                budget,
                "At least three closing prices are required "
                "for investment analysis.",
            )

        try:
            returns = calculate_returns(prices)

            annualized_return = calculate_annualized_return(
                prices
            )
            average_return = calculate_average_return(
                returns
            )
            volatility = calculate_volatility(returns)
            sharpe_ratio = calculate_sharpe_ratio(returns)

            investment_score = calculate_investment_score(
                annualized_return=annualized_return,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
            )

            total_return = float(
                prices.iloc[-1] / prices.iloc[0] - 1.0
            )

            metrics = [
                annualized_return,
                average_return,
                volatility,
                sharpe_ratio,
                investment_score,
                total_return,
            ]

            if not all(
                math.isfinite(float(value))
                for value in metrics
            ):
                raise ValueError(
                    "Investment calculations produced "
                    "non-finite values."
                )

        except (ValueError, ZeroDivisionError) as error:
            return self._failed(budget, str(error))

        assessment = self._classify_investment(
            investment_score
        )
        context = self._build_context()

        output = (
            f"Investment Assessment for {symbol}\n\n"
            f"Assessment: {assessment}\n\n"
            "Historical Performance:\n"
            f"Total holding-period return: "
            f"{total_return * 100:.2f}%\n"
            f"Annualized return estimate: "
            f"{annualized_return * 100:.2f}%\n"
            f"Average daily return: "
            f"{average_return * 100:.4f}%\n\n"
            "Risk and Performance:\n"
            f"Annualized volatility estimate: "
            f"{volatility * 100:.2f}%\n"
            f"Sharpe ratio: {sharpe_ratio:.4f}\n"
            f"Investment score: {investment_score:.2f}\n"
            f"Observations: {len(prices)} closing prices"
            f"{context}\n\n"
            "Important: This assessment uses historical prices. "
            "Annualization is sensitive to the observation period "
            "and does not predict or guarantee future performance."
        )

        return AgentState(
            agent_name=self.name,
            reliability=self.reliability,
            allocated_budget=budget,
            used_budget=required_budget,
            status=AgentStatus.COMPLETED,
            output=output,
        )

    def _failed(
        self,
        budget: int,
        reason: str,
    ) -> AgentState:
        return AgentState(
            agent_name=self.name,
            reliability=self.reliability,
            allocated_budget=budget,
            used_budget=0,
            status=AgentStatus.FAILED,
            failure_reason=reason,
        )

    def _get_symbol(self, query: str) -> str | None:
        if (
            self.task_requirement is not None
            and self.task_requirement.symbols
        ):
            return str(
                self.task_requirement.symbols[0]
            ).strip().upper()

        return self._find_symbol_in_query(query)

    def _build_context(self) -> str:
        if self.task_requirement is None:
            return ""

        parts = []

        if self.task_requirement.initial_amount is not None:
            parts.append(
                "Requested investment amount: "
                f"₹{self.task_requirement.initial_amount:,.2f}"
            )

        if self.task_requirement.years is not None:
            parts.append(
                "Investment horizon: "
                f"{self.task_requirement.years} years"
            )

        if self.task_requirement.risk_preference:
            parts.append(
                "Risk preference: "
                f"{self.task_requirement.risk_preference}"
            )

        if not parts:
            return ""

        return (
            "\n\nUser Investment Context:\n"
            + "\n".join(parts)
        )

    @staticmethod
    def _find_symbol_in_query(
        query: str,
        available_symbols=None,
    ) -> str | None:
        if available_symbols is None:
            available_symbols = (
                InvestmentAgent.SUPPORTED_SYMBOLS
            )

        query_upper = query.upper()

        for symbol in available_symbols:
            if re.search(
                rf"\b{re.escape(symbol.upper())}\b",
                query_upper,
            ):
                return symbol.upper()

        return None

    @staticmethod
    def _classify_investment(
        investment_score: float,
    ) -> str:
        if investment_score >= 40:
            return "Attractive"

        if investment_score >= 15:
            return "Moderate"

        return "Cautious"
