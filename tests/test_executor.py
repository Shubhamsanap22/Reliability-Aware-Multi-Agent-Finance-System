from app.agents.base_agent import BaseAgent
from app.models.schemas import AgentState, AgentStatus
from app.budget.budget_manager import BudgetManager
from app.execution.executor import Executor
from app.handling.failure_handler import FailureHandler
from app.agents.investment_agent import InvestmentAgent


class FailingAgent(BaseAgent):
    """Test agent that always fails."""

    def __init__(self):
        super().__init__(
            name="Failing Agent",
            reliability=0.50,
            estimated_cost=900,
        )

    def execute(
        self,
        query: str,
        budget: int,
    ) -> AgentState:

        return AgentState(
            agent_name=self.name,
            reliability=self.reliability,
            allocated_budget=budget,
            used_budget=100,
            status=AgentStatus.FAILED,
            failure_reason="Test failure.",
        )


def create_executor():
    budget_manager = BudgetManager(
        global_budget=5000
    )

    failure_handler = FailureHandler()

    return Executor(
        budget_manager=budget_manager,
        failure_handler=failure_handler,
    )


def test_executor_tracks_actual_usage():

    executor = create_executor()

    agent = InvestmentAgent()

    result = executor.run_agent(
        agent=agent,
        query="Analyze investment opportunities for TCS.",
    )

    assert result.status == AgentStatus.COMPLETED

    assert result.used_budget == 600

    assert (
        executor.budget_manager.state.used_budget
        == 600
    )


def test_executor_retries_failed_agent():

    executor = create_executor()

    agent = FailingAgent()

    result = executor.run_agent(
        agent=agent,
        query="Analyze portfolio risk.",
    )

    assert result.status == AgentStatus.FAILED

    assert (
        result.failure_reason
        == "Test failure."
    )


def test_executor_stops_after_retry_limit():

    failure_handler = FailureHandler(
        max_retries=2
    )

    budget_manager = BudgetManager(
        global_budget=5000
    )

    executor = Executor(
        budget_manager=budget_manager,
        failure_handler=failure_handler,
    )

    agent = FailingAgent()

    result = executor.run_agent(
        agent=agent,
        query="Analyze portfolio risk.",
    )

    assert result.status == AgentStatus.FAILED

    assert (
        failure_handler.retry_count
        == 2
    )


def test_executor_uses_fallback_agent():

    executor = create_executor()

    failing_agent = FailingAgent()

    fallback_agent = InvestmentAgent()

    result = executor.run_agent(
        agent=failing_agent,
        query="Analyze investment opportunities for TCS.",
        fallback_agents=[fallback_agent],
    )

    assert result.status == AgentStatus.COMPLETED

    assert result.agent_name == "Investment Agent"

    assert result.used_budget == 600