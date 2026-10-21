from typing import List, Optional

from app.agents.base_agent import BaseAgent
from app.budget.budget_manager import BudgetManager
from app.handling.failure_handler import FailureHandler
from app.models.schemas import AgentState, AgentStatus, TaskRequirement


class Executor:
    """Execute agents while tracking budgets and handling failures."""

    def __init__(
        self,
        budget_manager: BudgetManager,
        failure_handler: FailureHandler,
    ) -> None:
        self.budget_manager = budget_manager
        self.failure_handler = failure_handler

    def _execute_once(
        self,
        agent: BaseAgent,
        query: str,
        requirement: Optional[TaskRequirement] = None,
    ) -> AgentState:
        """Execute one agent attempt and record its usage."""
        if requirement is not None:
            agent.set_task_requirement(requirement)

        if not self.budget_manager.can_afford(agent.estimated_cost):
            return AgentState(
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
            )

        self.budget_manager.allocate(agent.estimated_cost)

        try:
            result = agent.execute(
                query=query,
                budget=agent.estimated_cost,
            )
        except Exception as error:
            # Exceptions must not be reported as successful execution.
            self.budget_manager.record_usage(0)

            return AgentState(
                agent_name=agent.name,
                reliability=agent.reliability,
                allocated_budget=agent.estimated_cost,
                used_budget=0,
                status=AgentStatus.FAILED,
                failure_reason=(
                    f"Unhandled exception in {agent.name}: "
                    f"{type(error).__name__}: {error}"
                ),
            )

        used = max(0, int(result.used_budget))
        self.budget_manager.record_usage(used)

        return result

    def run_agent(
        self,
        agent: BaseAgent,
        query: str,
        fallback_agents: Optional[List[BaseAgent]] = None,
        requirement: Optional[TaskRequirement] = None,
    ) -> AgentState:
        """Run an agent, retry eligible failures, and optionally fall back."""
        self.failure_handler.reset()

        result = self._execute_once(
            agent=agent,
            query=query,
            requirement=requirement,
        )

        while (
            result.status == AgentStatus.FAILED
            and not (
                result.failure_reason or ""
            ).startswith("Insufficient global budget")
            and self.failure_handler.can_retry()
        ):
            self.failure_handler.record_retry()

            result = self._execute_once(
                agent=agent,
                query=query,
                requirement=requirement,
            )

        if result.status == AgentStatus.FAILED and fallback_agents:
            fallback = self.failure_handler.select_fallback(
                failed_agent=agent,
                available_agents=fallback_agents,
            )

            if fallback is not None:
                result = self._execute_once(
                    agent=fallback,
                    query=query,
                    requirement=requirement,
                )

        return result

    def run_agents(
        self,
        agents: List[BaseAgent],
        query: str,
        requirement: Optional[TaskRequirement] = None,
    ) -> List[AgentState]:
        """Execute the supplied agents sequentially."""
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
        This method therefore does not automatically replace one agent
        with another specialization.
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