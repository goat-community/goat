"""The anonymous seat for preview-sql: a published project's own stored queries.

A public dashboard's table widget runs the SQL its author saved in the
builder config. The viewer is anonymous, so the router lets preview-sql run
without a caller only when the request names a published project and both the
query and every layer it reads are part of that project's published snapshot.
"""

from typing import Any

import duckdb
import pytest
from fastapi.testclient import TestClient

import processes.routers.processes as processes_router
from processes.main import app
from processes.services.analytics_service import analytics_service
from processes.services.public_search_config import parse_sql_scope

PROJECT_ID = "3e870eb8-9633-44e9-8a43-36a7290f1ced"
LAYER_ID = "90e3bcb2-d7ec-4abf-955d-50633ab4a101"
QUERY = "SELECT indikator, wert\nFROM input_1\nLIMIT 4"


def _snapshot() -> dict[str, Any]:
    return {
        "project": {
            "builder_config": {
                "interface": [
                    {"widgets": [{"config": {"setup": {"sql_query": QUERY}}}]},
                    {"widgets": [{"config": {"setup": {"query_mode": "grouped"}}}]},
                ]
            }
        },
        "layers": [{"id": 86901, "layer_id": LAYER_ID}],
    }


class TestParseSqlScope:
    def test_collects_every_stored_query_and_layer(self) -> None:
        scope = parse_sql_scope(_snapshot())
        assert scope["queries"] == {QUERY}
        assert scope["layer_ids"] == {LAYER_ID}

    def test_snapshot_without_builder_config_is_empty(self) -> None:
        scope = parse_sql_scope({"project": {}, "layers": []})
        assert scope["queries"] == set()
        assert scope["layer_ids"] == set()

    def test_non_string_sql_values_are_ignored(self) -> None:
        config = _snapshot()
        config["project"]["builder_config"]["interface"][0]["widgets"][0]["config"][
            "setup"
        ]["sql_query"] = None
        assert parse_sql_scope(config)["queries"] == set()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def published(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        processes_router,
        "get_public_sql_scope",
        lambda project_id: parse_sql_scope(_snapshot()),
    )


@pytest.fixture
def preview_calls(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []

    def fake_preview(self: Any, **kwargs: Any) -> dict[str, Any]:
        calls.append(kwargs)
        return {"success": True, "columns": [], "rows": [], "error": None}

    monkeypatch.setattr(type(analytics_service), "preview_sql", fake_preview)
    return calls


def _post(client: TestClient, inputs: dict[str, Any]) -> Any:
    return client.post("/processes/preview-sql/execution", json={"inputs": inputs})


def test_anonymous_without_project_id_is_401(client: TestClient) -> None:
    resp = _post(client, {"sql_query": QUERY, "layers": {"input_1": LAYER_ID}})
    assert resp.status_code == 401


def test_anonymous_stored_query_on_published_layer_runs(
    client: TestClient, published: None, preview_calls: list[dict[str, Any]]
) -> None:
    resp = _post(
        client,
        {
            "project_id": PROJECT_ID,
            "sql_query": QUERY,
            "layers": {"input_1": LAYER_ID},
            "limit": 10,
            "offset": 0,
        },
    )
    assert resp.status_code == 200, resp.text
    assert preview_calls == [
        {
            "sql_query": QUERY,
            "layers": {"input_1": LAYER_ID},
            "user_id": None,
            "limit": 10,
            "offset": 0,
            "filter_expr": None,
        }
    ]


def test_anonymous_query_not_in_snapshot_is_403(
    client: TestClient, published: None, preview_calls: list[dict[str, Any]]
) -> None:
    resp = _post(
        client,
        {
            "project_id": PROJECT_ID,
            "sql_query": "SELECT * FROM input_1",
            "layers": {"input_1": LAYER_ID},
        },
    )
    assert resp.status_code == 403
    assert preview_calls == []


def test_anonymous_layer_not_in_snapshot_is_403(
    client: TestClient, published: None, preview_calls: list[dict[str, Any]]
) -> None:
    resp = _post(
        client,
        {
            "project_id": PROJECT_ID,
            "sql_query": QUERY,
            "layers": {"input_1": "b707a8a4-3260-497c-94e2-75e0b1261b06"},
        },
    )
    assert resp.status_code == 403
    assert preview_calls == []


def test_anonymous_temp_layer_is_403(
    client: TestClient, published: None, preview_calls: list[dict[str, Any]]
) -> None:
    resp = _post(
        client,
        {
            "project_id": PROJECT_ID,
            "sql_query": QUERY,
            "layers": {"input_1": f"temp:{LAYER_ID}"},
        },
    )
    assert resp.status_code == 403
    assert preview_calls == []


def test_anonymous_unpublished_project_is_403(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    preview_calls: list[dict[str, Any]],
) -> None:
    monkeypatch.setattr(processes_router, "get_public_sql_scope", lambda pid: None)
    resp = _post(
        client,
        {"project_id": PROJECT_ID, "sql_query": QUERY, "layers": {"input_1": LAYER_ID}},
    )
    assert resp.status_code == 403
    assert preview_calls == []


def test_anonymous_bad_project_id_is_422(
    client: TestClient, preview_calls: list[dict[str, Any]]
) -> None:
    resp = _post(
        client,
        {
            "project_id": "not-a-uuid",
            "sql_query": QUERY,
            "layers": {"input_1": LAYER_ID},
        },
    )
    assert resp.status_code == 422
    assert preview_calls == []


def test_snapshot_outage_is_503_without_leaking(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    preview_calls: list[dict[str, Any]],
) -> None:
    def boom(project_id: str) -> None:
        raise duckdb.IOException("postgresql://rds:SECRET@db/goat unreachable")

    monkeypatch.setattr(processes_router, "get_public_sql_scope", boom)
    resp = _post(
        client,
        {"project_id": PROJECT_ID, "sql_query": QUERY, "layers": {"input_1": LAYER_ID}},
    )
    assert resp.status_code == 503
    assert "SECRET" not in resp.text
    assert preview_calls == []
