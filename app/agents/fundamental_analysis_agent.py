import numpy as np
import pandas as pd

from app.agents.base_agent import BaseAgent
from app.calculations.fundamental_metrics import (
    calculate_eps_growth,
    calculate_fundamental_score,
    calculate_price_to_earnings,
    calculate_profit_margin,
    calculate_revenue_growth,
    classify_fundamental_strength,
)
from app.models.schemas import AgentState, AgentStatus


class FundamentalAnalysisAgent(BaseAgent):
    """Analyze financial-statement metrics for a company."""

    REQUIRED_COLUMNS = {
        "symbol",
        "period",
        "revenue",
        "net_income",
        "eps",
        "price",
    }

    def __init__(self) -> None:
        super().__init__(
            name="Fundamental Analysis Agent",
            reliability=0.91,
            estimated_cost=750,
        )

    def execute(
        self,
        query: str,
        budget: int,
        fundamental_data: pd.DataFrame | None = None,
    ) -> AgentState:
        required_budget = 550

        if budget < required_budget:
            return self._failed(budget, "Insufficient budget.")

        if fundamental_data is None:
            return self._failed(
                budget,
                "Fundamental data is unavailable. Supply financial-statement "
                "data containing symbol, period, revenue, net_income, eps "
                "and price.",
            )

        if fundamental_data.empty:
            return self._failed(budget, "Fundamental data is empty.")

        missing = self.REQUIRED_COLUMNS.difference(
            fundamental_data.columns
        )

        if missing:
            return self._failed(
                budget,
                f"Fundamental data is missing required columns: {sorted(missing)}",
            )

        symbol = self._get_preferred_symbol(
            query=query,
            available_symbols=fundamental_data["symbol"].unique(),
        )

        if symbol is None:
            return self._failed(
                budget,
                "No supported symbol found in query.",
            )

        data = fundamental_data.copy()
        data["symbol"] = data["symbol"].astype(str).str.upper()

        symbol_data = data.loc[
            data["symbol"] == symbol.upper()
        ].copy()

        if symbol_data.empty:
            return self._failed(
                budget,
                f"No fundamental data found for {symbol}.",
            )

        symbol_data["period"] = pd.to_datetime(
            symbol_data["period"],
            errors="coerce",
        )

        if symbol_data["period"].isna().any():
            return self._failed(
                budget,
                "Fundamental data contains invalid reporting periods.",
            )

        symbol_data = symbol_data.sort_values("period")

        for column in ("revenue", "net_income", "eps", "price"):
            symbol_data[column] = pd.to_numeric(
                symbol_data[column],
                errors="coerce",
            )

        numeric_data = symbol_data[
            ["revenue", "net_income", "eps", "price"]
        ]

        if numeric_data.isna().any().any():
            return self._failed(
                budget,
                "Fundamental data contains missing or non-numeric values.",
            )

        if not np.isfinite(
            numeric_data.to_numpy(dtype=float)
        ).all():
            return self._failed(
                budget,
                "Fundamental data contains non-finite values.",
            )

        if (symbol_data["revenue"] <= 0).any():
            return self._failed(
                budget,
                "Revenue values must be greater than zero.",
            )

        if (symbol_data["price"] <= 0).any():
            return self._failed(
                budget,
                "Share prices must be greater than zero.",
            )

        if symbol_data["period"].duplicated().any():
            return self._failed(
                budget,
                "Duplicate reporting periods found for the selected symbol.",
            )

        revenue = symbol_data["revenue"]
        net_income = symbol_data["net_income"]
        eps = symbol_data["eps"]
        latest_price = float(symbol_data["price"].iloc[-1])

        try:
            revenue_growth = calculate_revenue_growth(revenue)
            profit_margin = calculate_profit_margin(
                revenue,
                net_income,
            )
            eps_growth = calculate_eps_growth(eps)
            pe_ratio = calculate_price_to_earnings(
                latest_price,
                float(eps.iloc[-1]),
            )

            fundamental_score = calculate_fundamental_score(
                revenue_growth=revenue_growth,
                profit_margin=profit_margin,
                eps_growth=eps_growth,
                pe_ratio=pe_ratio,
            )

            fundamental_strength = classify_fundamental_strength(
                fundamental_score
            )

        except (ValueError, ZeroDivisionError) as error:
            return self._failed(budget, str(error))

        output = self._build_output(
            symbol=symbol,
            revenue_growth=revenue_growth,
            profit_margin=profit_margin,
            eps_growth=eps_growth,
            pe_ratio=pe_ratio,
            fundamental_score=fundamental_score,
            fundamental_strength=fundamental_strength,
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
        revenue_growth: float,
        profit_margin: float,
        eps_growth: float,
        pe_ratio: float,
        fundamental_score: float,
        fundamental_strength: str,
    ) -> str:
        return (
            f"Fundamental Analysis Assessment for {symbol}\n\n"
            f"Overall Assessment: {fundamental_strength}\n\n"
            "Growth Indicators:\n"
            f"Revenue growth: {revenue_growth * 100:.2f}%\n"
            f"EPS growth: {eps_growth * 100:.2f}%\n\n"
            "Profitability:\n"
            f"Net profit margin: {profit_margin * 100:.2f}%\n\n"
            "Valuation:\n"
            f"Price-to-earnings ratio: {pe_ratio:.2f}\n\n"
            f"Fundamental Score: {fundamental_score:.2f}\n\n"
            f"The available financial data indicates {fundamental_strength.lower()} "
            f"for {symbol}, based on revenue growth, profitability, EPS growth "
            "and valuation.\n\n"
            "This assessment uses historical financial data and does not "
            "guarantee future company performance."
        )