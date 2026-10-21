import pandas as pd

from app.agents.fundamental_analysis_agent import (
    FundamentalAnalysisAgent,
)
from app.models.schemas import AgentStatus


def create_fundamental_data():
    return pd.DataFrame(
        {
            "symbol": ["TCS", "TCS"],
            "period": ["2024", "2025"],
            "revenue": [100.0, 150.0],
            "net_income": [15.0, 30.0],
            "eps": [10.0, 15.0],
            "price": [200.0, 300.0],
        }
    )


def test_fundamental_agent_has_correct_configuration():
    agent = FundamentalAnalysisAgent()

    assert agent.name == (
        "Fundamental Analysis Agent"
    )

    assert agent.reliability == 0.91
    assert agent.estimated_cost == 750


def test_fundamental_agent_fails_with_insufficient_budget():
    agent = FundamentalAnalysisAgent()

    result = agent.execute(
        query="Analyze the fundamentals of TCS.",
        budget=500,
        fundamental_data=create_fundamental_data(),
    )

    assert result.status == AgentStatus.FAILED
    assert result.failure_reason == (
        "Insufficient budget."
    )


def test_fundamental_agent_fails_with_empty_data():
    agent = FundamentalAnalysisAgent()

    result = agent.execute(
        query="Analyze the fundamentals of TCS.",
        budget=1000,
        fundamental_data=pd.DataFrame(),
    )

    assert result.status == AgentStatus.FAILED
    assert result.failure_reason == (
        "Fundamental data is empty."
    )


def test_fundamental_agent_fails_when_symbol_is_missing():
    agent = FundamentalAnalysisAgent()

    result = agent.execute(
        query="Analyze the fundamentals of MSFT.",
        budget=1000,
        fundamental_data=create_fundamental_data(),
    )

    assert result.status == AgentStatus.FAILED
    assert result.failure_reason == (
        "No supported symbol found in query."
    )


def test_fundamental_agent_completes_analysis():
    agent = FundamentalAnalysisAgent()

    result = agent.execute(
        query="Analyze the fundamentals of TCS.",
        budget=1000,
        fundamental_data=create_fundamental_data(),
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.used_budget == 550
    assert "TCS" in result.output
    assert "Revenue growth" in result.output
    assert "Net profit margin" in result.output
    assert "EPS growth" in result.output
    assert "Price-to-earnings ratio" in result.output
    assert "Fundamental Score" in result.output


def test_fundamental_agent_returns_expected_assessment():
    agent = FundamentalAnalysisAgent()

    result = agent.execute(
        query="Analyze the fundamentals of TCS.",
        budget=1000,
        fundamental_data=create_fundamental_data(),
    )

    assert "Strong Fundamentals" in result.output