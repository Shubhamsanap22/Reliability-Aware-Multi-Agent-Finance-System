from app.models.schemas import TaskRequirement


class RuleBasedQueryAnalyzer:
    """Analyzes a financial query and identifies all required capabilities."""

    def analyze(self, query: str) -> TaskRequirement:
        """
        Analyze the query and return all capabilities required
        to complete the task.
        """

        query_lower = query.lower()

        required_capabilities = []

        # ---------------------------------------------------------
        # 1. Portfolio Management
        # ---------------------------------------------------------
        if (
            "portfolio" in query_lower
            or "diversified portfolio" in query_lower
            or "build a portfolio" in query_lower
            or "construct a portfolio" in query_lower
        ):
            required_capabilities.append(
                "portfolio_management"
            )

        # ---------------------------------------------------------
        # 2. Investment Analysis
        # ---------------------------------------------------------
        if (
            "invest" in query_lower
            or "investment" in query_lower
            or "investment potential" in query_lower
            or "investment opportunity" in query_lower
            or "buy" in query_lower
            or "should i invest" in query_lower
        ):
            required_capabilities.append(
                "investment_analysis"
            )

        # ---------------------------------------------------------
        # 3. Risk Analysis
        # ---------------------------------------------------------
        if (
            "risk" in query_lower
            or "risky" in query_lower
            or "volatility" in query_lower
            or "risk level" in query_lower
            or "risk profile" in query_lower
        ):
            required_capabilities.append(
                "risk_analysis"
            )

        # ---------------------------------------------------------
        # 4. Market Research
        # ---------------------------------------------------------
        if (
            "market" in query_lower
            or "market condition" in query_lower
            or "market conditions" in query_lower
            or "market trend" in query_lower
            or "market trends" in query_lower
            or "trend" in query_lower
            or "industry" in query_lower
        ):
            required_capabilities.append(
                "market_research"
            )

        # ---------------------------------------------------------
        # 5. Fundamental Analysis
        # ---------------------------------------------------------
        if (
            "fundamental" in query_lower
            or "fundamentals" in query_lower
            or "financial strength" in query_lower
            or "financial health" in query_lower
            or "financial performance" in query_lower
            or "valuation" in query_lower
            or "profitability" in query_lower
            or "revenue" in query_lower
            or "earnings" in query_lower
        ):
            required_capabilities.append(
                "fundamental_analysis"
            )

        # ---------------------------------------------------------
        # 6. Technical Analysis
        # ---------------------------------------------------------
        if (
            "technical" in query_lower
            or "technical analysis" in query_lower
            or "price trend" in query_lower
            or "moving average" in query_lower
            or "rsi" in query_lower
            or "macd" in query_lower
            or "support" in query_lower
            or "resistance" in query_lower
        ):
            required_capabilities.append(
                "technical_analysis"
            )

        # ---------------------------------------------------------
        # 7. Sentiment Analysis
        # ---------------------------------------------------------
        if (
            "sentiment" in query_lower
            or "market sentiment" in query_lower
            or "investor sentiment" in query_lower
            or "news sentiment" in query_lower
            or "positive sentiment" in query_lower
            or "negative sentiment" in query_lower
        ):
            required_capabilities.append(
                "sentiment_analysis"
            )

        # ---------------------------------------------------------
        # 8. Financial Planning
        # ---------------------------------------------------------
        if (
            "financial plan" in query_lower
            or "financial planning" in query_lower
            or "investment plan" in query_lower
            or "plan my investment" in query_lower
            or "target amount" in query_lower
            or "financial goal" in query_lower
            or "retirement plan" in query_lower
            or "retirement planning" in query_lower
            or "years" in query_lower
            and (
                "lakh" in query_lower
                or "crore" in query_lower
                or "goal" in query_lower
            )
        ):
            required_capabilities.append(
                "financial_planning"
            )

        # ---------------------------------------------------------
        # Portfolio queries also require investment analysis
        # ---------------------------------------------------------
        if (
            "portfolio_management" in required_capabilities
            and "investment_analysis" not in required_capabilities
        ):
            required_capabilities.append(
                "investment_analysis"
            )

        # ---------------------------------------------------------
        # Default capability
        # ---------------------------------------------------------
        if not required_capabilities:
            required_capabilities.append(
                "financial_analysis"
            )

        return TaskRequirement(
            query=query,
            required_capabilities=required_capabilities,
        )

# Backward compatibility for existing tests and code
QueryAnalyzer = RuleBasedQueryAnalyzer