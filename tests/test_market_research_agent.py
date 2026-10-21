import pandas as pd

from app.agents.market_research_agent import MarketResearchAgent
from app.models.schemas import AgentStatus


def create_market_data():
    return pd.DataFrame(
        {
            "date": pd.date_range(
                "2026-01-01",
                periods=5,
            ),
            "symbol": [
                "TCS",
                "TCS",
                "TCS",
                "TCS",
                "TCS",
            ],
            "open": [
                100,
                105,
                110,
                115,
                120,
            ],
            "high": [
                105,
                110,
                115,
                120,
                125,
            ],
            "low": [
                95,
                100,
                105,
                110,
                115,
            ],
            "close": [
                100,
                105,
                110,
                115,
                120,
            ],
            "volume": [
                1000,
                1200,
                1400,
                1600,
                2000,
            ],
        }
    )


def test_market_research_agent_initialization():
    agent = MarketResearchAgent()

    assert agent.name == "Market Research Agent"
    assert agent.reliability == 0.89
    assert agent.estimated_cost == 650


def test_market_research_agent_completes_analysis():
    agent = MarketResearchAgent()

    market_data = create_market_data()

    result = agent.execute(
        query="Analyze TCS market trend",
        budget=500,
        market_data=market_data,
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.agent_name == "Market Research Agent"
    assert result.used_budget == 450


def test_market_research_agent_output_contains_trend():
    agent = MarketResearchAgent()

    market_data = create_market_data()

    result = agent.execute(
        query="Analyze TCS market trend",
        budget=500,
        market_data=market_data,
    )

    assert result.output is not None
    assert "Strong Upward Trend" in result.output
    assert "Price Trend: Upward" in result.output
    assert "Volume Trend: Increasing" in result.output


def test_market_research_agent_output_contains_metrics():
    agent = MarketResearchAgent()

    market_data = create_market_data()

    result = agent.execute(
        query="Analyze TCS market trend",
        budget=500,
        market_data=market_data,
    )

    assert "Total return:" in result.output
    assert "Average daily volume:" in result.output
    assert "Historical volatility:" in result.output


def test_market_research_agent_rejects_insufficient_budget():
    agent = MarketResearchAgent()

    market_data = create_market_data()

    result = agent.execute(
        query="Analyze TCS market trend",
        budget=400,
        market_data=market_data,
    )

    assert result.status == AgentStatus.FAILED
    assert result.used_budget == 0
    assert result.failure_reason == "Insufficient budget."


def test_market_research_agent_rejects_empty_data():
    agent = MarketResearchAgent()

    market_data = pd.DataFrame()

    result = agent.execute(
        query="Analyze TCS market trend",
        budget=500,
        market_data=market_data,
    )

    assert result.status == AgentStatus.FAILED
    assert result.failure_reason == "Market data is empty."


def test_market_research_agent_rejects_unknown_symbol():
    agent = MarketResearchAgent()

    market_data = create_market_data()

    result = agent.execute(
        query="Analyze XYZ market trend",
        budget=500,
        market_data=market_data,
    )

    assert result.status == AgentStatus.FAILED
    assert (
        result.failure_reason
        == "No supported symbol found in query."
    )


def test_market_research_agent_finds_symbol_case_insensitively():
    agent = MarketResearchAgent()

    market_data = create_market_data()

    result = agent.execute(
        query="Analyze tcs market trend",
        budget=500,
        market_data=market_data,
    )

    assert result.status == AgentStatus.COMPLETED
    assert "TCS" in result.output


def test_market_research_agent_handles_invalid_market_data():
    agent = MarketResearchAgent()

    market_data = create_market_data()

    market_data.loc[2, "close"] = -10

    result = agent.execute(
        query="Analyze TCS market trend",
        budget=500,
        market_data=market_data,
    )

    assert result.status == AgentStatus.FAILED