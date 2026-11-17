
import logging
from time import perf_counter
from typing import List, Optional
from uuid import uuid4

from app.agents.base_agent import BaseAgent
from app.budget.budget_manager import BudgetManager
from app.execution.history_store import ExecutionHistoryStore
from app.handling.failure_handler import FailureHandler
from app.models.schemas import AgentState, AgentStatus, TaskRequirement


logger = logging.getLogger(__name__)


class Executor:
    """Execute agents while tracking budgets, latency, and failures."""

    def __init__(
        self,
        budget_manager: BudgetManager,
        failure_handler: FailureHandler,
        history_store: Optional[ExecutionHistoryStore] = None,
    ) -> None:
        self.budget_manager = budget_manager
        self.failure_handler = failure_handler
        self.history_store = history_store

    def _record_history(
        self,
        result: AgentState,
        run_id: str,
        attempt_number: int,
        requirement: Optional[TaskRequirement],
        is_fallback: bool,
        execution_started: bool,
    ) -> None:
        """Persist one execution attempt when history storage is enabled."""

        if self.history_store is None:
            return

        capabilities = None

        if requirement is not None:
            capabilities = ",".join(
                requirement.required_capabilities
            )

        try:
            status = (
                result.status.value
                if isinstance(result.status, AgentStatus)
                else str(result.status)
            )

            self.history_store.record_attempt(
                run_id=run_id,
                agent_name=result.agent_name,
                capabilities=capabilities,
                attempt_number=attempt_number,
                is_fallback=is_fallback,
                execution_started=execution_started,
                execution_time_seconds=result.execution_time_seconds,
                status=status,
                reliability=result.reliability,
                allocated_budget=result.allocated_budget,
                used_budget=result.used_budget,
                failure_reason=result.failure_reason,
            )

        except Exception:
            logger.exception(
                "Could not persist execution history for agent %s",
                result.agent_name,
            )

    def _execute_once(
        self,
        agent: BaseAgent,
        query: str,
        requirement: Optional[TaskRequirement] = None,
        run_id: Optional[str] = None,
        attempt_number: int = 1,
        is_fallback: bool = False,
    ) -> AgentState:
        """Execute one attempt and record usage and execution time."""

        if requirement is not None:
            agent.set_task_requirement(requirement)

        if not self.budget_manager.can_afford(agent.estimated_cost):

            result = AgentState(
                agent_name=agent.name,
                reliability=agent.reliability,
                allocated_budget=0,
                used_budget=0,
                status=AgentStatus.FAILED,
                failure_reason=(
                    f"Insufficient global budget for {agent.name}: "
                    f"requires {agent.estimated_cost}, remaining "
                    f"{self.budget_manager.remaining_budget}."
                ),
                execution_time_seconds=None,
            )

            self._record_history(
                result=result,
                run_id=run_id or str(uuid4()),
                attempt_number=attempt_number,
                requirement=requirement,
                is_fallback=is_fallback,
                execution_started=False,
            )

            return result

        self.budget_manager.allocate(agent.estimated_cost)

        start_time = perf_counter()

        try:
            result = agent.execute(
                query=query,
                budget=agent.estimated_cost,
            )

        except Exception as error:

            elapsed_seconds = perf_counter() - start_time

            agent.record_execution_time(elapsed_seconds)

            self.budget_manager.record_usage(0)

            result = AgentState(
                agent_name=agent.name,
                reliability=agent.reliability,
                allocated_budget=agent.estimated_cost,
                used_budget=0,
                status=AgentStatus.FAILED,
                failure_reason=(
                    f"Unhandled exception in {agent.name}: "
                    f"{type(error).__name__}: {error}"
                ),
                execution_time_seconds=elapsed_seconds,
            )

            self._record_history(
                result=result,
                run_id=run_id or str(uuid4()),
                attempt_number=attempt_number,
                requirement=requirement,
                is_fallback=is_fallback,
                execution_started=True,
            )

            return result

        elapsed_seconds = perf_counter() - start_time

        agent.record_execution_time(elapsed_seconds)

        result.execution_time_seconds = elapsed_seconds

        used = max(0, int(result.used_budget))

        self.budget_manager.record_usage(used)

        self._record_history(
            result=result,
            run_id=run_id or str(uuid4()),
            attempt_number=attempt_number,
            requirement=requirement,
            is_fallback=is_fallback,
            execution_started=True,
        )

        return result

    def run_agent(
        self,
        agent: BaseAgent,
        query: str,
        fallback_agents: Optional[List[BaseAgent]] = None,
        requirement: Optional[TaskRequirement] = None,
    ) -> AgentState:
        """Run an agent, retry failures, and optionally use a fallback."""

        self.failure_handler.reset()

        run_id = str(uuid4())
        attempt_number = 1

        result = self._execute_once(
            agent=agent,
            query=query,
            requirement=requirement,
            run_id=run_id,
            attempt_number=attempt_number,
        )

        while (
            result.status == AgentStatus.FAILED
            and not (
                result.failure_reason or ""
            ).startswith("Insufficient global budget")
            and self.failure_handler.can_retry()
        ):
            self.failure_handler.record_retry()
            attempt_number += 1

            result = self._execute_once(
                agent=agent,
                query=query,
                requirement=requirement,
                run_id=run_id,
                attempt_number=attempt_number,
            )

        if result.status == AgentStatus.FAILED and fallback_agents:

            fallback = self.failure_handler.select_fallback(
                failed_agent=agent,
                available_agents=fallback_agents,
            )

            if fallback is not None:
                attempt_number += 1

                result = self._execute_once(
                    agent=fallback,
                    query=query,
                    requirement=requirement,
                    run_id=run_id,
                    attempt_number=attempt_number,
                    is_fallback=True,
                )

        return result

    def run_agents(
        self,
        agents: List[BaseAgent],
        query: str,
        requirement: Optional[TaskRequirement] = None,
    ) -> List[AgentState]:
        """Execute multiple agents sequentially."""

        return [
            self.run_agent(
                agent=agent,
                query=query,
                requirement=requirement,
            )
            for agent in agents
        ]

    def run_agents_with_fallback(
        self,
        agents: List[BaseAgent],
        query: str,
        requirement: Optional[TaskRequirement] = None,
    ) -> List[AgentState]:
        """
        Execute selected specialists with retry support.

        Different financial specializations are not interchangeable.
        Therefore, this method does not automatically replace one
        specialization with another.
        """

        results: List[AgentState] = []

        for agent in agents:
            result = self.run_agent(
                agent=agent,
                query=query,
                fallback_agents=None,
                requirement=requirement,
            )

            results.append(result)

        return results
