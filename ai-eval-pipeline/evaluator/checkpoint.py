import sqlite3
from pathlib import Path


DB_PATH = Path("results/evaluations.db")


class CheckpointStore:

    def __init__(self, db_path: Path = DB_PATH):
        db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.connection = sqlite3.connect(
            db_path,
            check_same_thread=False,
        )

        self._create_table()

    def _create_table(self):
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS evaluation_records (
                request_id TEXT NOT NULL,
                record_id TEXT NOT NULL,
                status TEXT NOT NULL,
                score INTEGER,
                reason TEXT,
                PRIMARY KEY (request_id, record_id)
            )
            """
        )

        self.connection.commit()

    def get_status(
        self,
        request_id: str,
        record_id: str,
    ) -> str | None:

        cursor = self.connection.execute(
            """
            SELECT status
            FROM evaluation_records
            WHERE request_id = ?
              AND record_id = ?
            """,
            (request_id, record_id),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return row[0]

    def mark_processing(
        self,
        request_id: str,
        record_id: str,
    ):
        self.connection.execute(
            """
            INSERT INTO evaluation_records (
                request_id,
                record_id,
                status
            )
            VALUES (?, ?, 'processing')

            ON CONFLICT(request_id, record_id)
            DO UPDATE SET
                status = 'processing'
            """,
            (request_id, record_id),
        )

        self.connection.commit()

    def mark_completed(
        self,
        request_id: str,
        record_id: str,
        score: int,
        reason: str,
    ):
        self.connection.execute(
            """
            INSERT INTO evaluation_records (
                request_id,
                record_id,
                status,
                score,
                reason
            )
            VALUES (?, ?, 'completed', ?, ?)

            ON CONFLICT(request_id, record_id)
            DO UPDATE SET
                status = 'completed',
                score = excluded.score,
                reason = excluded.reason
            """,
            (
                request_id,
                record_id,
                score,
                reason,
            ),
        )

        self.connection.commit()

    def mark_failed(
        self,
        request_id: str,
        record_id: str,
        reason: str,
    ):
        self.connection.execute(
            """
            INSERT INTO evaluation_records (
                request_id,
                record_id,
                status,
                reason
            )
            VALUES (?, ?, 'failed', ?)

            ON CONFLICT(request_id, record_id)
            DO UPDATE SET
                status = 'failed',
                reason = excluded.reason
            """,
            (
                request_id,
                record_id,
                reason,
            ),
        )

        self.connection.commit()

    def close(self):
        self.connection.close()