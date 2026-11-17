
from abc import ABC, abstractmethod
from typing import Dict, Optional

from app.models.schemas import AgentState, TaskRequirement


class BaseAgent(ABC):
    """Base class for all financial decision-support agents."""

    def __init__(
        self,
        name: str,
        reliability: float,
        estimated_cost: int,
    ) -> None:
        self.name = name
        self.reliability = reliability
        self.estimated_cost = estimated_cost

        self.analytical_quality_score: Optional[float] = None
        self.average_execution_time_seconds: Optional[float] = None
        self.execution_time_observations: int = 0
        self.capability_relevance: Dict[str, float] = {}

        self.selection_score: Optional[float] = None
        self.selection_score_breakdown: Dict[str, float] = {}

        self.task_requirement: Optional[TaskRequirement] = None

    def record_execution_time(self, elapsed_seconds: float) -> None:
        """Update the running average execution time."""

        if elapsed_seconds < 0:
            raise ValueError("Execution time cannot be negative.")

        self.execution_time_observations += 1

        if self.average_execution_time_seconds is None:
            self.average_execution_time_seconds = float(elapsed_seconds)
            return

        previous_count = self.execution_time_observations - 1
        previous_average = self.average_execution_time_seconds

        self.average_execution_time_seconds = (
            previous_average * previous_count + float(elapsed_seconds)
        ) / self.execution_time_observations

    def set_task_requirement(
        self,
        requirement: TaskRequirement,
    ) -> None:
        self.task_requirement = requirement

    def get_task_requirement(self) -> TaskRequirement:
        if self.task_requirement is None:
            raise RuntimeError(
                f"No TaskRequirement has been assigned to {self.name}."
            )

        return self.task_requirement

    @abstractmethod
    def execute(
        self,
        query: str,
        budget: int,
    ) -> AgentState:
        raise NotImplementedError
