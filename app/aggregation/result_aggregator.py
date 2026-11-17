
"""Aggregate multi-agent execution results without inventing financial facts."""

from dataclasses import dataclass
from typing import Iterable

from app.models.schemas import AgentState, AgentStatus


@dataclass(frozen=True)
class AgentFinding:
    """A completed agent output retained as a traceable finding."""

    agent_name: str
    output: str
    reliability: float


@dataclass(frozen=True)
class AggregatedResult:
    """Summary of execution statuses, findings, limitations, and budgets."""

    overall_status: str
    total_agents: int
    completed_agents: int
    failed_agents: int
    incomplete_agents: int
    findings: tuple[AgentFinding, ...]
    limitations: tuple[str, ...]
    allocated_budget: int
    used_budget: int

    @property
    def executive_summary(self) -> str:
        if self.total_agents == 0:
            return "No agents were selected, so no analysis was produced."

        if self.overall_status == "completed":
            return (
                f"All {self.total_agents} selected agent(s) completed. "
                f"{len(self.findings)} agent output(s) are available for review."
            )

        if self.overall_status == "partially_completed":
            return (
                f"Analysis is partial: {self.completed_agents} of "
                f"{self.total_agents} selected agent(s) completed. "
                "Review the limitations before relying on these findings."
            )

        return (
            f"No agent completed successfully out of {self.total_agents} "
            "selected. The system does not have a completed analysis to present."
        )


class ResultAggregator:
    """Build a traceable summary from AgentState objects."""

    def aggregate(self, results: Iterable[AgentState]) -> AggregatedResult:
        states = tuple(results)

        completed = tuple(
            result for result in states
            if result.status == AgentStatus.COMPLETED
        )
        failed = tuple(
            result for result in states
            if result.status == AgentStatus.FAILED
        )
        incomplete = tuple(
            result for result in states
            if result.status not in (
                AgentStatus.COMPLETED,
                AgentStatus.FAILED,
            )
        )

        if not states:
            overall_status = "no_results"
        elif len(completed) == len(states):
            overall_status = "completed"
        elif completed:
            overall_status = "partially_completed"
        else:
            overall_status = "failed"

        findings = tuple(
            AgentFinding(
                agent_name=result.agent_name,
                output=result.output.strip(),
                reliability=result.reliability,
            )
            for result in completed
            if isinstance(result.output, str) and result.output.strip()
        )

        limitations = []

        for result in failed:
            reason = (
                result.failure_reason
                or "No failure reason was provided."
            )
            limitations.append(
                f"{result.agent_name} failed: {reason}"
            )

        for result in incomplete:
            limitations.append(
                f"{result.agent_name} has non-final status: "
                f"{result.status.value}."
            )

        for result in completed:
            if not (
                isinstance(result.output, str)
                and result.output.strip()
            ):
                limitations.append(
                    f"{result.agent_name} completed but returned no output."
                )

        return AggregatedResult(
            overall_status=overall_status,
            total_agents=len(states),
            completed_agents=len(completed),
            failed_agents=len(failed),
            incomplete_agents=len(incomplete),
            findings=findings,
            limitations=tuple(limitations),
            allocated_budget=sum(
                result.allocated_budget for result in states
            ),
            used_budget=sum(
                result.used_budget for result in states
            ),
        )
