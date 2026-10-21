
import math
import re

import numpy as np
import pandas as pd

from app.agents.base_agent import BaseAgent
from app.calculations.risk_classifier import classify_risk
from app.calculations.risk_metrics import (
    calculate_max_drawdown,
    calculate_returns,
    calculate_sharpe_ratio,
    calculate_volatility,
)
from app.data.fallback_provider import (
    create_default_data_provider,
)
from app.models.schemas import AgentState, AgentStatus


class RiskAgent(BaseAgent):
    """Assess historical market risk using closing-price data."""

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
            name="Risk Agent",
            reliability=0.91,
            estimated_cost=900,
        )

        # Configure a default provider only when one was not injected.
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
        required_budget = 400

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
                    "Market data is unavailable; configure a data "
                    "provider or supply market_data.",
                )

            if not self.local_file_path:
                return self._failed(
                    budget,
                    "Local data file path was not supplied.",
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

        # This message is retained for compatibility with the
        # existing test for a requested symbol missing from data.
        if data.empty:
            return self._failed(
                budget,
                "No supported symbol found in query.",
            )

        if data["date"].duplicated().any():
            return self._failed(
                budget,
                f"Duplicate dates found for {symbol}.",
            )

        prices = data["close"].astype(float)

        if not np.isfinite(prices.to_numpy()).all():
            return self._failed(
                budget,
                "Closing prices must be finite numbers.",
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
                "for risk analysis.",
            )

        try:
            returns = calculate_returns(prices)
            volatility = calculate_volatility(returns)
            max_drawdown = calculate_max_drawdown(prices)
            sharpe_ratio = calculate_sharpe_ratio(returns)

            metrics = [
                volatility,
                max_drawdown,
                sharpe_ratio,
            ]

            if not all(
                math.isfinite(float(value))
                for value in metrics
            ):
                raise ValueError(
                    "Risk calculations produced non-finite values."
                )

        except (ValueError, ZeroDivisionError) as error:
            return self._failed(budget, str(error))

        risk_level = classify_risk(
            volatility=volatility,
            max_drawdown=max_drawdown,
        )

        if risk_level == "Low":
            interpretation = (
                "The stock showed relatively small price "
                "fluctuations and limited declines during "
                "the analyzed period."
            )
        elif risk_level == "Moderate":
            interpretation = (
                "The stock showed noticeable price fluctuations "
                "or declines during the analyzed period."
            )
        else:
            interpretation = (
                "The stock showed large price fluctuations or "
                "significant declines during the analyzed period."
            )

        context = self._build_context()

        output = (
            f"Risk Assessment for {symbol}\n\n"
            f"Risk Level: {risk_level}\n\n"
            f"Explanation: {interpretation}\n\n"
            f"Annualized volatility estimate: "
            f"{volatility * 100:.2f}%\n"
            f"Maximum historical drawdown: "
            f"{max_drawdown * 100:.2f}%\n"
            f"Sharpe ratio: {sharpe_ratio:.4f}\n"
            f"Closing-price observations: {len(prices)}"
            f"{context}\n\n"
            "Important: This is a historical risk assessment, "
            "not a forecast. Short histories may produce "
            "unstable estimates."
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

        return self._extract_symbol_from_query(query)

    def _build_context(self) -> str:
        if self.task_requirement is None:
            return ""

        parts = []

        if self.task_requirement.risk_preference:
            parts.append(
                "User risk preference: "
                f"{self.task_requirement.risk_preference}"
            )

        if self.task_requirement.years is not None:
            parts.append(
                "Investment horizon: "
                f"{self.task_requirement.years} years"
            )

        if not parts:
            return ""

        return "\n\nUser Context:\n" + "\n".join(parts)

    @staticmethod
    def _extract_symbol_from_query(
        query: str,
    ) -> str | None:
        query_upper = query.upper()

        for symbol in RiskAgent.SUPPORTED_SYMBOLS:
            if re.search(
                rf"\b{re.escape(symbol)}\b",
                query_upper,
            ):
                return symbol

        return None
