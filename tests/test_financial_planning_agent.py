from app.agents.financial_planning_agent import (
    FinancialPlanningAgent,
)
from app.models.schemas import AgentStatus


def test_financial_planning_agent_completes():
    agent = FinancialPlanningAgent()

    result = agent.execute(
        query="Plan my investment.",
        budget=1000,
        initial_amount=500000,
        target_amount=1000000,
        years=5,
        risk_level="moderate",
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.used_budget == 500
    assert "Financial Planning Assessment" in result.output


def test_financial_planning_agent_with_expected_return():
    agent = FinancialPlanningAgent()

    result = agent.execute(
        query="Plan my investment.",
        budget=1000,
        initial_amount=500000,
        target_amount=1000000,
        annual_return=0.10,
        years=5,
        risk_level="moderate",
    )

    assert result.status == AgentStatus.COMPLETED
    assert "Expected Return Scenario" in result.output
    assert "Projected future value" in result.output


def test_financial_planning_agent_rejects_low_budget():
    agent = FinancialPlanningAgent()

    result = agent.execute(
        query="Plan my investment.",
        budget=400,
        initial_amount=500000,
        target_amount=1000000,
        years=5,
    )

    assert result.status == AgentStatus.FAILED
    assert result.failure_reason == "Insufficient budget."


def test_financial_planning_agent_requires_initial_amount():
    agent = FinancialPlanningAgent()

    result = agent.execute(
        query="Plan my investment.",
        budget=1000,
        target_amount=1000000,
        years=5,
    )

    assert result.status == AgentStatus.FAILED
    assert "Initial investment amount" in result.failure_reason


def test_financial_planning_agent_requires_target():
    agent = FinancialPlanningAgent()

    result = agent.execute(
        query="Plan my investment.",
        budget=1000,
        initial_amount=500000,
        years=5,
    )

    assert result.status == AgentStatus.FAILED
    assert "Target amount" in result.failure_reason


def test_financial_planning_agent_requires_time_horizon():
    agent = FinancialPlanningAgent()

    result = agent.execute(
        query="Plan my investment.",
        budget=1000,
        initial_amount=500000,
        target_amount=1000000,
    )

    assert result.status == AgentStatus.FAILED
    assert "time horizon" in result.failure_reason.lower()


def test_financial_planning_agent_rejects_invalid_risk():
    agent = FinancialPlanningAgent()

    result = agent.execute(
        query="Plan my investment.",
        budget=1000,
        initial_amount=500000,
        target_amount=1000000,
        years=5,
        risk_level="extreme",
    )

    assert result.status == AgentStatus.FAILED
    assert "Risk level" in result.failure_reason


def test_financial_planning_agent_has_expected_reliability():
    agent = FinancialPlanningAgent()

    assert agent.reliability == 0.90