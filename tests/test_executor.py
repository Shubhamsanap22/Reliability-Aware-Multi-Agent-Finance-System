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


def test_executor_records_execution_latency(monkeypatch):
    """A successful attempt stores its measured duration and running mean."""

    import app.execution.executor as executor_module

    class SuccessfulAgent(BaseAgent):

        def __init__(self):
            super().__init__(
                name="Successful Agent",
                reliability=0.9,
                estimated_cost=500,
            )

        def execute(self, query: str, budget: int) -> AgentState:
            return AgentState(
                agent_name=self.name,
                reliability=self.reliability,
                allocated_budget=budget,
                used_budget=100,
                status=AgentStatus.COMPLETED,
            )

    timestamps = iter([10.0, 10.25])

    monkeypatch.setattr(
        executor_module,
        "perf_counter",
        lambda: next(timestamps),
    )

    executor = create_executor()
    agent = SuccessfulAgent()

    result = executor.run_agent(
        agent=agent,
        query="Test latency.",
    )

    assert result.execution_time_seconds == 0.25
    assert agent.average_execution_time_seconds == 0.25
    assert agent.execution_time_observations == 1


def test_executor_includes_failed_attempts_in_latency_average(monkeypatch):
    """Failed executions also contribute to the running average."""

    import pytest
    import app.execution.executor as executor_module

    # Three attempts: initial execution plus two retries.
    timestamps = iter([
        0.0, 0.1,
        1.0, 1.2,
        2.0, 2.3,
    ])

    monkeypatch.setattr(
        executor_module,
        "perf_counter",
        lambda: next(timestamps),
    )

    executor = create_executor()
    agent = FailingAgent()

    result = executor.run_agent(
        agent=agent,
        query="Analyze portfolio risk.",
    )

    assert result.status == AgentStatus.FAILED
    assert agent.execution_time_observations == 3

    assert agent.average_execution_time_seconds == pytest.approx(0.2)
    assert result.execution_time_seconds == pytest.approx(0.3)


def test_executor_records_latency_when_agent_raises_exception(monkeypatch):
    """An exception still produces a measured failed execution attempt."""

    import pytest
    import app.execution.executor as executor_module

    class ExceptionAgent(BaseAgent):

        def __init__(self):
            super().__init__(
                name="Exception Agent",
                reliability=0.8,
                estimated_cost=400,
            )

        def execute(self, query: str, budget: int) -> AgentState:
            raise RuntimeError("Simulated execution error.")

    # Three attempts: initial execution plus two configured retries.
    timestamps = iter([
        5.0, 5.4,
        6.0, 6.4,
        7.0, 7.4,
    ])

    monkeypatch.setattr(
        executor_module,
        "perf_counter",
        lambda: next(timestamps),
    )

    executor = create_executor()
    agent = ExceptionAgent()

    result = executor.run_agent(
        agent=agent,
        query="Test exception timing.",
    )

    assert result.status == AgentStatus.FAILED
    assert result.execution_time_seconds == pytest.approx(0.4)
    assert agent.average_execution_time_seconds == pytest.approx(0.4)
    assert agent.execution_time_observations == 3

    assert "RuntimeError" in (result.failure_reason or "")
