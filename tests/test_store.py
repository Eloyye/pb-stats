"""Durability, referential integrity, and competing editor integration scenarios."""

import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from pb_stats.store import RevisionConflict, Store


def test_migrations_and_foreign_keys(tmp_path: Path) -> None:
    store = Store(tmp_path / "metadata.sqlite3")
    with store.connection() as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 1
        assert connection.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("INSERT INTO fact VALUES ('f','missing',NULL,'shot_type',NULL,0)")
    assert Store(store.path).read_workspace().revision == 0


def test_concurrent_editors_have_one_winner(tmp_path: Path) -> None:
    store = Store(tmp_path / "metadata.sqlite3")

    def rename(name: str) -> str:
        try:
            store.rename_workspace(name, 0)
            return "saved"
        except RevisionConflict:
            return "conflict"

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(rename, ["One", "Two"]))
    assert sorted(results) == ["conflict", "saved"]
    assert store.read_workspace().revision == 1


def test_reader_sees_committed_revision_during_write(tmp_path: Path) -> None:
    store = Store(tmp_path / "metadata.sqlite3")
    with store.connection() as writer:
        writer.execute("BEGIN IMMEDIATE")
        writer.execute("UPDATE workspace SET name='Uncommitted'")
        with ThreadPoolExecutor(max_workers=1) as pool:
            assert pool.submit(store.read_workspace).result(timeout=2).name == "Local match"
        writer.rollback()


def test_existing_database_is_backed_up_before_migration(tmp_path: Path) -> None:
    path = tmp_path / "metadata.sqlite3"
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE prior_data(value TEXT)")
        connection.execute("INSERT INTO prior_data VALUES ('keep me')")
    Store(path)
    with sqlite3.connect(path.with_name("metadata.sqlite3.before-v1.bak")) as backup:
        assert backup.execute("SELECT value FROM prior_data").fetchone()[0] == "keep me"
        assert backup.execute("PRAGMA user_version").fetchone()[0] == 0


def test_failed_backup_blocks_migration(tmp_path: Path) -> None:
    path = tmp_path / "metadata.sqlite3"
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE prior_data(value TEXT)")
    path.with_name("metadata.sqlite3.before-v1.bak").mkdir()
    with pytest.raises(RuntimeError, match="backup already exists"):
        Store(path)
    with sqlite3.connect(path) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 0


@pytest.mark.parametrize("name", ["", "   "])
def test_rename_rejects_empty_names(tmp_path: Path, name: str) -> None:
    store = Store(tmp_path / "metadata.sqlite3")
    with pytest.raises(ValueError, match="must not be empty"):
        store.rename_workspace(name, 0)
    assert store.read_workspace().revision == 0


def test_workspace_name_check_rejects_empty_sql_writes(tmp_path: Path) -> None:
    store = Store(tmp_path / "metadata.sqlite3")
    with store.connection() as connection, pytest.raises(sqlite3.IntegrityError):
        connection.execute("UPDATE workspace SET name='' WHERE id='local'")
    assert store.read_workspace().name == "Local match"
