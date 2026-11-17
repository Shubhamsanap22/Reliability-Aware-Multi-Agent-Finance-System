
from app.execution.history_store import ExecutionHistoryStore


def record_sample(
    store: ExecutionHistoryStore,
    agent_name: str = "Risk Agent",
    run_id: str = "run_001",
    status: str = "completed",
    attempt_number: int = 1,
    is_fallback: bool = False,
    execution_started: bool = True,
    execution_time_seconds: float | None = 0.25,
    reliability: float | None = 0.91,
    allocated_budget: int = 900,
    used_budget: int = 400,
    failure_reason: str | None = None,
) -> None:
    """Insert a sample execution attempt."""

    store.record_attempt(
        run_id=run_id,
        agent_name=agent_name,
        capabilities="risk_analysis",
        attempt_number=attempt_number,
        is_fallback=is_fallback,
        execution_started=execution_started,
        execution_time_seconds=execution_time_seconds,
        status=status,
        reliability=reliability,
        allocated_budget=allocated_budget,
        used_budget=used_budget,
        failure_reason=failure_reason,
    )


def test_database_and_table_are_created(tmp_path):
    database_path = tmp_path / "test_history.db"

    store = ExecutionHistoryStore(
        database_path=str(database_path)
    )

    assert database_path.exists()
    assert store.get_record_count() == 0


def test_record_attempt_is_saved(tmp_path):
    database_path = tmp_path / "test_history.db"

    store = ExecutionHistoryStore(
        database_path=str(database_path)
    )

    record_sample(store)

    records = store.get_all_records()

    assert len(records) == 1

    record = records[0]

    assert record["agent_name"] == "Risk Agent"
    assert record["run_id"] == "run_001"
    assert record["status"] == "completed"
    assert record["execution_time_seconds"] == 0.25
    assert record["allocated_budget"] == 900
    assert record["used_budget"] == 400
    assert record["is_fallback"] == 0


def test_agent_records_are_filtered_correctly(tmp_path):
    database_path = tmp_path / "test_history.db"

    store = ExecutionHistoryStore(
        database_path=str(database_path)
    )

    record_sample(
        store,
        agent_name="Risk Agent",
        run_id="run_001",
    )

    record_sample(
        store,
        agent_name="Investment Agent",
        run_id="run_002",
    )

    risk_records = store.get_agent_records("Risk Agent")
    investment_records = store.get_agent_records("Investment Agent")

    assert len(risk_records) == 1
    assert len(investment_records) == 1

    assert risk_records[0]["agent_name"] == "Risk Agent"
    assert investment_records[0]["agent_name"] == "Investment Agent"

    assert store.get_agent_records("Unknown Agent") == []


def test_records_persist_after_reopening_database(tmp_path):
    database_path = tmp_path / "test_history.db"

    first_store = ExecutionHistoryStore(
        database_path=str(database_path)
    )

    record_sample(first_store)

    # Create a new store instance using the same database.
    second_store = ExecutionHistoryStore(
        database_path=str(database_path)
    )

    assert second_store.get_record_count() == 1

    records = second_store.get_all_records()

    assert records[0]["agent_name"] == "Risk Agent"


def test_record_count_updates_correctly(tmp_path):
    database_path = tmp_path / "test_history.db"

    store = ExecutionHistoryStore(
        database_path=str(database_path)
    )

    assert store.get_record_count() == 0

    record_sample(store, run_id="run_001")
    assert store.get_record_count() == 1

    record_sample(
        store,
        agent_name="Investment Agent",
        run_id="run_002",
    )
    assert store.get_record_count() == 2


def test_failed_attempt_details_are_saved(tmp_path):
    database_path = tmp_path / "test_history.db"

    store = ExecutionHistoryStore(
        database_path=str(database_path)
    )

    record_sample(
        store,
        status="failed",
        failure_reason="Simulated agent failure",
        attempt_number=2,
    )

    records = store.get_all_records()

    assert len(records) == 1
    assert records[0]["status"] == "failed"
    assert records[0]["attempt_number"] == 2
    assert records[0]["failure_reason"] == "Simulated agent failure"


def test_fallback_attempt_is_saved(tmp_path):
    database_path = tmp_path / "test_history.db"

    store = ExecutionHistoryStore(
        database_path=str(database_path)
    )

    record_sample(
        store,
        agent_name="Portfolio Agent",
        is_fallback=True,
    )

    records = store.get_all_records()

    assert len(records) == 1
    assert records[0]["is_fallback"] == 1


def test_budget_rejection_is_saved_without_execution(tmp_path):
    database_path = tmp_path / "test_history.db"

    store = ExecutionHistoryStore(
        database_path=str(database_path)
    )

    record_sample(
        store,
        status="budget_rejected",
        execution_started=False,
        execution_time_seconds=None,
        allocated_budget=900,
        used_budget=0,
    )

    records = store.get_all_records()

    assert len(records) == 1

    record = records[0]

    assert record["status"] == "budget_rejected"
    assert record["execution_started"] == 0
    assert record["execution_time_seconds"] is None
    assert record["used_budget"] == 0
