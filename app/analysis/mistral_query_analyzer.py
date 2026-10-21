import json
import ollama
from pydantic import ValidationError

from app.models.schemas import TaskRequirement


class MistralQueryAnalyzer:
    """LLM-based financial query analyzer using local Mistral."""

    MODEL_NAME = "mistral:latest"

    ALLOWED_CAPABILITIES = [
        "investment_analysis",
        "risk_analysis",
        "portfolio_management",
        "market_research",
        "fundamental_analysis",
        "technical_analysis",
        "sentiment_analysis",
        "financial_planning",
    ]

    ALLOWED_RISK_LEVELS = {
        "low",
        "moderate",
        "medium",
        "high",
    }

    def analyze(self, query: str) -> TaskRequirement:
        """
        Convert a natural-language financial query into
        a validated TaskRequirement object.
        """

        # ---------------------------------------------------------
        # 1. Validate input
        # ---------------------------------------------------------
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        # ---------------------------------------------------------
        # 2. Build the extraction prompt
        # ---------------------------------------------------------
        capabilities = ", ".join(self.ALLOWED_CAPABILITIES)

        system_prompt = f"""
You are a financial query classification and information extraction system.

Your ONLY task is to convert the user's natural-language query into
structured JSON.

You are NOT performing financial calculations.
You are NOT giving investment advice.
You are NOT answering the financial question.

Allowed capabilities:
{capabilities}

IMPORTANT RULES:

1. Select ONLY capabilities explicitly required by the query.

2. Do NOT add extra capabilities merely because they could be useful.

3. If the user states a risk preference such as low, moderate,
   medium, or high, extract it as risk_preference.

4. A stated risk preference does NOT automatically mean
   risk_analysis is required.

5. Select risk_analysis ONLY when the user asks about:
   - risk
   - volatility
   - risk assessment
   - risk level analysis
   - risk of an investment

6. Select investment_analysis when the user asks about:
   - investing
   - whether to invest
   - investment potential
   - investment opportunity
   - evaluating an investment

7. Select portfolio_management when the user asks about:
   - portfolio construction
   - portfolio diversification
   - managing a portfolio
   - building a portfolio

8. Select financial_planning when the query involves:
   - financial goals
   - target amounts
   - investment horizons
   - retirement planning
   - planning how to reach a financial target

9. Select market_research when the query asks about:
   - market conditions
   - market trends
   - industry trends
   - overall market behavior

10. Select fundamental_analysis when the query explicitly asks about:
    - fundamentals
    - financial health
    - revenue
    - earnings
    - profitability
    - valuation
    - financial performance

11. Select technical_analysis when the query explicitly asks about:
    - technical indicators
    - moving averages
    - RSI
    - MACD
    - support
    - resistance
    - technical price analysis

12. Select sentiment_analysis when the query explicitly asks about:
    - sentiment
    - investor sentiment
    - market sentiment
    - news sentiment

13. Extract monetary amounts when explicitly stated.

14. Convert monetary units:
    - 1 lakh = 100000
    - 1 crore = 10000000

15. Examples:
    - ₹20 lakh = 2000000
    - ₹5 lakh = 500000
    - ₹50 lakh = 5000000
    - ₹1 crore = 10000000

16. Extract the investment or financial horizon in years.

17. Extract annual_return ONLY when the user explicitly states
    an expected annual return.

18. Extract actual stock ticker symbols only.

19. Never put:
    - risk levels
    - amounts
    - ordinary English words
    - capability names
    into symbols.

20. Do not invent missing information.

21. Return ONLY valid JSON.

22. Do NOT include the original user query in the JSON.
    The application will add it automatically.

The JSON must contain exactly these fields:

{{
    "required_capabilities": [],
    "risk_preference": null,
    "initial_amount": null,
    "target_amount": null,
    "years": null,
    "annual_return": null,
    "symbols": []
}}

EXAMPLE 1

User:
Should I invest in TCS?

JSON:
{{
    "required_capabilities": ["investment_analysis"],
    "risk_preference": null,
    "initial_amount": null,
    "target_amount": null,
    "years": null,
    "annual_return": null,
    "symbols": ["TCS"]
}}

EXAMPLE 2

User:
What is the risk of investing in INFY?

JSON:
{{
    "required_capabilities": ["risk_analysis"],
    "risk_preference": null,
    "initial_amount": null,
    "target_amount": null,
    "years": null,
    "annual_return": null,
    "symbols": ["INFY"]
}}

EXAMPLE 3

User:
I want ₹20 lakh in 8 years with moderate risk.

JSON:
{{
    "required_capabilities": ["financial_planning"],
    "risk_preference": "moderate",
    "initial_amount": null,
    "target_amount": 2000000,
    "years": 8,
    "annual_return": null,
    "symbols": []
}}

EXAMPLE 4

User:
Analyze the technical indicators and risk of TCS.

JSON:
{{
    "required_capabilities": [
        "technical_analysis",
        "risk_analysis"
    ],
    "risk_preference": null,
    "initial_amount": null,
    "target_amount": null,
    "years": null,
    "annual_return": null,
    "symbols": ["TCS"]
}}
"""

        # ---------------------------------------------------------
        # 3. Call local Mistral through Ollama
        # ---------------------------------------------------------
        try:
            response = ollama.chat(
                model=self.MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": query,
                    },
                ],
                format="json",
                options={
                    "temperature": 0,
                    "num_ctx": 2048,
                },
            )

            # -----------------------------------------------------
            # 4. Extract model response
            # -----------------------------------------------------
            content = response["message"]["content"]

            # -----------------------------------------------------
            # 5. Parse JSON
            # -----------------------------------------------------
            data = json.loads(content)

            # -----------------------------------------------------
            # 6. Add original query BEFORE Pydantic validation
            # -----------------------------------------------------
            #
            # TaskRequirement requires:
            #
            #     query: str
            #
            # But we deliberately told Mistral not to generate it.
            # Therefore Python adds the original query here.
            #
            data["query"] = query

            # -----------------------------------------------------
            # 7. Validate against TaskRequirement
            # -----------------------------------------------------
            requirement = TaskRequirement.model_validate(data)

            # -----------------------------------------------------
            # 8. Preserve exact original query
            # -----------------------------------------------------
            requirement.query = query

            # -----------------------------------------------------
            # 9. Clean capabilities
            # -----------------------------------------------------
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

            # -----------------------------------------------------
            # 10. Normalize risk preference
            # -----------------------------------------------------
            if requirement.risk_preference:
                risk = (
                    requirement.risk_preference
                    .strip()
                    .lower()
                )

                # Normalize "medium" → "moderate"
                if risk == "medium":
                    risk = "moderate"

                if risk in {"low", "moderate", "high"}:
                    requirement.risk_preference = risk
                else:
                    requirement.risk_preference = None

            # -----------------------------------------------------
            # 11. Clean and normalize symbols
            # -----------------------------------------------------
            cleaned_symbols = []

            for symbol in requirement.symbols:

                if not symbol:
                    continue

                normalized_symbol = symbol.strip().upper()

                # Prevent risk levels from appearing as symbols.
                if normalized_symbol.lower() in self.ALLOWED_RISK_LEVELS:
                    continue

                # Remove duplicates.
                if normalized_symbol not in cleaned_symbols:
                    cleaned_symbols.append(
                        normalized_symbol
                    )

            requirement.symbols = cleaned_symbols

            # -----------------------------------------------------
            # 12. Return validated requirement
            # -----------------------------------------------------
            return requirement

        # ---------------------------------------------------------
        # 13. JSON parsing error
        # ---------------------------------------------------------
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Mistral returned invalid JSON."
            ) from exc

        # ---------------------------------------------------------
        # 14. Pydantic validation error
        # ---------------------------------------------------------
        except ValidationError as exc:
            raise RuntimeError(
                "Mistral returned data that does not "
                "match TaskRequirement."
            ) from exc

        # ---------------------------------------------------------
        # 15. Other errors
        # ---------------------------------------------------------
        except Exception as exc:
            raise RuntimeError(
                f"Mistral query analysis failed: {exc}"
            ) from exc