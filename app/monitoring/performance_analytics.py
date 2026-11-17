
from statistics import mean
from typing import Any, Dict, List, Optional

from app.execution.history_store import ExecutionHistoryStore


class AgentPerformanceAnalytics:
    """
    Calculates empirical agent performance metrics
    using persistent SQLite execution history.

    This module is observational. It does not modify
    agent reliability or selection decisions.
    """

    SUCCESS_STATUSES = {"completed", "success", "successful"}

    FAILURE_STATUSES = {"failed", "failure", "error"}

    def __init__(
        self,
        history_store: ExecutionHistoryStore,
        minimum_samples: int = 5,
    ):
        if minimum_samples < 1:
            raise ValueError("minimum_samples must be at least 1")

        self.history_store = history_store
        self.minimum_samples = minimum_samples

    def get_agent_metrics(
        self,
        agent_name: str,
    ) -> Dict[str, Any]:
        """Calculate performance metrics for one agent."""

        records = self.history_store.get_agent_records(agent_name)

        executed_records = [
            record
            for record in records
            if bool(record["execution_started"])
        ]

        successful_records = [
            record
            for record in executed_records
            if str(record["status"]).lower() in self.SUCCESS_STATUSES
        ]

        failed_records = [
            record
            for record in executed_records
            if str(record["status"]).lower() in self.FAILURE_STATUSES
        ]

        budget_rejections = [
            record
            for record in records
            if str(record["status"]).lower() == "budget_rejected"
        ]

        execution_times = [
            float(record["execution_time_seconds"])
            for record in executed_records
            if record["execution_time_seconds"] is not None
        ]

        budget_values = [
            float(record["used_budget"])
            for record in executed_records
            if record["used_budget"] is not None
        ]

        execution_count = len(executed_records)
        successful_count = len(successful_records)

        success_rate: Optional[float] = None

        if execution_count > 0:
            success_rate = (
                successful_count / execution_count
            ) * 100

        fallback_count = sum(
            1
            for record in records
            if bool(record["is_fallback"])
        )

        latest_timestamp = (
            records[-1]["timestamp"]
            if records
            else None
        )

        return {
            "agent_name": agent_name,
            "total_attempts": len(records),
            "execution_count": execution_count,
            "successful_executions": successful_count,
            "failed_executions": len(failed_records),
            "budget_rejections": len(budget_rejections),
            "fallback_count": fallback_count,
            "success_rate_percent": success_rate,
            "average_execution_time_seconds": (
                mean(execution_times)
                if execution_times
                else None
            ),
            "average_budget_used": (
                mean(budget_values)
                if budget_values
                else None
            ),
            "sample_count": execution_count,
            "minimum_samples_required": self.minimum_samples,
            "sufficient_samples": (
                execution_count >= self.minimum_samples
            ),
            "latest_execution": latest_timestamp,
        }

    def get_all_agent_metrics(self) -> List[Dict[str, Any]]:
        """Calculate metrics for every agent in history."""

        records = self.history_store.get_all_records()

        agent_names = sorted({
            record["agent_name"]
            for record in records
        })

        return [
            self.get_agent_metrics(agent_name)
            for agent_name in agent_names
        ]

    def get_ranked_agents(self) -> List[Dict[str, Any]]:
        """
        Return agents with sufficient execution samples,
        ordered by historical success rate.

        This is a descriptive ranking, not a guarantee
        of future agent performance.
        """

        metrics = self.get_all_agent_metrics()

        eligible_agents = [
            item
            for item in metrics
            if item["sufficient_samples"]
            and item["success_rate_percent"] is not None
        ]

        return sorted(
            eligible_agents,
            key=lambda item: item["success_rate_percent"],
            reverse=True,
        )
