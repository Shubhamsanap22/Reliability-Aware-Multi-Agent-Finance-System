from unittest.mock import MagicMock

from app.models.schemas import (
    AgentState,
    AgentStatus,
    TaskRequirement,
)
from app.execution.executor import Executor


def create_mock_agent():
    """Create a mock agent with the required BaseAgent attributes."""

    agent = MagicMock()

    agent.name = "InvestmentAgent"
    agent.reliability = 0.8
    agent.estimated_cost = 10

    agent.execute.return_value = AgentState(
        agent_name="InvestmentAgent",
        reliability=0.8,
        allocated_budget=10,
        used_budget=5,
        status=AgentStatus.COMPLETED,
        output="Investment analysis completed.",
    )

    return agent


def create_executor():
    """Create an Executor with mocked dependencies."""

    budget_manager = MagicMock()

    budget_manager.can_afford.return_value = True

    failure_handler = MagicMock()

    failure_handler.can_retry.return_value = False

    executor = Executor(
        budget_manager=budget_manager,
        failure_handler=failure_handler,
    )

    return executor


def test_executor_passes_task_requirement_to_agent():
    executor = create_executor()
    agent = create_mock_agent()

    requirement = TaskRequirement(
        query="Should I invest in TCS?",
        required_capabilities=[
            "investment_analysis"
        ],
        symbols=["TCS"],
    )

    result = executor.run_agent(
        agent=agent,
        query=requirement.query,
        requirement=requirement,
    )

    agent.set_task_requirement.assert_called_once_with(
        requirement
    )

    assert result.status == AgentStatus.COMPLETED


def test_executor_preserves_query_execution():
    executor = create_executor()
    agent = create_mock_agent()

    requirement = TaskRequirement(
        query="What is the risk of TCS?",
        required_capabilities=[
            "risk_analysis"
        ],
        symbols=["TCS"],
    )

    executor.run_agent(
        agent=agent,
        query=requirement.query,
        requirement=requirement,
    )

    agent.execute.assert_called_once_with(
        query="What is the risk of TCS?",
        budget=10,
    )

def test_agent_receives_structured_information():
    executor = create_executor()
    agent = create_mock_agent()

    requirement = TaskRequirement(
        query="I want to invest ₹5 lakh in TCS for 5 years.",
        required_capabilities=[
            "investment_analysis"
        ],
        initial_amount=500000,
        years=5,
        symbols=["TCS"],
    )

    executor.run_agent(
        agent=agent,
        query=requirement.query,
        requirement=requirement,
    )

    agent.set_task_requirement.assert_called_once()

    stored_requirement = (
        agent.set_task_requirement.call_args.args[0]
    )

    assert stored_requirement.symbols == ["TCS"]
    assert stored_requirement.initial_amount == 500000
    assert stored_requirement.years == 5