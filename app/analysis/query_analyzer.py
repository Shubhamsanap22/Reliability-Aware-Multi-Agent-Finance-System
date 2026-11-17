import re
from typing import Any

from app.analysis.rule_based_query_analyzer import (
    QueryAnalyzer as RuleBasedQueryAnalyzer,
)
from app.models.schemas import TaskRequirement


class QueryAnalyzer:
    """Analyze financial queries and extract task requirements."""

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

    CAPABILITY_ORDER = (
        "portfolio_management",
        "investment_analysis",
        "risk_analysis",
        "market_research",
        "fundamental_analysis",
        "technical_analysis",
        "sentiment_analysis",
        "financial_planning",
    )

    RISK_LEVELS = {"low", "moderate", "high"}

    KNOWN_SYMBOLS = {"TCS", "INFY", "RELIANCE", "AAPL", "MSFT"}

    PLANNING_KEYWORDS = (
        "investment plan",
        "financial plan",
        "financial planning",
        "investment planning",
        "plan my investment",
        "plan an investment",
        "reach my target",
        "reach a target",
        "target amount",
        "future value",
        "retirement plan",
        "save for",
        "saving for",
        "i want",
        "i need",
        "accumulate",
        "grow my money",
    )

    RISK_ANALYSIS_PHRASES = (
        "analyse the risk",
        "analyze the risk",
        "risk analysis",
        "assess the risk",
        "evaluate the risk",
        "risk assessment",
        "risk exposure",
        "risk profile of",
        "risk associated with",
        "downside risk",
        "value at risk",
        "maximum drawdown",
    )

    PORTFOLIO_KEYWORDS = (
        "build a portfolio",
        "build portfolio",
        "create a portfolio",
        "create portfolio",
        "construct a portfolio",
        "construct portfolio",
        "manage my portfolio",
        "manage the portfolio",
        "portfolio allocation",
        "portfolio rebalancing",
        "rebalance my portfolio",
        "optimize my portfolio",
        "optimise my portfolio",
    )

    def __init__(self) -> None:
        self.rule_analyzer = RuleBasedQueryAnalyzer()

    def analyze(self, query: str) -> TaskRequirement:
        """Analyze a query and return validated requirements."""
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")

        query = query.strip()

        base_result = self.rule_analyzer.analyze(query)

        if isinstance(base_result, dict):
            data = dict(base_result)
        elif hasattr(base_result, "model_dump"):
            data = base_result.model_dump()
        elif hasattr(base_result, "dict"):
            data = base_result.dict()
        else:
            data = {}

        data["query"] = query

        capabilities = self._normalize_capabilities(
            data.get("required_capabilities", [])
        )

        if self._is_portfolio_query(query):
            capabilities.update(
                {"portfolio_management", "investment_analysis"}
            )

        if self._is_planning_query(query):
            capabilities.add("financial_planning")

        # A stated risk preference is not, by itself, a request for
        # a separate risk-analysis capability.
        if self._explicitly_requests_risk(query):
            capabilities.add("risk_analysis")
        else:
            capabilities.discard("risk_analysis")

        data["required_capabilities"] = [
            capability
            for capability in self.CAPABILITY_ORDER
            if capability in capabilities
        ]

        risk_preference = self._extract_risk_preference(query)
        if risk_preference is not None:
            data["risk_preference"] = risk_preference

        planning_details = self._extract_planning_details(query)

        for field in ("initial_amount", "target_amount", "years"):
            value = planning_details.get(field)
            if value is not None:
                data[field] = value

        annual_return = data.get("annual_return")
        if annual_return is None:
            annual_return = self._extract_annual_return(query)

        data["annual_return"] = self._normalize_annual_return(
            annual_return,
            query,
        )

        symbols = self._extract_symbols(query)

        if symbols:
            data["symbols"] = symbols
        else:
            existing_symbols = data.get("symbols")

            if existing_symbols is None:
                data["symbols"] = []
            elif isinstance(existing_symbols, str):
                data["symbols"] = [existing_symbols.upper()]
            elif isinstance(existing_symbols, (list, tuple, set)):
                data["symbols"] = [
                    str(symbol).upper() for symbol in existing_symbols
                ]

        return TaskRequirement.model_validate(data)

    @classmethod
    def _normalize_capabilities(
        cls,
        capabilities: Any,
    ) -> set[str]:
        """Normalize and filter supported capability names."""
        if capabilities is None:
            return set()

        if isinstance(capabilities, str):
            capabilities = [capabilities]

        if not isinstance(capabilities, (list, tuple, set)):
            return set()

        normalized = set()

        for capability in capabilities:
            if not isinstance(capability, str):
                continue

            name = (
                capability.strip()
                .lower()
                .replace("-", "_")
                .replace(" ", "_")
            )

            if name in cls.ALLOWED_CAPABILITIES:
                normalized.add(name)

        return normalized

    @classmethod
    def _is_portfolio_query(cls, query: str) -> bool:
        """Detect explicit portfolio-management requests."""
        normalized_query = query.lower()
        return any(
            keyword in normalized_query
            for keyword in cls.PORTFOLIO_KEYWORDS
        )

    @classmethod
    def _explicitly_requests_risk(cls, query: str) -> bool:
        """Detect explicit requests for risk analysis."""
        normalized_query = query.lower()
        return any(
            phrase in normalized_query
            for phrase in cls.RISK_ANALYSIS_PHRASES
        )

    @classmethod
    def _is_planning_query(cls, query: str) -> bool:
        """Detect financial-planning requests."""
        normalized_query = query.lower()

        if any(
            keyword in normalized_query
            for keyword in cls.PLANNING_KEYWORDS
        ):
            return True

        has_goal = bool(
            re.search(
                r"\b(?:target|reach|accumulate|save|need|want)\b",
                normalized_query,
            )
        )

        has_horizon = bool(
            re.search(
                r"\b\d+(?:\.\d+)?\s*"
                r"(?:years?|yrs?|months?|mos?)\b",
                normalized_query,
            )
        )

        return has_goal and has_horizon

    @classmethod
    def _extract_risk_preference(
        cls,
        query: str,
    ) -> str | None:
        """Extract low, moderate, or high risk preference."""
        normalized_query = query.lower()

        patterns = (
            (
                r"\b(?:low|conservative|risk[- ]averse)\s+risk\b",
                "low",
            ),
            (
                r"\b(?:moderate|medium|balanced)\s+risk\b",
                "moderate",
            ),
            (
                r"\b(?:high|aggressive)\s+risk\b",
                "high",
            ),
        )

        for pattern, level in patterns:
            if re.search(pattern, normalized_query):
                return level

        for level in cls.RISK_LEVELS:
            if re.search(
                rf"\b{level}\b.{{0,30}}\b"
                rf"(?:risk tolerance|risk appetite|risk profile)\b",
                normalized_query,
            ):
                return level

            if re.search(
                rf"\b(?:risk tolerance|risk appetite|risk profile)"
                rf".{{0,30}}\b{level}\b",
                normalized_query,
            ):
                return level

        return None

    @staticmethod
    def _to_amount(
        value: str | int | float | None,
    ) -> float | None:
        """Convert a monetary amount to rupees."""
        if value is None:
            return None

        if isinstance(value, (int, float)):
            return float(value)

        normalized = str(value).strip().lower()
        normalized = normalized.replace(",", "")
        normalized = normalized.replace("₹", "")
        normalized = normalized.replace("inr", "")
        normalized = normalized.replace("rs.", "")
        normalized = normalized.replace("rs", "").strip()

        match = re.fullmatch(
            r"(\d+(?:\.\d+)?)\s*"
            r"(crores?|cr|lakhs?|lacs?|thousands?|k|l)?",
            normalized,
        )

        if not match:
            try:
                return float(normalized)
            except (TypeError, ValueError):
                return None

        amount = float(match.group(1))
        unit = (match.group(2) or "").lower()

        if unit in {"crore", "crores", "cr"}:
            amount *= 10_000_000
        elif unit in {"lakh", "lakhs", "lac", "lacs", "l"}:
            amount *= 100_000
        elif unit in {"thousand", "thousands", "k"}:
            amount *= 1_000

        return amount

    @classmethod
    def _extract_amount_matches(
        cls,
        query: str,
    ) -> list[dict[str, Any]]:
        """Extract monetary amounts and their character positions."""
        matches: list[dict[str, Any]] = []

        unit_pattern = re.compile(
            r"(?:(?:₹|rs\.?\s*|inr\s*)\s*)?"
            r"(\d+(?:,\d{3})*(?:\.\d+)?)\s*"
            r"(crores?|cr|lakhs?|lacs?|thousands?|k|l)\b",
            re.IGNORECASE,
        )

        for match in unit_pattern.finditer(query):
            amount = cls._to_amount(
                f"{match.group(1)} {match.group(2)}"
            )

            if amount is not None:
                matches.append(
                    {
                        "start": match.start(),
                        "end": match.end(),
                        "amount": amount,
                        "text": match.group(0),
                    }
                )

        plain_pattern = re.compile(
            r"(?:₹|rs\.?\s*|inr\s*)"
            r"(\d+(?:,\d{3})*(?:\.\d+)?)"
            r"|\b(\d+(?:,\d{3})*(?:\.\d+)?)\s*"
            r"(?:inr|rupees?)\b",
            re.IGNORECASE,
        )

        for match in plain_pattern.finditer(query):
            raw_number = match.group(1) or match.group(2)
            amount = cls._to_amount(raw_number)

            if amount is None:
                continue

            overlaps = any(
                match.start() < item["end"]
                and match.end() > item["start"]
                for item in matches
            )

            if not overlaps:
                matches.append(
                    {
                        "start": match.start(),
                        "end": match.end(),
                        "amount": amount,
                        "text": match.group(0),
                    }
                )

        return sorted(matches, key=lambda item: item["start"])

    @classmethod
    def _extract_planning_details(
        cls,
        query: str,
    ) -> dict[str, Any]:
        """Extract initial amount, target amount, and planning horizon."""
        result: dict[str, Any] = {
            "initial_amount": None,
            "target_amount": None,
            "years": None,
        }

        normalized_query = query.lower()
        amounts = cls._extract_amount_matches(query)

        # Extract planning horizon.
        horizon_match = re.search(
            r"\b(\d+(?:\.\d+)?)\s*"
            r"(years?|yrs?|months?|mos?)\b",
            normalized_query,
        )

        if horizon_match:
            duration = float(horizon_match.group(1))
            unit = horizon_match.group(2)

            result["years"] = (
                duration / 12.0
                if unit.startswith(("month", "mo"))
                else duration
            )

        # Identify amount labels on either side of each amount.
        for amount in amounts:
            start = amount["start"]
            end = amount["end"]

            before = normalized_query[max(0, start - 100):start]
            after = normalized_query[end:min(len(query), end + 100)]

            initial_before = bool(
                re.search(
                    r"\b(?:initial|starting|start|principal|existing|current)"
                    r"(?:\s+\w+){0,2}\s*$",
                    before,
                )
            )
            initial_after = bool(
                re.match(
                    r"\s*(?:initial|starting|start|principal|existing|current)"
                    r"\b",
                    after,
                )
            )

            target_before = bool(
                re.search(
                    r"\b(?:target|goal|desired)\s*$",
                    before,
                )
            )
            target_after = bool(
                re.match(
                    r"\s*(?:target|goal|desired)\b",
                    after,
                )
            )

            if initial_before or initial_after:
                result["initial_amount"] = amount["amount"]

            if target_before or target_after:
                result["target_amount"] = amount["amount"]

        # Find amounts following explicit goal-directed verbs such as
        # "reach 20 lakh" or "achieve 20 lakh".
        if result["target_amount"] is None:
            for amount in amounts:
                prefix = normalized_query[:amount["start"]]

                if re.search(
                    r"\b(?:reach|achieve|accumulate)\s*$",
                    prefix,
                ):
                    result["target_amount"] = amount["amount"]
                    break

        # Identify the starting amount when its label follows the amount.
        if result["initial_amount"] is None:
            for amount in amounts:
                suffix = normalized_query[
                    amount["end"]:amount["end"] + 50
                ]

                if re.match(
                    r"\s*(?:initial|starting|start|principal)\s+"
                    r"(?:amount|investment|capital)\b",
                    suffix,
                ):
                    result["initial_amount"] = amount["amount"]
                    break

        # Fallback for two amounts without explicit role labels.
        # Never replace a role that has already been identified.
        if len(amounts) >= 2:
            if (
                result["initial_amount"] is None
                and result["target_amount"] is None
            ):
                result["initial_amount"] = amounts[0]["amount"]
                result["target_amount"] = amounts[-1]["amount"]

            elif result["initial_amount"] is None:
                for amount in amounts:
                    if amount["amount"] != result["target_amount"]:
                        result["initial_amount"] = amount["amount"]
                        break

            elif result["target_amount"] is None:
                for amount in reversed(amounts):
                    if amount["amount"] != result["initial_amount"]:
                        result["target_amount"] = amount["amount"]
                        break

        elif len(amounts) == 1 and cls._is_planning_query(query):
            if result["target_amount"] is None:
                result["target_amount"] = amounts[0]["amount"]

        return result

    @staticmethod
    def _extract_annual_return(query: str) -> float | None:
        """Extract an explicitly stated annual return percentage."""
        normalized_query = query.lower()

        patterns = (
            r"\b(?:annual|yearly)\s+(?:return|rate)\s*"
            r"(?:of|is|=|:)?\s*(\d+(?:\.\d+)?)\s*%",
            r"\b(\d+(?:\.\d+)?)\s*%\s*"
            r"(?:annual|yearly)\s+(?:return|rate)\b",
            r"\bassuming\s+(\d+(?:\.\d+)?)\s*%\s*"
            r"(?:annual|yearly)?\s*(?:return|growth|rate)?",
            r"\bexpected\s+(?:annual\s+)?return\s*"
            r"(?:of|is|=|:)?\s*(\d+(?:\.\d+)?)\s*%",
            r"\b(\d+(?:\.\d+)?)\s*%\s*return\b",
        )

        for pattern in patterns:
            match = re.search(pattern, normalized_query)

            if match:
                try:
                    return float(match.group(1))
                except (TypeError, ValueError):
                    return None

        return None

    @staticmethod
    def _normalize_annual_return(
        value: float | int | None,
        query: str = "",
    ) -> float | None:
        """Normalize annual return percentages to decimal rates."""
        if value is None:
            return None

        try:
            annual_return = float(value)
        except (TypeError, ValueError):
            return None

        if "%" in query:
            return annual_return / 100.0

        if annual_return > 1:
            return annual_return / 100.0

        return annual_return

    @classmethod
    def _extract_symbols(cls, query: str) -> list[str]:
        """Extract recognized stock symbols from the query."""
        words = set(
            re.findall(
                r"\b[A-Za-z][A-Za-z0-9.]{0,14}\b",
                query.upper(),
            )
        )

        return sorted(words.intersection(cls.KNOWN_SYMBOLS))
