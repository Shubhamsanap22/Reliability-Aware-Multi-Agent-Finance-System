
from collections import deque
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from main import create_application
from app.aggregation.result_aggregator import ResultAggregator
from app.reporting.consolidated_report import ConsolidatedReportBuilder

router = APIRouter()
HISTORY: deque[dict[str, Any]] = deque(maxlen=100)


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=5000)


def model_to_dict(value: Any) -> Any:
    """Convert models, enums, and nested values into JSON-safe data."""
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")

    if hasattr(value, "dict"):
        return value.dict()

    if hasattr(value, "value"):
        return value.value

    if isinstance(value, dict):
        return {
            key: model_to_dict(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            model_to_dict(item)
            for item in value
        ]

    return value


def serialize_agent(result: Any) -> dict[str, Any]:
    """Serialize one agent result for workflow monitoring."""
    return {
        "agent_name": result.agent_name,
        "reliability": result.reliability,
        "allocated_budget": result.allocated_budget,
        "used_budget": result.used_budget,
        "status": result.status.value,
        "output": result.output,
        "failure_reason": result.failure_reason,
        "remaining_agent_budget": result.remaining_agent_budget,
    }


def serialize_budget(orchestrator: Any) -> dict[str, Any]:
    """Serialize the orchestrator's budget state."""
    state = orchestrator.executor.budget_manager.state

    return {
        "global_budget": state.global_budget,
        "allocated_budget": state.allocated_budget,
        "used_budget": state.used_budget,
        "reserved_budget": state.reserved_budget,
        "remaining_budget": state.remaining_budget,
        "available_budget": state.available_budget,
    }


def serialize_report(results: list[Any]) -> dict[str, Any]:
    """Convert the existing result aggregator output into a dictionary."""
    report = ResultAggregator().aggregate(results)

    return {
        "overall_status": model_to_dict(report.overall_status),
        "total_agents": report.total_agents,
        "completed_agents": report.completed_agents,
        "failed_agents": report.failed_agents,
        "incomplete_agents": report.incomplete_agents,
        "findings": [
            {
                "agent_name": finding.agent_name,
                "output": finding.output,
                "reliability": finding.reliability,
            }
            for finding in report.findings
        ],
        "limitations": report.limitations,
        "allocated_budget": report.allocated_budget,
        "used_budget": report.used_budget,
        "executive_summary": report.executive_summary,
    }


@router.get("/health")
def health() -> dict[str, str]:
    """Basic API health check."""
    return {
        "status": "ok",
        "service": "financial-multi-agent-api",
    }


@router.post("/query")
def run_query(request: QueryRequest) -> dict[str, Any]:
    """Run the agents and return a consolidated financial report."""
    query = request.query.strip()

    if not query:
        raise HTTPException(
            status_code=422,
            detail="Query cannot be empty.",
        )

    try:
        orchestrator = create_application()

        # Analyze the query to identify the user's requested task
        # and any explicitly supplied planning assumptions.
        requirement = orchestrator.analyzer.analyze(query)

        # Execute the existing multi-agent workflow.
        results = orchestrator.run(query)

        # Keep detailed agent output for diagnostics and workflow monitoring.
        serialized_results = [
            serialize_agent(result)
            for result in results
        ]

        # Aggregate the existing agent results.
        report = serialize_report(results)

        # Build a single user-facing summary and evidence-backed charts.
        report = ConsolidatedReportBuilder().build(
            query=query,
            requirement=requirement,
            results=results,
            base_report=report,
        )

        budget = serialize_budget(orchestrator)

        response = {
            "query": query,
            "requirement": model_to_dict(requirement),
            "results": serialized_results,
            "report": report,
            "budget": budget,
        }

        HISTORY.appendleft(response)
        return response

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Query execution failed: {exc}",
        ) from exc


@router.get("/history")
def get_history() -> dict[str, Any]:
    """Return recent query responses stored in this process."""
    return {"items": list(HISTORY)}
