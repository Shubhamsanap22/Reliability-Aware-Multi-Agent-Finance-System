import pandas as pd

from app.agents.fundamental_analysis_agent import FundamentalAnalysisAgent
from app.models.schemas import AgentStatus, TaskRequirement


def create_fundamental_data():
    return pd.DataFrame(
        {
            "period": [
                "2024",
                "2025",
                "2026",
            ],
            "symbol": [
                "TCS",
                "TCS",
                "TCS",
            ],
            "revenue": [
                1000,
                1100,
                1250,
            ],
            "net_income": [
                150,
                170,
                200,
            ],
            "eps": [
                10,
                11,
                13,
            ],
            "price": [
                3000,
                3200,
                3500,
            ],
        }
    )


def test_fundamental_agent_uses_task_requirement_symbol():
    agent = FundamentalAnalysisAgent()

    requirement = TaskRequirement(
        query="Analyze the selected company",
        required_capabilities=[
            "fundamental_analysis"
        ],
        symbols=["TCS"],
    )

    agent.set_task_requirement(requirement)

    result = agent.execute(
        query="Analyze the selected company",
        budget=600,
        fundamental_data=create_fundamental_data(),
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.agent_name == "Fundamental Analysis Agent"
    assert result.output is not None
    assert "TCS" in result.output


def test_fundamental_agent_prefers_structured_symbol():
    agent = FundamentalAnalysisAgent()

    requirement = TaskRequirement(
        query="Analyze the selected stock",
        required_capabilities=[
            "fundamental_analysis"
        ],
        symbols=["TCS"],
    )

    agent.set_task_requirement(requirement)

    result = agent.execute(
        query="Analyze the selected stock",
        budget=600,
        fundamental_data=create_fundamental_data(),
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.output is not None
    assert "Fundamental Analysis Assessment for TCS" in result.output


def test_fundamental_agent_falls_back_to_query_symbol():
    agent = FundamentalAnalysisAgent()

    result = agent.execute(
        query="Analyze TCS fundamentals",
        budget=600,
        fundamental_data=create_fundamental_data(),
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.output is not None
    assert "TCS" in result.output


def test_fundamental_agent_uses_matching_structured_symbol():
    agent = FundamentalAnalysisAgent()

    fundamental_data = create_fundamental_data()

    requirement = TaskRequirement(
        query="Analyze the selected company",
        required_capabilities=[
            "fundamental_analysis"
        ],
        symbols=["TCS"],
    )

    agent.set_task_requirement(requirement)

    result = agent.execute(
        query="Analyze the selected company",
        budget=600,
        fundamental_data=fundamental_data,
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.output is not None
    assert "Fundamental Analysis Assessment for TCS" in result.output


def test_fundamental_agent_rejects_unavailable_structured_symbol():
    agent = FundamentalAnalysisAgent()

    requirement = TaskRequirement(
        query="Analyze the selected company",
        required_capabilities=[
            "fundamental_analysis"
        ],
        symbols=["INFY"],
    )

    agent.set_task_requirement(requirement)

    fundamental_data = create_fundamental_data()

    result = agent.execute(
        query="Analyze the selected company",
        budget=600,
        fundamental_data=fundamental_data,
    )

    assert result.status == AgentStatus.FAILED
    assert (
        result.failure_reason
        == "No supported symbol found in query."
    )