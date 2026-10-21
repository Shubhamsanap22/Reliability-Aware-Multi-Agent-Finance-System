import pandas as pd

from app.agents.market_research_agent import MarketResearchAgent
from app.models.schemas import AgentStatus, TaskRequirement


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


def test_market_research_agent_uses_task_requirement_symbol():
    agent = MarketResearchAgent()

    requirement = TaskRequirement(
        query="Analyze the selected company",
        required_capabilities=[
            "market_research"
        ],
        symbols=["TCS"],
    )

    agent.set_task_requirement(requirement)

    result = agent.execute(
        query="Analyze the selected company",
        budget=500,
        market_data=create_market_data(),
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.agent_name == "Market Research Agent"
    assert result.output is not None
    assert "TCS" in result.output


def test_market_research_agent_prefers_structured_symbol():
    agent = MarketResearchAgent()

    requirement = TaskRequirement(
        query="Analyze the selected stock",
        required_capabilities=[
            "market_research"
        ],
        symbols=["TCS"],
    )

    agent.set_task_requirement(requirement)

    # TCS is deliberately absent from the query.
    # The agent must obtain it from TaskRequirement.
    result = agent.execute(
        query="Analyze the selected stock",
        budget=500,
        market_data=create_market_data(),
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.output is not None
    assert "TCS" in result.output


def test_market_research_agent_falls_back_to_query_symbol():
    agent = MarketResearchAgent()

    # No TaskRequirement is supplied.
    # Existing query-based behavior must still work.
    result = agent.execute(
        query="Analyze TCS market trend",
        budget=500,
        market_data=create_market_data(),
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.output is not None
    assert "TCS" in result.output


def test_market_research_agent_uses_matching_structured_symbol():
    agent = MarketResearchAgent()

    market_data = create_market_data()

    requirement = TaskRequirement(
        query="Analyze the selected company",
        required_capabilities=[
            "market_research"
        ],
        symbols=["TCS"],
    )

    agent.set_task_requirement(requirement)

    result = agent.execute(
        query="Analyze the selected company",
        budget=500,
        market_data=market_data,
    )

    assert result.status == AgentStatus.COMPLETED
    assert "Market Research Assessment for TCS" in result.output


def test_market_research_agent_rejects_unavailable_structured_symbol():
    agent = MarketResearchAgent()

    requirement = TaskRequirement(
        query="Analyze the selected company",
        required_capabilities=[
            "market_research"
        ],
        symbols=["INFY"],
    )

    agent.set_task_requirement(requirement)

    market_data = create_market_data()

    result = agent.execute(
        query="Analyze the selected company",
        budget=500,
        market_data=market_data,
    )

    assert result.status == AgentStatus.FAILED
    assert (
        result.failure_reason
        == "No supported symbol found in query."
    )