import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import ValidationError

from app.models.schemas import TaskRequirement


load_dotenv()


class GeminiQueryAnalyzer:
    """LLM-based financial query analyzer using Gemini."""

    MODEL_NAME = "gemini-3.6-flash"

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

    VALID_RISK_LEVELS = {
        "low",
        "moderate",
        "medium",
        "high",
    }

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(api_key=api_key)

    def _build_system_prompt(self) -> str:
        capabilities = ", ".join(
            sorted(self.ALLOWED_CAPABILITIES)
        )

        return f"""
You are a financial query analysis component.

Your ONLY responsibility is to convert the user's natural-language
financial query into structured information.

You must NOT:
- perform financial calculations
- provide investment advice
- make financial recommendations
- invent financial data
- answer the user's financial question

You only identify what information and capabilities are required
to process the query.

Allowed capabilities:
{capabilities}

Rules for capabilities:

1. investment_analysis
Use when the user asks about investment potential, whether to invest,
investment opportunities, or evaluating an investment.

2. risk_analysis
Use only when the user explicitly asks to analyze risk, volatility,
risk level, risk exposure, or risk assessment.

A stated risk preference such as "low risk" or "moderate risk"
does NOT automatically require risk_analysis.

3. portfolio_management
Use when the user asks to construct, build, manage, diversify,
or evaluate a portfolio.

4. market_research
Use for market conditions, market trends, industry trends,
or broader market analysis.

5. fundamental_analysis
Use for company fundamentals such as revenue, earnings,
profitability, valuation, EPS, or financial health.

6. technical_analysis
Use for technical indicators such as RSI, moving averages,
MACD, support, resistance, momentum, or technical analysis.

7. sentiment_analysis
Use for investor sentiment, news sentiment, market sentiment,
or sentiment analysis.

8. financial_planning
Use for financial goals, target amounts, investment horizons,
retirement planning, or calculating/planning toward a financial goal.

Important:
- Select ONLY capabilities explicitly required by the query.
- Do NOT add capabilities merely because they could be useful.
- Extra unnecessary capabilities are incorrect.
- A risk preference is separate from risk_analysis.

Risk preference:
Extract only if explicitly stated.
Normalize:
"medium" -> "moderate"
Valid values:
low, moderate, high

Amounts:
Convert Indian monetary expressions into numeric INR values.

Examples:
₹20 lakh -> 2000000
20 lakh -> 2000000
₹5 crore -> 50000000
5 crore -> 50000000

Years:
Extract the number of years when explicitly stated.

Symbols:
Extract ONLY actual financial ticker symbols explicitly mentioned.
Examples:
TCS -> TCS
INFY -> INFY

Never put ordinary words, risk levels, amounts, or years into symbols.

If a field is not explicitly available, return null or an empty list
as appropriate.

Return information that follows the provided schema exactly.
"""

    def analyze(self, query: str) -> TaskRequirement:

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        try:
            response = self.client.models.generate_content(
                model=self.MODEL_NAME,
                contents=[
                    self._build_system_prompt(),
                    query,
                ],
                config=types.GenerateContentConfig(
                    temperature=0,
                    response_mime_type="application/json",
                    response_schema=TaskRequirement,
                ),
            )

            requirement = TaskRequirement.model_validate_json(
                response.text
            )

            # Always preserve the exact original query.
            requirement.query = query

            # Keep only capabilities defined by our system.
            requirement.required_capabilities = [
                capability
                for capability in requirement.required_capabilities
                if capability in self.ALLOWED_CAPABILITIES
            ]

            # Remove duplicate capabilities while preserving order.
            requirement.required_capabilities = list(
                dict.fromkeys(
                    requirement.required_capabilities
                )
            )

            # Normalize risk preference.
            if requirement.risk_preference:
                risk = requirement.risk_preference.strip().lower()

                if risk == "medium":
                    risk = "moderate"

                if risk in {"low", "moderate", "high"}:
                    requirement.risk_preference = risk
                else:
                    requirement.risk_preference = None

            # Normalize and validate symbols.
            cleaned_symbols = []

            for symbol in requirement.symbols:
                if not symbol:
                    continue

                normalized = symbol.strip().upper()

                # Prevent risk levels from becoming symbols.
                if normalized.lower() in self.VALID_RISK_LEVELS:
                    continue

                if normalized not in cleaned_symbols:
                    cleaned_symbols.append(normalized)

            requirement.symbols = cleaned_symbols

            return requirement

        except ValidationError as exc:
            raise RuntimeError(
                "Gemini returned data that does not match "
                "TaskRequirement."
            ) from exc

        except Exception as exc:
            raise RuntimeError(
                f"Gemini query analysis failed: {exc}"
            ) from exc