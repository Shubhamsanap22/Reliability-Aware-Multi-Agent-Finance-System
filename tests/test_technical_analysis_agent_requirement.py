import pandas as pd

from app.agents.technical_analysis_agent import TechnicalAnalysisAgent
from app.models.schemas import AgentStatus, TaskRequirement


def create_market_data():
    periods = 30

    return pd.DataFrame(
        {
            "date": pd.date_range(
                "2026-01-01",
                periods=periods,
            ),
            "symbol": ["TCS"] * periods,
            "close": [
                100 + i
                for i in range(periods)
            ],
        }
    )


def test_technical_agent_uses_task_requirement_symbol():
    agent = TechnicalAnalysisAgent()

    requirement = TaskRequirement(
        query="Analyze the selected company",
        required_capabilities=[
            "technical_analysis"
        ],
        symbols=["TCS"],
    )

    agent.set_task_requirement(requirement)

    result = agent.execute(
        query="Analyze the selected company",
        budget=600,
        market_data=create_market_data(),
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.agent_name == "Technical Analysis Agent"
    assert result.output is not None
    assert "TCS" in result.output


def test_technical_agent_prefers_structured_symbol():
    agent = TechnicalAnalysisAgent()

    requirement = TaskRequirement(
        query="Analyze the selected stock",
        required_capabilities=[
            "technical_analysis"
        ],
        symbols=["TCS"],
    )

    agent.set_task_requirement(requirement)

    result = agent.execute(
        query="Analyze the selected stock",
        budget=600,
        market_data=create_market_data(),
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.output is not None
    assert "Technical Analysis Assessment for TCS" in result.output


def test_technical_agent_falls_back_to_query_symbol():
    agent = TechnicalAnalysisAgent()

    result = agent.execute(
        query="Analyze TCS technical indicators",
        budget=600,
        market_data=create_market_data(),
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.output is not None
    assert "TCS" in result.output


def test_technical_agent_uses_matching_structured_symbol():
    agent = TechnicalAnalysisAgent()

    market_data = create_market_data()

    requirement = TaskRequirement(
        query="Analyze the selected company",
        required_capabilities=[
            "technical_analysis"
        ],
        symbols=["TCS"],
    )

    agent.set_task_requirement(requirement)

    result = agent.execute(
        query="Analyze the selected company",
        budget=600,
        market_data=market_data,
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.output is not None
    assert "Technical Analysis Assessment for TCS" in result.output


def test_technical_agent_rejects_unavailable_structured_symbol():
    agent = TechnicalAnalysisAgent()

    requirement = TaskRequirement(
        query="Analyze the selected company",
        required_capabilities=[
            "technical_analysis"
        ],
        symbols=["INFY"],
    )

    agent.set_task_requirement(requirement)

    market_data = create_market_data()

    result = agent.execute(
        query="Analyze the selected company",
        budget=600,
        market_data=market_data,
    )

    assert result.status == AgentStatus.FAILED
    assert (
        result.failure_reason
        == "No supported symbol found in query."
    )