import json
import time
from pathlib import Path

from ollama import chat


# ---------------------------------------------------------
# 1. Models to compare
# ---------------------------------------------------------

MODELS = [
    "qwen3:4b",
    "qwen3:8b",
]


# ---------------------------------------------------------
# 2. Capabilities allowed by our financial system
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# 3. Benchmark dataset
# ---------------------------------------------------------

BENCHMARK_QUERIES = [
    {
        "query": "Should I invest in TCS?",
        "capabilities": ["investment_analysis"],
        "risk_preference": None,
        "target_amount": None,
        "years": None,
        "symbols": ["TCS"],
    },
    {
        "query": "What is the risk of investing in INFY?",
        "capabilities": ["risk_analysis"],
        "risk_preference": None,
        "target_amount": None,
        "years": None,
        "symbols": ["INFY"],
    },
    {
        "query": "Analyze the technical indicators of TCS.",
        "capabilities": ["technical_analysis"],
        "risk_preference": None,
        "target_amount": None,
        "years": None,
        "symbols": ["TCS"],
    },
    {
        "query": "Analyze the fundamentals of INFY.",
        "capabilities": ["fundamental_analysis"],
        "risk_preference": None,
        "target_amount": None,
        "years": None,
        "symbols": ["INFY"],
    },
    {
        "query": "What is the investor sentiment for TCS?",
        "capabilities": ["sentiment_analysis"],
        "risk_preference": None,
        "target_amount": None,
        "years": None,
        "symbols": ["TCS"],
    },
    {
        "query": "Analyze the current market trend.",
        "capabilities": ["market_research"],
        "risk_preference": None,
        "target_amount": None,
        "years": None,
        "symbols": [],
    },
    {
        "query": "Build a diversified portfolio using TCS and INFY.",
        "capabilities": [
            "portfolio_management",
            "investment_analysis",
        ],
        "risk_preference": None,
        "target_amount": None,
        "years": None,
        "symbols": ["TCS", "INFY"],
    },
    {
        "query": "I want ₹20 lakh in 8 years with moderate risk.",
        "capabilities": ["financial_planning"],
        "risk_preference": "moderate",
        "target_amount": 2_000_000,
        "years": 8,
        "symbols": [],
    },
    {
        "query": "Analyze TCS from investment, risk and technical perspectives.",
        "capabilities": [
            "investment_analysis",
            "risk_analysis",
            "technical_analysis",
        ],
        "risk_preference": None,
        "target_amount": None,
        "years": None,
        "symbols": ["TCS"],
    },
    {
        "query": "Is TCS good for my portfolio?",
        "capabilities": [
            "portfolio_management",
            "investment_analysis",
        ],
        "risk_preference": None,
        "target_amount": None,
        "years": None,
        "symbols": ["TCS"],
    },
    {
        "query": "Evaluate the risk and market trend of INFY.",
        "capabilities": [
            "risk_analysis",
            "market_research",
        ],
        "risk_preference": None,
        "target_amount": None,
        "years": None,
        "symbols": ["INFY"],
    },
    {
        "query": "Give me a fundamental and technical analysis of TCS.",
        "capabilities": [
            "fundamental_analysis",
            "technical_analysis",
        ],
        "risk_preference": None,
        "target_amount": None,
        "years": None,
        "symbols": ["TCS"],
    },
    {
        "query": "I have ₹5 lakh and want to invest it for 5 years.",
        "capabilities": ["financial_planning"],
        "risk_preference": None,
        "target_amount": None,
        "years": 5,
        "symbols": [],
    },
    {
        "query": "Compare the investment potential of TCS and INFY.",
        "capabilities": ["investment_analysis"],
        "risk_preference": None,
        "target_amount": None,
        "years": None,
        "symbols": ["TCS", "INFY"],
    },
    {
        "query": "Check the volatility and risk level of TCS.",
        "capabilities": ["risk_analysis"],
        "risk_preference": None,
        "target_amount": None,
        "years": None,
        "symbols": ["TCS"],
    },
    {
        "query": "What does the recent price trend of INFY indicate?",
        "capabilities": [
            "technical_analysis",
            "market_research",
        ],
        "risk_preference": None,
        "target_amount": None,
        "years": None,
        "symbols": ["INFY"],
    },
    {
        "query": "Analyze TCS using news sentiment and market conditions.",
        "capabilities": [
            "sentiment_analysis",
            "market_research",
        ],
        "risk_preference": None,
        "target_amount": None,
        "years": None,
        "symbols": ["TCS"],
    },
    {
        "query": "I need ₹50 lakh for retirement in 15 years with low risk.",
        "capabilities": ["financial_planning"],
        "risk_preference": "low",
        "target_amount": 5_000_000,
        "years": 15,
        "symbols": [],
    },
    {
        "query": "Should I invest in TCS considering its fundamentals and risk?",
        "capabilities": [
            "investment_analysis",
            "fundamental_analysis",
            "risk_analysis",
        ],
        "risk_preference": None,
        "target_amount": None,
        "years": None,
        "symbols": ["TCS"],
    },
    {
        "query": "Construct a portfolio using TCS and INFY and assess its risk.",
        "capabilities": [
            "portfolio_management",
            "risk_analysis",
            "investment_analysis",
        ],
        "risk_preference": None,
        "target_amount": None,
        "years": None,
        "symbols": ["TCS", "INFY"],
    },
]


# ---------------------------------------------------------
# 4. Prompt used for BOTH models
# ---------------------------------------------------------

SYSTEM_PROMPT = f"""
You are a financial query analyzer.

Your ONLY job is to convert the user's natural-language query
into structured JSON.

Do NOT provide financial advice.
Do NOT calculate financial metrics.
Do NOT explain your reasoning.

Allowed capabilities:
{", ".join(ALLOWED_CAPABILITIES)}

Return ONLY valid JSON with exactly these fields:

{{
    "required_capabilities": [],
    "risk_preference": null,
    "initial_amount": null,
    "target_amount": null,
    "years": null,
    "annual_return": null,
    "symbols": []
}}

Rules:

1. Select every capability genuinely required by the query.

2. Do not add capabilities that are not required.

3. Risk preference and risk analysis are different.
   Example:
   "moderate risk" means:
   risk_preference = "moderate"
   It does NOT automatically mean risk_analysis.

4. Valid risk preferences:
   low, moderate, high.

5. Convert Indian currency expressions to numbers.
   ₹20 lakh = 2000000
   ₹50 lakh = 5000000
   ₹1 crore = 10000000

6. Extract investment horizon in years.

7. Extract stock symbols only when explicitly mentioned.
   Examples:
   TCS -> TCS
   INFY -> INFY

8. Never put words such as "low", "moderate", "medium",
   or "high" into symbols.

9. If a field is not stated, return null.

10. Return JSON only.
"""


# ---------------------------------------------------------
# 5. Run one query against one model
# ---------------------------------------------------------

def run_model(model_name, query):
    start_time = time.perf_counter()

    try:
        response = chat(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": query,
                },
            ],
            format="json",
            options={
                "temperature": 0,
            },
        )

        elapsed = time.perf_counter() - start_time

        raw_output = response.message.content

        try:
            parsed_output = json.loads(raw_output)
            json_valid = True
        except json.JSONDecodeError:
            parsed_output = None
            json_valid = False

        return {
            "model": model_name,
            "query": query,
            "latency_seconds": round(elapsed, 3),
            "json_valid": json_valid,
            "output": parsed_output,
            "raw_output": raw_output,
            "error": None,
        }

    except Exception as exc:
        elapsed = time.perf_counter() - start_time

        return {
            "model": model_name,
            "query": query,
            "latency_seconds": round(elapsed, 3),
            "json_valid": False,
            "output": None,
            "raw_output": None,
            "error": str(exc),
        }


# ---------------------------------------------------------
# 6. Compare model output with expected answer
# ---------------------------------------------------------

def calculate_scores(expected, actual):
    if actual is None:
        return {
            "capability_correct": False,
            "risk_correct": False,
            "amount_correct": False,
            "years_correct": False,
            "symbols_correct": False,
        }

    expected_capabilities = set(expected["capabilities"])
    actual_capabilities = set(
        actual.get("required_capabilities", [])
    )

    expected_symbols = set(expected["symbols"])
    actual_symbols = set(
        actual.get("symbols", [])
    )

    return {
        "capability_correct": (
            expected_capabilities == actual_capabilities
        ),
        "risk_correct": (
            expected["risk_preference"]
            == actual.get("risk_preference")
        ),
        "amount_correct": (
            expected["target_amount"]
            == actual.get("target_amount")
        ),
        "years_correct": (
            expected["years"]
            == actual.get("years")
        ),
        "symbols_correct": (
            expected_symbols == actual_symbols
        ),
    }


# ---------------------------------------------------------
# 7. Main benchmark
# ---------------------------------------------------------

def main():
    all_results = []

    print("\n========================================")
    print("LLM QUERY ANALYZER BENCHMARK")
    print("========================================")

    print(f"\nQueries: {len(BENCHMARK_QUERIES)}")
    print(f"Models: {len(MODELS)}")

    for model_name in MODELS:

        print(f"\n\nMODEL: {model_name}")
        print("-" * 50)

        for index, test_case in enumerate(BENCHMARK_QUERIES, start=1):

            print(
                f"[{index}/{len(BENCHMARK_QUERIES)}] "
                f"{test_case['query']}"
            )

            result = run_model(
                model_name,
                test_case["query"],
            )

            scores = calculate_scores(
                test_case,
                result["output"],
            )

            result.update(scores)

            all_results.append(result)

            print(
                f"  Latency: "
                f"{result['latency_seconds']} sec"
            )

            print(
                f"  JSON: "
                f"{result['json_valid']}"
            )

            print(
                f"  Capabilities: "
                f"{scores['capability_correct']}"
            )

            print(
                f"  Symbols: "
                f"{scores['symbols_correct']}"
            )

    # -----------------------------------------------------
    # Save raw results
    # -----------------------------------------------------

    output_directory = Path("experiments")
    output_directory.mkdir(exist_ok=True)

    output_file = (
        output_directory
        / "llm_benchmark_results.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            all_results,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print("\n========================================")
    print("BENCHMARK COMPLETE")
    print("========================================")
    print(f"\nResults saved to:")
    print(output_file)


if __name__ == "__main__":
    main()