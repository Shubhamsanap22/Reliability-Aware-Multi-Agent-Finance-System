import pandas as pd

from app.agents.technical_analysis_agent import (
    TechnicalAnalysisAgent,
)
from app.models.schemas import AgentStatus


def create_market_data():
    prices = [
        100,
        101,
        102,
        103,
        104,
        105,
        106,
        107,
        108,
        109,
        110,
        111,
        112,
        113,
        114,
        115,
        116,
        117,
        118,
        119,
        120,
        121,
        122,
        123,
        124,
    ]

    return pd.DataFrame(
        {
            "date": pd.date_range(
                start="2025-01-01",
                periods=len(prices),
                freq="D",
            ),
            "symbol": ["TCS"] * len(prices),
            "open": prices,
            "high": [
                price + 1
                for price in prices
            ],
            "low": [
                price - 1
                for price in prices
            ],
            "close": prices,
            "volume": [
                100000
                for _ in prices
            ],
        }
    )


def test_technical_agent_has_correct_configuration():
    agent = TechnicalAnalysisAgent()

    assert agent.name == (
        "Technical Analysis Agent"
    )

    assert agent.reliability == 0.90
    assert agent.estimated_cost == 700


def test_technical_agent_fails_with_insufficient_budget():
    agent = TechnicalAnalysisAgent()

    result = agent.execute(
        query="Analyze the technical indicators of TCS.",
        budget=400,
        market_data=create_market_data(),
    )

    assert result.status == AgentStatus.FAILED
    assert result.failure_reason == (
        "Insufficient budget."
    )


def test_technical_agent_returns_dummy_result_without_data():
    agent = TechnicalAnalysisAgent()

    result = agent.execute(
        query="Analyze the technical indicators of TCS.",
        budget=1000,
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.used_budget == 500
    assert "Dummy technical analysis completed." in (
        result.output
    )


def test_technical_agent_fails_with_empty_data():
    agent = TechnicalAnalysisAgent()

    result = agent.execute(
        query="Analyze the technical indicators of TCS.",
        budget=1000,
        market_data=pd.DataFrame(),
    )

    assert result.status == AgentStatus.FAILED
    assert result.failure_reason == (
        "Market data is empty."
    )


def test_technical_agent_fails_without_symbol_column():
    agent = TechnicalAnalysisAgent()

    data = create_market_data().drop(
        columns=["symbol"]
    )

    result = agent.execute(
        query="Analyze the technical indicators of TCS.",
        budget=1000,
        market_data=data,
    )

    assert result.status == AgentStatus.FAILED
    assert result.failure_reason == (
        "Market data does not contain a symbol column."
    )


def test_technical_agent_fails_without_close_column():
    agent = TechnicalAnalysisAgent()

    data = create_market_data().drop(
        columns=["close"]
    )

    result = agent.execute(
        query="Analyze the technical indicators of TCS.",
        budget=1000,
        market_data=data,
    )

    assert result.status == AgentStatus.FAILED
    assert result.failure_reason == (
        "Market data does not contain a close column."
    )


def test_technical_agent_fails_when_symbol_is_missing():
    agent = TechnicalAnalysisAgent()

    result = agent.execute(
        query="Analyze the technical indicators of MSFT.",
        budget=1000,
        market_data=create_market_data(),
    )

    assert result.status == AgentStatus.FAILED
    assert result.failure_reason == (
        "No supported symbol found in query."
    )


def test_technical_agent_completes_analysis():
    agent = TechnicalAnalysisAgent()

    result = agent.execute(
        query="Analyze the technical indicators of TCS.",
        budget=1000,
        market_data=create_market_data(),
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.used_budget == 500
    assert "TCS" in result.output
    assert "20-day moving average" in result.output
    assert "price momentum" in result.output
    assert "RSI" in result.output
    assert "Technical Score" in result.output


def test_technical_agent_detects_strong_signals():
    agent = TechnicalAnalysisAgent()

    result = agent.execute(
        query="Analyze the technical indicators of TCS.",
        budget=1000,
        market_data=create_market_data(),
    )

    assert "Moderate Technical Signals" in result.output