
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterator, List


class ExecutionHistoryStore:
    """
    Stores agent execution history in a persistent SQLite database.

    Each execution attempt is stored separately, including:
    - Agent name and capabilities
    - Attempt number
    - Fallback execution status
    - Execution duration
    - Success or failure status
    - Reliability score
    - Allocated and consumed budget
    - Failure reason
    - Timestamp
    """

    def __init__(
        self,
        database_path: str = "data/execution_history.db"
    ):
        self.database_path = Path(database_path)

        # Create the parent directory if it does not exist.
        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self._initialize_database()

    @contextmanager
    def _get_connection(self) -> Iterator[sqlite3.Connection]:
        """
        Creates and safely manages a SQLite connection.

        Commits successful transactions, rolls back failed
        transactions, and always closes the connection.
        """

        connection = sqlite3.connect(
            str(self.database_path),
            timeout=30
        )

        connection.row_factory = sqlite3.Row

        try:
            yield connection
            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def _initialize_database(self) -> None:
        """
        Creates the execution_history table and indexes
        if they do not already exist.
        """

        with self._get_connection() as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS execution_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    run_id TEXT NOT NULL,

                    agent_name TEXT NOT NULL,

                    capabilities TEXT,

                    attempt_number INTEGER NOT NULL,

                    is_fallback INTEGER NOT NULL DEFAULT 0,

                    execution_started INTEGER NOT NULL DEFAULT 1,

                    execution_time_seconds REAL,

                    status TEXT NOT NULL,

                    reliability REAL,

                    allocated_budget INTEGER NOT NULL DEFAULT 0,

                    used_budget INTEGER NOT NULL DEFAULT 0,

                    failure_reason TEXT,

                    timestamp TEXT NOT NULL DEFAULT (
                        strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                    )
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_execution_history_agent
                ON execution_history(agent_name)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_execution_history_run
                ON execution_history(run_id)
                """
            )

    def record_attempt(
        self,
        run_id: str,
        agent_name: str,
        capabilities: str,
        attempt_number: int,
        is_fallback: bool,
        execution_started: bool,
        execution_time_seconds: float | None,
        status: str,
        reliability: float | None,
        allocated_budget: int,
        used_budget: int,
        failure_reason: str | None = None
    ) -> None:
        """
        Records one agent execution attempt.

        A retry or fallback is stored as a separate record.
        """

        with self._get_connection() as connection:

            connection.execute(
                """
                INSERT INTO execution_history (
                    run_id,
                    agent_name,
                    capabilities,
                    attempt_number,
                    is_fallback,
                    execution_started,
                    execution_time_seconds,
                    status,
                    reliability,
                    allocated_budget,
                    used_budget,
                    failure_reason
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    agent_name,
                    capabilities,
                    attempt_number,
                    int(is_fallback),
                    int(execution_started),
                    execution_time_seconds,
                    status,
                    reliability,
                    allocated_budget,
                    used_budget,
                    failure_reason
                )
            )

    def get_all_records(self) -> List[Dict[str, Any]]:
        """
        Returns all execution-history records,
        ordered by insertion ID.
        """

        with self._get_connection() as connection:

            rows = connection.execute(
                """
                SELECT *
                FROM execution_history
                ORDER BY id ASC
                """
            ).fetchall()

            return [dict(row) for row in rows]

    def get_agent_records(
        self,
        agent_name: str
    ) -> List[Dict[str, Any]]:
        """
        Returns execution-history records for one agent.
        """

        with self._get_connection() as connection:

            rows = connection.execute(
                """
                SELECT *
                FROM execution_history
                WHERE agent_name = ?
                ORDER BY id ASC
                """,
                (agent_name,)
            ).fetchall()

            return [dict(row) for row in rows]

    def get_record_count(self) -> int:
        """
        Returns the total number of recorded attempts.
        """

        with self._get_connection() as connection:

            result = connection.execute(
                """
                SELECT COUNT(*) AS total
                FROM execution_history
                """
            ).fetchone()

            return int(result["total"])
