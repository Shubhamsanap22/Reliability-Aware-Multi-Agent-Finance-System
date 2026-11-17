
from app.execution.history_store import ExecutionHistoryStore
from app.monitoring.performance_analytics import (
    AgentPerformanceAnalytics,
)


def add_record(
    store,
    agent_name,
    status="completed",
    execution_time=0.5,
    used_budget=400,
    execution_started=True,
    is_fallback=False,
):
    store.record_attempt(
        run_id="test_run",
        agent_name=agent_name,
        capabilities="risk_analysis",
        attempt_number=1,
        is_fallback=is_fallback,
        execution_started=execution_started,
        execution_time_seconds=execution_time,
        status=status,
        reliability=0.90,
        allocated_budget=900,
        used_budget=used_budget,
        failure_reason=None,
    )


def test_empty_history_returns_empty_metrics(tmp_path):
    store = ExecutionHistoryStore(
        str(tmp_path / "history.db")
    )

    analytics = AgentPerformanceAnalytics(store)

    assert analytics.get_all_agent_metrics() == []
    assert analytics.get_ranked_agents() == []


def test_success_rate_is_calculated_correctly(tmp_path):
    store = ExecutionHistoryStore(
        str(tmp_path / "history.db")
    )

    add_record(store, "Risk Agent", "completed")
    add_record(store, "Risk Agent", "completed")
    add_record(store, "Risk Agent", "failed")

    analytics = AgentPerformanceAnalytics(store)

    metrics = analytics.get_agent_metrics("Risk Agent")

    assert metrics["execution_count"] == 3
    assert metrics["successful_executions"] == 2
    assert metrics["failed_executions"] == 1
    assert abs(metrics["success_rate_percent"] - 66.6667) < 0.01


def test_execution_time_average_is_calculated(tmp_path):
    store = ExecutionHistoryStore(
        str(tmp_path / "history.db")
    )

    add_record(store, "Investment Agent", execution_time=0.2)
    add_record(store, "Investment Agent", execution_time=0.4)

    analytics = AgentPerformanceAnalytics(store)

    metrics = analytics.get_agent_metrics("Investment Agent")

    assert abs(metrics["average_execution_time_seconds"] - 0.3) < 1e-9


def test_average_budget_usage_is_calculated(tmp_path):
    store = ExecutionHistoryStore(
        str(tmp_path / "history.db")
    )

    add_record(store, "Portfolio Agent", used_budget=300)
    add_record(store, "Portfolio Agent", used_budget=500)

    analytics = AgentPerformanceAnalytics(store)

    metrics = analytics.get_agent_metrics("Portfolio Agent")

    assert metrics["average_budget_used"] == 400


def test_budget_rejections_are_not_counted_as_executions(tmp_path):
    store = ExecutionHistoryStore(
        str(tmp_path / "history.db")
    )

    add_record(store, "Risk Agent", "completed")

    add_record(
        store,
        "Risk Agent",
        status="budget_rejected",
        execution_time=None,
        used_budget=0,
        execution_started=False,
    )

    analytics = AgentPerformanceAnalytics(store)

    metrics = analytics.get_agent_metrics("Risk Agent")

    assert metrics["total_attempts"] == 2
    assert metrics["execution_count"] == 1
    assert metrics["budget_rejections"] == 1
    assert metrics["success_rate_percent"] == 100.0


def test_insufficient_samples_are_identified(tmp_path):
    store = ExecutionHistoryStore(
        str(tmp_path / "history.db")
    )

    for _ in range(3):
        add_record(store, "Risk Agent")

    analytics = AgentPerformanceAnalytics(
        store,
        minimum_samples=5,
    )

    metrics = analytics.get_agent_metrics("Risk Agent")

    assert metrics["sample_count"] == 3
    assert metrics["sufficient_samples"] is False


def test_agent_ranking_excludes_insufficient_samples(tmp_path):
    store = ExecutionHistoryStore(
        str(tmp_path / "history.db")
    )

    # Risk Agent: 5 successful executions.
    for _ in range(5):
        add_record(store, "Risk Agent", "completed")

    # Investment Agent: 3 successful executions.
    for _ in range(3):
        add_record(store, "Investment Agent", "completed")

    analytics = AgentPerformanceAnalytics(
        store,
        minimum_samples=5,
    )

    ranked = analytics.get_ranked_agents()

    assert len(ranked) == 1
    assert ranked[0]["agent_name"] == "Risk Agent"


def test_fallback_count_is_calculated(tmp_path):
    store = ExecutionHistoryStore(
        str(tmp_path / "history.db")
    )

    add_record(
        store,
        "Portfolio Agent",
        is_fallback=True,
    )

    add_record(
        store,
        "Portfolio Agent",
        is_fallback=False,
    )

    analytics = AgentPerformanceAnalytics(store)

    metrics = analytics.get_agent_metrics("Portfolio Agent")

    assert metrics["fallback_count"] == 1
