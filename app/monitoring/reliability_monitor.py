from app.agents.base_agent import BaseAgent
from app.models.schemas import AgentStatus


class ReliabilityMonitor:
    """Updates agent reliability based on execution outcomes."""

    def __init__(self, learning_rate: float = 0.05) -> None:
        self.learning_rate = learning_rate

    def update(self, agent: BaseAgent, status: AgentStatus) -> float:
        """Update and return the agent's new reliability."""

        if status == AgentStatus.COMPLETED:
            agent.reliability += self.learning_rate

        elif status == AgentStatus.FAILED:
            agent.reliability -= self.learning_rate

        else:
            raise ValueError(
                f"Unsupported agent status: {status}"
            )

        agent.reliability = max(
            0.0,
            min(1.0, agent.reliability),
        )

        return agent.reliability