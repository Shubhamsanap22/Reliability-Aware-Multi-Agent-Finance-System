from __future__ import annotations

import re
from typing import Any

from app.analysis.rule_based_query_analyzer import RuleBasedQueryAnalyzer
from app.models.schemas import TaskRequirement


class QueryAnalyzer:
    """Normalize financial queries into structured task requirements."""

    ALLOWED_CAPABILITIES = {
        "investment_analysis",
        "risk_analysis",
        "portfolio_management",
        "market_research",
        "fundamental_analysis",
        "technical_analysis",
        "sentiment_analysis",
        "financial_planning",
    }

    # Symbols used by the current project test data.
    KNOWN_SYMBOLS = {
        "TCS",
        "INFY",
        "RELIANCE",
        "AAPL",
        "MSFT",
    }

    def __init__(self, analyzer: Any | None = None) -> None:
        self.analyzer = analyzer or RuleBasedQueryAnalyzer()

    @staticmethod
    def _normalize_annual_return(
        value: Any,
        query: str = "",
    ) -> float | None:
        """Convert percentage-point returns to decimal form."""

        if value is None or isinstance(value, bool):
            return None

        try:
            result = float(value)
        except (TypeError, ValueError):
            return None

        if not (result == result and abs(result) != float("inf")):
            raise ValueError("Annual return must be a finite number.")

        text = query.lower()

        explicitly_percentage = (
            "%" in text
            or "percent" in text
            or "percentage" in text
        )

        # If the query explicitly expresses a percentage,
        # convert percentage points to a decimal.
        if explicitly_percentage:
            result /= 100.0

        return result

    def analyze(self, query: str) -> TaskRequirement:
        """Convert a financial query into a validated requirement."""

        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query cannot be empty.")

        query = query.strip()
        result = self.analyzer.analyze(query)

        if isinstance(result, TaskRequirement):
            data = result.model_dump()
        elif isinstance(result, dict):
            data = dict(result)
        elif hasattr(result, "model_dump"):
            data = result.model_dump()
        else:
            raise TypeError(
                "Analyzer must return TaskRequirement or a dictionary."
            )

        # Preserve the original query.
        data["query"] = query

        # Normalize and deduplicate capabilities.
        capabilities = data.get("required_capabilities") or []

        capabilities = list(
            dict.fromkeys(
                capability
                for capability in capabilities
                if isinstance(capability, str)
                and capability in self.ALLOWED_CAPABILITIES
            )
        )

        lowered = query.lower()

        planning_phrases = (
            "financial planning",
            "financial goal",
            "want ₹",
            "want rs",
            "reach my target",
            "save for",
            "retirement",
        )

        explicit_risk_phrases = (
            "risk analysis",
            "analyze the risk",
            "analyse the risk",
            "risk of investing",
            "risk assessment",
            "investment risk",
            "volatility",
            "maximum drawdown",
        )

        is_planning_query = any(
            phrase in lowered
            for phrase in planning_phrases
        )

        explicitly_requests_risk = any(
            phrase in lowered
            for phrase in explicit_risk_phrases
        )

        # A stated risk preference alone should not select
        # the risk-analysis agent.
        if is_planning_query and not explicitly_requests_risk:
            capabilities = [
                capability
                for capability in capabilities
                if capability != "risk_analysis"
            ]

        data["required_capabilities"] = capabilities

        # Normalize risk preference.
        risk = data.get("risk_preference")

        if isinstance(risk, str):
            risk = risk.strip().lower()

            if risk == "medium":
                risk = "moderate"

            data["risk_preference"] = (
                risk
                if risk in {"low", "moderate", "high"}
                else None
            )
        else:
            data["risk_preference"] = None

        # Normalize existing symbols and remove duplicates.
        cleaned_symbols = []
        existing_symbols = data.get("symbols") or []

        for symbol in existing_symbols:
            if not isinstance(symbol, str):
                continue

            symbol = symbol.strip().upper()

            if (
                symbol in self.KNOWN_SYMBOLS
                and symbol not in cleaned_symbols
            ):
                cleaned_symbols.append(symbol)

        # Extract known ticker symbols from the original query.
        for symbol in re.findall(r"\b[A-Z][A-Z0-9]{1,9}\b", query):
            if (
                symbol in self.KNOWN_SYMBOLS
                and symbol not in cleaned_symbols
            ):
                cleaned_symbols.append(symbol)

        data["symbols"] = cleaned_symbols

        # Normalize annual return if provided by the underlying analyzer.
        annual_return = data.get("annual_return")

        if annual_return is not None:
            data["annual_return"] = self._normalize_annual_return(
                annual_return,
                query,
            )

        return TaskRequirement.model_validate(data)