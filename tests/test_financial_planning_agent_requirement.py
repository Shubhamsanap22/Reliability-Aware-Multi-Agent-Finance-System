from app.agents.financial_planning_agent import (
    FinancialPlanningAgent,
)
from app.models.schemas import AgentStatus, TaskRequirement


def test_financial_planning_agent_uses_task_requirement_values():
    agent = FinancialPlanningAgent()

    requirement = TaskRequirement(
        query="Plan investment for a financial goal",
        required_capabilities=[
            "financial_planning"
        ],
        initial_amount=100000,
        target_amount=200000,
        years=5,
        annual_return=0.12,
        risk_preference="moderate",
    )

    agent.set_task_requirement(requirement)

    result = agent.execute(
        query="Plan investment for a financial goal",
        budget=600,
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.agent_name == "Financial Planning Agent"
    assert result.output is not None

    assert "₹100,000.00" in result.output
    assert "₹200,000.00" in result.output
    assert "5 years" in result.output
    assert "Moderate" in result.output


def test_financial_planning_agent_uses_structured_risk_preference():
    agent = FinancialPlanningAgent()

    requirement = TaskRequirement(
        query="Create a financial plan",
        required_capabilities=[
            "financial_planning"
        ],
        initial_amount=50000,
        target_amount=100000,
        years=5,
        risk_preference="low",
    )

    agent.set_task_requirement(requirement)

    result = agent.execute(
        query="Create a financial plan",
        budget=600,
        risk_level="high",
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.output is not None
    assert "Risk level: Low" in result.output


def test_financial_planning_agent_uses_structured_annual_return():
    agent = FinancialPlanningAgent()

    requirement = TaskRequirement(
        query="Plan my investment",
        required_capabilities=[
            "financial_planning"
        ],
        initial_amount=100000,
        target_amount=200000,
        years=5,
        annual_return=0.10,
    )

    agent.set_task_requirement(requirement)

    result = agent.execute(
        query="Plan my investment",
        budget=600,
        annual_return=0.20,
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.output is not None
    assert "Expected annual return: 10.00%" in result.output


def test_financial_planning_agent_requires_structured_values():
    agent = FinancialPlanningAgent()

    requirement = TaskRequirement(
        query="Create a financial plan",
        required_capabilities=[
            "financial_planning"
        ],
    )

    agent.set_task_requirement(requirement)

    result = agent.execute(
        query="Create a financial plan",
        budget=600,
    )

    assert result.status == AgentStatus.FAILED
    assert result.failure_reason == (
        "Initial investment amount is required."
    )


def test_financial_planning_agent_preserves_direct_arguments():
    agent = FinancialPlanningAgent()

    result = agent.execute(
        query="Create a financial plan",
        budget=600,
        initial_amount=100000,
        target_amount=200000,
        years=5,
        annual_return=0.10,
        risk_level="moderate",
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.output is not None

    assert "₹100,000.00" in result.output
    assert "₹200,000.00" in result.output
    assert "5 years" in result.output
    