"""One coordinator writes short transactions; WAL connections permit independent readers."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from threading import Lock

from pb_stats.contracts import Workspace

LOCAL_WORKSPACE_ID = "local"

MIGRATIONS = (
    (
        "CREATE TABLE workspace (id TEXT PRIMARY KEY, name TEXT NOT NULL "
        "CHECK(length(name) > 0), revision INTEGER NOT NULL DEFAULT 0 CHECK(revision >= 0))",
        "CREATE TABLE processing_run (id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL "
        "REFERENCES workspace(id), input_revision INTEGER NOT NULL CHECK(input_revision >= 0), "
        "status TEXT NOT NULL CHECK(status IN ('queued','running','completed','failed')))",
        "CREATE TABLE fact (id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL REFERENCES "
        "workspace(id), run_id TEXT REFERENCES processing_run(id), attribute TEXT NOT NULL, "
        "value TEXT, revision INTEGER NOT NULL CHECK(revision >= 0))",
        "CREATE TABLE human_decision (id TEXT PRIMARY KEY, fact_id TEXT NOT NULL REFERENCES "
        "fact(id), expected_revision INTEGER NOT NULL CHECK(expected_revision >= 0), "
        "prior_value TEXT, new_value TEXT, kind TEXT NOT NULL CHECK(kind IN "
        "('confirmation','correction','unknown','undo')), created_at TEXT NOT NULL "
        "DEFAULT CURRENT_TIMESTAMP, undo_of TEXT REFERENCES human_decision(id))",
        "INSERT INTO workspace(id, name) VALUES ('local', 'Local match')",
    ),
)


class RevisionConflict(Exception):
    def __init__(self, revision: int) -> None:
        self.revision = revision
        super().__init__(f"Current revision is {revision}")


class Store:
    """Single-coordinator metadata writer.

    Writers serialize through an in-process lock while WAL mode permits
    independent readers. Cross-instance safety relies on SQLite
    ``BEGIN IMMEDIATE``; only one coordinator process may open the database.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self._writer = Lock()
        path.parent.mkdir(parents=True, exist_ok=True)
        self._migrate()

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=5)
        connection.execute("PRAGMA foreign_keys=ON")
        try:
            yield connection
        finally:
            connection.close()

    def _migrate(self) -> None:
        with self._writer, self.connection() as connection:
            version = int(connection.execute("PRAGMA user_version").fetchone()[0])
            if version > len(MIGRATIONS):
                raise RuntimeError("Workspace schema is newer than this application")
            if version == len(MIGRATIONS):
                return
            if self.path.stat().st_size:
                # SQLite backup includes committed WAL contents; failure prevents migration.
                backup = self.path.with_name(f"{self.path.name}.before-v{version + 1}.bak")
                if backup.exists():
                    raise RuntimeError(f"Migration backup already exists: {backup}")
                with sqlite3.connect(backup) as snapshot:
                    connection.backup(snapshot)
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("BEGIN IMMEDIATE")
            try:
                for index in range(version, len(MIGRATIONS)):
                    for statement in MIGRATIONS[index]:
                        connection.execute(statement)
                    connection.execute(f"PRAGMA user_version={index + 1}")
                connection.commit()
            except Exception:
                connection.rollback()
                raise

    def read_workspace(self) -> Workspace:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT id, name, revision FROM workspace WHERE id=?",
                (LOCAL_WORKSPACE_ID,),
            ).fetchone()
            if row is None:
                raise RuntimeError("Workspace record is missing")
            return Workspace(id=row[0], name=row[1], revision=row[2])

    def rename_workspace(self, name: str, expected_revision: int) -> Workspace:
        if not name.strip():
            raise ValueError("Workspace name must not be empty")
        with self._writer, self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT revision FROM workspace WHERE id=?", (LOCAL_WORKSPACE_ID,)
            ).fetchone()
            if row is None:
                connection.rollback()
                raise RuntimeError("Workspace record is missing")
            revision = int(row[0])
            if revision != expected_revision:
                connection.rollback()
                raise RevisionConflict(revision)
            connection.execute(
                "UPDATE workspace SET name=?, revision=revision+1 WHERE id=?",
                (name, LOCAL_WORKSPACE_ID),
            )
            connection.commit()
            return Workspace(id=LOCAL_WORKSPACE_ID, name=name, revision=revision + 1)
