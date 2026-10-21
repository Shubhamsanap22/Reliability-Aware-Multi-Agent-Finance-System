"""
Mistral Query Analyzer Benchmark

Purpose:
    Evaluate the local Mistral model used by MistralQueryAnalyzer.

Metrics:
    1. Capability exact-match accuracy
    2. Risk preference accuracy
    3. Initial amount extraction accuracy
    4. Target amount extraction accuracy
    5. Years extraction accuracy
    6. Symbol extraction accuracy
    7. JSON validity
    8. Pydantic validation
    9. Latency

Output:
    experiments/mistral_benchmark_results.json
"""

import json
import sys
import time
from pathlib import Path


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORT PROJECT CODE
# ============================================================

from app.analysis.mistral_query_analyzer import MistralQueryAnalyzer


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "mistral:latest"

OUTPUT_FILE = (
    PROJECT_ROOT
    / "experiments"
    / "mistral_benchmark_results.json"
)


# ============================================================
# GROUND-TRUTH DATASET
# ============================================================
#
# IMPORTANT:
# These labels represent the annotation rules used for this
# benchmark.
#
# Extra capabilities are considered an error.
#
# Risk preference does NOT automatically mean risk_analysis.
#
# initial_amount and target_amount are evaluated separately.
#
# ============================================================

TEST_CASES = [

    {
        "id": 1,
        "query": "Should I invest in TCS?",
        "capabilities": [
            "investment_analysis"
        ],
        "risk": None,
        "initial_amount": None,
        "target_amount": None,
        "years": None,
        "annual_return": None,
        "symbols": ["TCS"],
    },

    {
        "id": 2,
        "query": "What is the risk of investing in INFY?",
        "capabilities": [
            "risk_analysis"
        ],
        "risk": None,
        "initial_amount": None,
        "target_amount": None,
        "years": None,
        "annual_return": None,
        "symbols": ["INFY"],
    },

    {
        "id": 3,
        "query": "I want ₹20 lakh in 8 years with moderate risk.",
        "capabilities": [
            "financial_planning"
        ],
        "risk": "moderate",
        "initial_amount": None,
        "target_amount": 2000000,
        "years": 8,
        "annual_return": None,
        "symbols": [],
    },

    {
        "id": 4,
        "query": "Analyze the technical indicators and risk of TCS.",
        "capabilities": [
            "technical_analysis",
            "risk_analysis",
        ],
        "risk": None,
        "initial_amount": None,
        "target_amount": None,
        "years": None,
        "annual_return": None,
        "symbols": ["TCS"],
    },

    {
        "id": 5,
        "query": "Analyze the fundamentals of INFY.",
        "capabilities": [
            "fundamental_analysis"
        ],
        "risk": None,
        "initial_amount": None,
        "target_amount": None,
        "years": None,
        "annual_return": None,
        "symbols": ["INFY"],
    },

    {
        "id": 6,
        "query": "What is investor sentiment for TCS?",
        "capabilities": [
            "sentiment_analysis"
        ],
        "risk": None,
        "initial_amount": None,
        "target_amount": None,
        "years": None,
        "annual_return": None,
        "symbols": ["TCS"],
    },

    {
        "id": 7,
        "query": "How should I build a diversified portfolio using TCS and INFY?",
        "capabilities": [
            "portfolio_management",
            "investment_analysis",
        ],
        "risk": None,
        "initial_amount": None,
        "target_amount": None,
        "years": None,
        "annual_return": None,
        "symbols": ["TCS", "INFY"],
    },

    {
        "id": 8,
        "query": "What are the current market trends?",
        "capabilities": [
            "market_research"
        ],
        "risk": None,
        "initial_amount": None,
        "target_amount": None,
        "years": None,
        "annual_return": None,
        "symbols": [],
    },

    {
        "id": 9,
        "query": "Calculate the technical indicators for TCS.",
        "capabilities": [
            "technical_analysis"
        ],
        "risk": None,
        "initial_amount": None,
        "target_amount": None,
        "years": None,
        "annual_return": None,
        "symbols": ["TCS"],
    },

    {
        "id": 10,
        "query": "Evaluate the financial health and profitability of INFY.",
        "capabilities": [
            "fundamental_analysis"
        ],
        "risk": None,
        "initial_amount": None,
        "target_amount": None,
        "years": None,
        "annual_return": None,
        "symbols": ["INFY"],
    },

    {
        "id": 11,
        "query": "What is the risk level of TCS?",
        "capabilities": [
            "risk_analysis"
        ],
        "risk": None,
        "initial_amount": None,
        "target_amount": None,
        "years": None,
        "annual_return": None,
        "symbols": ["TCS"],
    },

    {
        "id": 12,
        "query": "What is the sentiment around INFY?",
        "capabilities": [
            "sentiment_analysis"
        ],
        "risk": None,
        "initial_amount": None,
        "target_amount": None,
        "years": None,
        "annual_return": None,
        "symbols": ["INFY"],
    },

    {
        "id": 13,
        "query": "I want to invest ₹5 lakh for 5 years.",
        "capabilities": [
            "investment_analysis"
        ],
        "risk": None,
        "initial_amount": 500000,
        "target_amount": None,
        "years": 5,
        "annual_return": None,
        "symbols": [],
    },

    {
        "id": 14,
        "query": "Compare the investment potential of TCS and INFY.",
        "capabilities": [
            "investment_analysis"
        ],
        "risk": None,
        "initial_amount": None,
        "target_amount": None,
        "years": None,
        "annual_return": None,
        "symbols": ["TCS", "INFY"],
    },

    {
        "id": 15,
        "query": "How risky is investing in TCS?",
        "capabilities": [
            "risk_analysis"
        ],
        "risk": None,
        "initial_amount": None,
        "target_amount": None,
        "years": None,
        "annual_return": None,
        "symbols": ["TCS"],
    },

    {
        "id": 16,
        "query": "Analyze the market and recent price trend of TCS.",
        "capabilities": [
            "market_research",
            "technical_analysis",
        ],
        "risk": None,
        "initial_amount": None,
        "target_amount": None,
        "years": None,
        "annual_return": None,
        "symbols": ["TCS"],
    },

    {
        "id": 17,
        "query": "I have ₹10 lakh and want to invest it for 10 years.",
        "capabilities": [
            "investment_analysis"
        ],
        "risk": None,
        "initial_amount": 1000000,
        "target_amount": None,
        "years": 10,
        "annual_return": None,
        "symbols": [],
    },

    {
        "id": 18,
        "query": "I need ₹50 lakh for retirement in 15 years with low risk.",
        "capabilities": [
            "financial_planning"
        ],
        "risk": "low",
        "initial_amount": None,
        "target_amount": 5000000,
        "years": 15,
        "annual_return": None,
        "symbols": [],
    },

    {
        "id": 19,
        "query": "Analyze the investment in TCS considering its fundamentals and risk.",
        "capabilities": [
            "fundamental_analysis",
            "investment_analysis",
            "risk_analysis",
        ],
        "risk": None,
        "initial_amount": None,
        "target_amount": None,
        "years": None,
        "annual_return": None,
        "symbols": ["TCS"],
    },

    {
        "id": 20,
        "query": "Build a portfolio using TCS and INFY considering investment potential and risk.",
        "capabilities": [
            "portfolio_management",
            "investment_analysis",
            "risk_analysis",
        ],
        "risk": None,
        "initial_amount": None,
        "target_amount": None,
        "years": None,
        "annual_return": None,
        "symbols": ["TCS", "INFY"],
    },
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_list(values):
    """
    Normalize list values so comparison is consistent.
    """
    if values is None:
        return []

    return sorted(
        {
            str(value).strip().lower()
            for value in values
            if value is not None
        }
    )


def normalize_symbols(values):
    """
    Normalize ticker symbols.
    """
    if values is None:
        return []

    return sorted(
        {
            str(value).strip().upper()
            for value in values
            if value is not None
        }
    )


def compare_capabilities(predicted, expected):
    """
    Exact multi-label capability match.

    Example:
        expected = ["investment_analysis"]
        predicted = ["investment_analysis"]

        -> True

    Extra or missing capabilities -> False.
    """
    return normalize_list(predicted) == normalize_list(expected)


def compare_value(predicted, expected):
    """
    Generic exact-value comparison.
    """
    return predicted == expected


def compare_symbols(predicted, expected):
    """
    Exact ticker-set comparison.
    """
    return normalize_symbols(predicted) == normalize_symbols(expected)


# ============================================================
# RUN BENCHMARK
# ============================================================

def run_benchmark():

    analyzer = MistralQueryAnalyzer()

    results = []

    print("=" * 70)
    print("MISTRAL QUERY ANALYZER BENCHMARK")
    print("=" * 70)
    print(f"Model: {MODEL_NAME}")
    print(f"Queries: {len(TEST_CASES)}")
    print()

    for test_case in TEST_CASES:

        query_id = test_case["id"]
        query = test_case["query"]

        print("-" * 70)
        print(f"Query {query_id}/{len(TEST_CASES)}")
        print(f"Input: {query}")

        start_time = time.perf_counter()

        try:
            requirement = analyzer.analyze(query)

            latency = time.perf_counter() - start_time

            predicted_capabilities = (
                requirement.required_capabilities
            )

            predicted_risk = requirement.risk_preference

            predicted_initial_amount = (
                requirement.initial_amount
            )

            predicted_target_amount = (
                requirement.target_amount
            )

            predicted_years = requirement.years

            predicted_annual_return = (
                requirement.annual_return
            )

            predicted_symbols = requirement.symbols

            capability_correct = compare_capabilities(
                predicted_capabilities,
                test_case["capabilities"],
            )

            risk_correct = compare_value(
                predicted_risk,
                test_case["risk"],
            )

            initial_amount_correct = compare_value(
                predicted_initial_amount,
                test_case["initial_amount"],
            )

            target_amount_correct = compare_value(
                predicted_target_amount,
                test_case["target_amount"],
            )

            years_correct = compare_value(
                predicted_years,
                test_case["years"],
            )

            annual_return_correct = compare_value(
                predicted_annual_return,
                test_case["annual_return"],
            )

            symbols_correct = compare_symbols(
                predicted_symbols,
                test_case["symbols"],
            )

            json_valid = True
            pydantic_valid = True

            status = "success"

            error = None

            print(f"Predicted capabilities: {predicted_capabilities}")
            print(f"Expected capabilities:  {test_case['capabilities']}")
            print(
                f"Capability correct:     "
                f"{capability_correct}"
            )

            print(
                f"Predicted risk:          "
                f"{predicted_risk}"
            )

            print(
                f"Predicted initial:       "
                f"{predicted_initial_amount}"
            )

            print(
                f"Predicted target:        "
                f"{predicted_target_amount}"
            )

            print(
                f"Predicted years:         "
                f"{predicted_years}"
            )

            print(
                f"Predicted symbols:       "
                f"{predicted_symbols}"
            )

            print(
                f"Latency:                 "
                f"{latency:.3f} seconds"
            )

        except json.JSONDecodeError as exc:

            latency = time.perf_counter() - start_time

            capability_correct = False
            risk_correct = False
            initial_amount_correct = False
            target_amount_correct = False
            years_correct = False
            annual_return_correct = False
            symbols_correct = False

            json_valid = False
            pydantic_valid = False

            predicted_capabilities = []
            predicted_risk = None
            predicted_initial_amount = None
            predicted_target_amount = None
            predicted_years = None
            predicted_annual_return = None
            predicted_symbols = []

            status = "invalid_json"

            error = str(exc)

            print(f"ERROR: Invalid JSON: {exc}")

        except Exception as exc:

            latency = time.perf_counter() - start_time

            capability_correct = False
            risk_correct = False
            initial_amount_correct = False
            target_amount_correct = False
            years_correct = False
            annual_return_correct = False
            symbols_correct = False

            json_valid = False
            pydantic_valid = False

            predicted_capabilities = []
            predicted_risk = None
            predicted_initial_amount = None
            predicted_target_amount = None
            predicted_years = None
            predicted_annual_return = None
            predicted_symbols = []

            status = "error"

            error = str(exc)

            print(f"ERROR: {exc}")

        result = {
            "id": query_id,
            "query": query,

            # -----------------------------
            # Expected values
            # -----------------------------

            "expected": {
                "capabilities": test_case["capabilities"],
                "risk": test_case["risk"],
                "initial_amount": test_case["initial_amount"],
                "target_amount": test_case["target_amount"],
                "years": test_case["years"],
                "annual_return": test_case["annual_return"],
                "symbols": test_case["symbols"],
            },

            # -----------------------------
            # Predicted values
            # -----------------------------

            "predicted": {
                "capabilities": predicted_capabilities,
                "risk": predicted_risk,
                "initial_amount": predicted_initial_amount,
                "target_amount": predicted_target_amount,
                "years": predicted_years,
                "annual_return": predicted_annual_return,
                "symbols": predicted_symbols,
            },

            # -----------------------------
            # Evaluation
            # -----------------------------

            "evaluation": {
                "capability_correct": capability_correct,
                "risk_correct": risk_correct,
                "initial_amount_correct": (
                    initial_amount_correct
                ),
                "target_amount_correct": (
                    target_amount_correct
                ),
                "years_correct": years_correct,
                "annual_return_correct": (
                    annual_return_correct
                ),
                "symbols_correct": symbols_correct,
                "json_valid": json_valid,
                "pydantic_valid": pydantic_valid,
            },

            # -----------------------------
            # Performance
            # -----------------------------

            "latency_seconds": round(latency, 4),

            # -----------------------------
            # Execution status
            # -----------------------------

            "status": status,
            "error": error,
        }

        results.append(result)

    return results


# ============================================================
# CALCULATE SUMMARY
# ============================================================

def calculate_summary(results):

    total = len(results)

    if total == 0:
        return {}

    capability_correct = sum(
        r["evaluation"]["capability_correct"]
        for r in results
    )

    risk_correct = sum(
        r["evaluation"]["risk_correct"]
        for r in results
    )

    initial_amount_correct = sum(
        r["evaluation"]["initial_amount_correct"]
        for r in results
    )

    target_amount_correct = sum(
        r["evaluation"]["target_amount_correct"]
        for r in results
    )

    years_correct = sum(
        r["evaluation"]["years_correct"]
        for r in results
    )

    annual_return_correct = sum(
        r["evaluation"]["annual_return_correct"]
        for r in results
    )

    symbols_correct = sum(
        r["evaluation"]["symbols_correct"]
        for r in results
    )

    json_valid = sum(
        r["evaluation"]["json_valid"]
        for r in results
    )

    pydantic_valid = sum(
        r["evaluation"]["pydantic_valid"]
        for r in results
    )

    latencies = [
        r["latency_seconds"]
        for r in results
    ]

    latencies_sorted = sorted(latencies)

    average_latency = sum(latencies) / total

    if total % 2 == 0:
        median_latency = (
            latencies_sorted[total // 2 - 1]
            + latencies_sorted[total // 2]
        ) / 2
    else:
        median_latency = latencies_sorted[total // 2]

    summary = {
        "model": MODEL_NAME,

        "total_queries": total,

        # -----------------------------
        # Capability metrics
        # -----------------------------

        "capability_correct": capability_correct,

        "capability_accuracy": round(
            capability_correct / total,
            4,
        ),

        # -----------------------------
        # Extraction metrics
        # -----------------------------

        "risk_correct": risk_correct,

        "risk_accuracy": round(
            risk_correct / total,
            4,
        ),

        "initial_amount_correct": (
            initial_amount_correct
        ),

        "initial_amount_accuracy": round(
            initial_amount_correct / total,
            4,
        ),

        "target_amount_correct": (
            target_amount_correct
        ),

        "target_amount_accuracy": round(
            target_amount_correct / total,
            4,
        ),

        "years_correct": years_correct,

        "years_accuracy": round(
            years_correct / total,
            4,
        ),

        "annual_return_correct": (
            annual_return_correct
        ),

        "annual_return_accuracy": round(
            annual_return_correct / total,
            4,
        ),

        "symbols_correct": symbols_correct,

        "symbols_accuracy": round(
            symbols_correct / total,
            4,
        ),

        # -----------------------------
        # Output validity
        # -----------------------------

        "json_valid": json_valid,

        "json_validity": round(
            json_valid / total,
            4,
        ),

        "pydantic_valid": pydantic_valid,

        "pydantic_validity": round(
            pydantic_valid / total,
            4,
        ),

        # -----------------------------
        # Latency
        # -----------------------------

        "average_latency_seconds": round(
            average_latency,
            4,
        ),

        "median_latency_seconds": round(
            median_latency,
            4,
        ),

        "min_latency_seconds": round(
            min(latencies),
            4,
        ),

        "max_latency_seconds": round(
            max(latencies),
            4,
        ),
    }

    return summary


# ============================================================
# SAVE RESULTS
# ============================================================

def save_results(summary, results):

    output = {
        "benchmark": {
            "model": MODEL_NAME,
            "description": (
                "Benchmark of local Mistral query analyzer "
                "for financial capability classification "
                "and information extraction."
            ),
            "total_queries": len(TEST_CASES),
        },

        "summary": summary,

        "results": results,
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print("=" * 70)
    print("RESULTS SAVED")
    print("=" * 70)
    print(OUTPUT_FILE)


# ============================================================
# PRINT SUMMARY
# ============================================================

def print_summary(summary):

    print()
    print("=" * 70)
    print("BENCHMARK SUMMARY")
    print("=" * 70)

    print(
        f"Model:                         "
        f"{summary['model']}"
    )

    print(
        f"Total queries:                 "
        f"{summary['total_queries']}"
    )

    print()

    print(
        f"Capability accuracy:           "
        f"{summary['capability_correct']}/"
        f"{summary['total_queries']} "
        f"({summary['capability_accuracy'] * 100:.1f}%)"
    )

    print(
        f"Risk accuracy:                 "
        f"{summary['risk_correct']}/"
        f"{summary['total_queries']} "
        f"({summary['risk_accuracy'] * 100:.1f}%)"
    )

    print(
        f"Initial amount accuracy:       "
        f"{summary['initial_amount_correct']}/"
        f"{summary['total_queries']} "
        f"({summary['initial_amount_accuracy'] * 100:.1f}%)"
    )

    print(
        f"Target amount accuracy:        "
        f"{summary['target_amount_correct']}/"
        f"{summary['total_queries']} "
        f"({summary['target_amount_accuracy'] * 100:.1f}%)"
    )

    print(
        f"Years accuracy:                "
        f"{summary['years_correct']}/"
        f"{summary['total_queries']} "
        f"({summary['years_accuracy'] * 100:.1f}%)"
    )

    print(
        f"Annual return accuracy:        "
        f"{summary['annual_return_correct']}/"
        f"{summary['total_queries']} "
        f"({summary['annual_return_accuracy'] * 100:.1f}%)"
    )

    print(
        f"Symbol accuracy:               "
        f"{summary['symbols_correct']}/"
        f"{summary['total_queries']} "
        f"({summary['symbols_accuracy'] * 100:.1f}%)"
    )

    print(
        f"JSON validity:                 "
        f"{summary['json_valid']}/"
        f"{summary['total_queries']} "
        f"({summary['json_validity'] * 100:.1f}%)"
    )

    print(
        f"Pydantic validity:             "
        f"{summary['pydantic_valid']}/"
        f"{summary['total_queries']} "
        f"({summary['pydantic_validity'] * 100:.1f}%)"
    )

    print()

    print(
        f"Average latency:               "
        f"{summary['average_latency_seconds']:.3f} sec"
    )

    print(
        f"Median latency:                "
        f"{summary['median_latency_seconds']:.3f} sec"
    )

    print(
        f"Minimum latency:               "
        f"{summary['min_latency_seconds']:.3f} sec"
    )

    print(
        f"Maximum latency:               "
        f"{summary['max_latency_seconds']:.3f} sec"
    )

    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

def main():

    results = run_benchmark()

    summary = calculate_summary(results)

    save_results(
        summary=summary,
        results=results,
    )

    print_summary(summary)


if __name__ == "__main__":
    main()