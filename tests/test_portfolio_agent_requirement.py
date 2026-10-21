import pandas as pd

from app.agents.portfolio_agent import PortfolioAgent
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
            ]
            * 2,
            "symbol": (
                ["TCS"] * 6
                + ["INFY"] * 6
            ),
            "close": [
                100.0,
                102.0,
                101.0,
                104.0,
                103.0,
                105.0,
                200.0,
                202.0,
                201.0,
                204.0,
                203.0,
                205.0,
            ],
        }
    )


def test_portfolio_agent_uses_task_requirement_symbols():
    agent = PortfolioAgent()

    requirement = TaskRequirement(
        query=(
            "Build a portfolio using TCS and INFY."
        ),
        required_capabilities=[
            "portfolio_management"
        ],
        symbols=["TCS", "INFY"],
    )

    agent.set_task_requirement(requirement)

    market_data = create_market_data()

    result = agent.execute(
        query=requirement.query,
        budget=700,
        market_data=market_data,
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.output is not None
    assert "TCS" in result.output
    assert "INFY" in result.output


def test_portfolio_agent_uses_multiple_structured_symbols():
    agent = PortfolioAgent()

    requirement = TaskRequirement(
        query=(
            "Create a diversified portfolio "
            "with TCS and INFY."
        ),
        required_capabilities=[
            "portfolio_management"
        ],
        symbols=["TCS", "INFY"],
    )

    agent.set_task_requirement(requirement)

    symbols = agent._get_symbols(
        requirement.query
    )

    assert symbols == ["TCS", "INFY"]


def test_portfolio_agent_falls_back_to_query_symbols():
    agent = PortfolioAgent()

    market_data = create_market_data()

    result = agent.execute(
        query=(
            "Build a portfolio using TCS and INFY."
        ),
        budget=700,
        market_data=market_data,
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.output is not None
    assert "TCS" in result.output
    assert "INFY" in result.output