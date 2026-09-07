"""Exercise durable API edits, validation and the local browser security boundary."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from pb_stats.app import create_app
from pb_stats.store import Store

ORIGIN = "http://127.0.0.1:8765"
HEADERS = {"X-Session-Token": "test-session", "Origin": ORIGIN}


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    static = tmp_path / "dist"
    static.mkdir()
    (static / "index.html").write_text("<html>Review workspace</html>")
    return TestClient(
        create_app(tmp_path / "metadata.sqlite3", static, "test-session"),
        base_url=ORIGIN,
        headers=HEADERS,
    )


def test_save_conflict_and_reopen(client: TestClient, tmp_path: Path) -> None:
    assert client.get("/").status_code == 200
    assert "Review workspace" in client.get("/").text
    assert client.get("/api/workspace").json()["revision"] == 0
    saved = client.patch("/api/workspace", json={"name": "Final", "expected_revision": 0})
    assert saved.json() == {"id": "local", "name": "Final", "revision": 1}
    stale = client.patch("/api/workspace", json={"name": "Old edit", "expected_revision": 0})
    assert stale.status_code == 409
    assert stale.json()["detail"]["current_revision"] == 1
    reopened = TestClient(
        create_app(tmp_path / "metadata.sqlite3", tmp_path / "dist", "new-session"),
        base_url=ORIGIN,
        headers={"X-Session-Token": "new-session"},
    )
    assert reopened.get("/api/workspace").json() == saved.json()


@pytest.mark.parametrize(
    "body",
    [
        {"name": "", "expected_revision": 0},
        {"name": "  ", "expected_revision": 0},
        {"name": "x", "expected_revision": -1},
        {"name": "x", "expected_revision": "0"},
        {"name": "x", "expected_revision": True},
        {"name": "x", "expected_revision": 0, "extra": "discard me"},
    ],
)
def test_reject_invalid_mutations(client: TestClient, body: dict[str, object]) -> None:
    assert client.patch("/api/workspace", json=body).status_code == 422
    assert client.get("/api/workspace").json()["revision"] == 0


@pytest.mark.parametrize(
    ("headers", "status"),
    [
        ({"Host": "attacker.example:8765"}, 400),
        ({"Host": "127.0.0.1:9999"}, 400),
        ({"Origin": "https://attacker.example"}, 403),
        ({"Origin": "null"}, 403),
        ({"X-Session-Token": "wrong"}, 401),
    ],
)
def test_reject_untrusted_requests(
    client: TestClient, headers: dict[str, str], status: int
) -> None:
    assert client.get("/api/workspace", headers=headers).status_code == status


def test_missing_credentials_and_origin(client: TestClient) -> None:
    client.headers.clear()
    assert client.get("/api/workspace").status_code == 401
    client.headers["X-Session-Token"] = "test-session"
    assert (
        client.patch("/api/workspace", json={"name": "x", "expected_revision": 0}).status_code
        == 403
    )
    assert client.get("/api/unknown").status_code == 404
    assert client.get("/api/unknown").headers["content-type"] == "application/json"


def test_create_app_uses_injected_store(tmp_path: Path) -> None:
    database = tmp_path / "metadata.sqlite3"
    injected = Store(database)
    injected.rename_workspace("Injected", 0)
    static = tmp_path / "dist"
    static.mkdir()
    (static / "index.html").write_text("<html>Review workspace</html>")
    client = TestClient(
        create_app(database, static, "test-session", store=injected),
        base_url=ORIGIN,
        headers=HEADERS,
    )
    assert client.get("/api/workspace").json() == {
        "id": "local",
        "name": "Injected",
        "revision": 1,
    }
