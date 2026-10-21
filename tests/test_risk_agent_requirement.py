import pandas as pd

from app.agents.risk_agent import RiskAgent
from app.models.schemas import (
    AgentStatus,
    TaskRequirement,
)


def create_market_data():
    return pd.DataFrame(
        {
            "date": [
                "2026-01-01",
                "2026-01-02",
                "2026-01-03",
                "2026-01-04",
                "2026-01-05",
                "2026-01-06",
            ],
            "symbol": [
                "TCS",
                "TCS",
                "TCS",
                "TCS",
                "TCS",
                "TCS",
            ],
            "close": [
                100.0,
                102.0,
                101.0,
                104.0,
                103.0,
                105.0,
            ],
        }
    )


def test_risk_agent_uses_task_requirement_symbol():
    agent = RiskAgent()

    requirement = TaskRequirement(
        query="What is the risk of investing in TCS?",
        required_capabilities=[
            "risk_analysis"
        ],
        symbols=["TCS"],
    )

    agent.set_task_requirement(requirement)

    market_data = create_market_data()

    result = agent.execute(
        query=requirement.query,
        budget=900,
        market_data=market_data,
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.output is not None
    assert "TCS" in result.output
    assert "Risk Assessment" in result.output


def test_risk_agent_reads_risk_preference():
    agent = RiskAgent()

    requirement = TaskRequirement(
        query="What is the risk of TCS for a moderate risk investor?",
        required_capabilities=[
            "risk_analysis"
        ],
        risk_preference="moderate",
        symbols=["TCS"],
    )

    agent.set_task_requirement(requirement)

    market_data = create_market_data()

    result = agent.execute(
        query=requirement.query,
        budget=900,
        market_data=market_data,
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.output is not None
    assert "moderate" in result.output


def test_risk_agent_falls_back_to_query_symbol():
    agent = RiskAgent()

    market_data = create_market_data()

    result = agent.execute(
        query="What is the risk of TCS?",
        budget=900,
        market_data=market_data,
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.output is not None
    assert "TCS" in result.output