import pandas as pd

from app.agents.investment_agent import InvestmentAgent
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
            ],
            "symbol": [
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
                106.0,
            ],
        }
    )


def test_investment_agent_uses_task_requirement_symbol():
    agent = InvestmentAgent()

    requirement = TaskRequirement(
        query="Should I invest in TCS?",
        required_capabilities=[
            "investment_analysis"
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


def test_investment_agent_reads_amount_and_horizon():
    agent = InvestmentAgent()

    requirement = TaskRequirement(
        query="I want to invest ₹5 lakh in TCS for 5 years.",
        required_capabilities=[
            "investment_analysis"
        ],
        initial_amount=500000,
        years=5,
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

    assert "₹500,000.00" in result.output
    assert "5 years" in result.output


def test_investment_agent_falls_back_to_query_symbol():
    agent = InvestmentAgent()

    market_data = create_market_data()

    result = agent.execute(
        query="Should I invest in TCS?",
        budget=900,
        market_data=market_data,
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.output is not None
    assert "TCS" in result.output