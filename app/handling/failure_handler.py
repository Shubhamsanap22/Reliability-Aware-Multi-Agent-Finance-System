from typing import List, Optional

from app.agents.base_agent import BaseAgent


class FailureHandler:
    """Handles retries and fallback agent selection."""

    def __init__(self, max_retries: int = 2) -> None:
        if max_retries < 0:
            raise ValueError("max_retries cannot be negative.")

        self.max_retries = max_retries
        self.retry_count = 0

    def should_retry(self, retry_count: int) -> bool:
        """Check whether another retry is allowed."""

        if retry_count < 0:
            raise ValueError("retry_count cannot be negative.")

        return retry_count < self.max_retries

    def can_retry(self) -> bool:
        """Check whether another retry is allowed using internal count."""

        return self.should_retry(self.retry_count)

    def record_retry(self) -> None:
        """Record one retry attempt."""

        self.retry_count += 1

    def reset(self) -> None:
        """Reset retry tracking."""

        self.retry_count = 0

    def select_fallback(
        self,
        failed_agent: BaseAgent,
        available_agents: List[BaseAgent],
    ) -> Optional[BaseAgent]:
        """Select the most reliable agent other than the failed agent."""

        candidates = [
            agent
            for agent in available_agents
            if agent.name != failed_agent.name
        ]

        if not candidates:
            return None

        return max(
            candidates,
            key=lambda agent: agent.reliability,
        )

    def select_fallback_agent(
        self,
        agents: List[BaseAgent],
    ) -> Optional[BaseAgent]:
        """Compatibility method for selecting the most reliable agent."""

        if not agents:
            return None

        return max(
            agents,
            key=lambda agent: agent.reliability,
        )