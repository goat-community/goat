"""Garage bootstrap against a fake admin API: every step is idempotent."""

from typing import Any

import pytest
from goatlib.storage import garage_init


class FakeApi:
    """Records calls and answers like Garage's admin API v2."""

    def __init__(
        self,
        role: dict[str, Any] | None = None,
        keys: list[str] | None = None,
        buckets: dict[str, str] | None = None,
    ) -> None:
        self.role = role
        self.keys = keys or []
        self.buckets = buckets or {}
        self.calls: list[tuple[str, str, object | None]] = []

    def __call__(self, method: str, path: str, body: object | None = None) -> Any:
        self.calls.append((method, path, body))
        if path == "GetClusterStatus":
            return {"nodes": [{"id": "node1", "role": self.role}]}
        if path == "GetClusterLayout":
            return {"version": 3}
        if path == "ListKeys":
            return [{"id": k} for k in self.keys]
        if path == "ListBuckets":
            return [{"id": i, "globalAliases": [a]} for a, i in self.buckets.items()]
        if path == "CreateBucket":
            return {"id": f"id-{body['globalAlias']}"}  # type: ignore[index]
        return None

    def paths(self) -> list[str]:
        return [p for _, p, _ in self.calls]


def test_layout_is_assigned_and_applied_once() -> None:
    api = FakeApi(role=None)
    garage_init.ensure_layout(api, capacity=100)
    assert ("POST", "ApplyClusterLayout", {"version": 4}) in api.calls
    update = next(b for _, p, b in api.calls if p == "UpdateClusterLayout")
    assert update["roles"][0]["id"] == "node1"  # type: ignore[index]

    assigned = FakeApi(role={"zone": "dc1"})
    garage_init.ensure_layout(assigned, capacity=100)
    assert "UpdateClusterLayout" not in assigned.paths()


def test_key_is_imported_only_when_missing() -> None:
    api = FakeApi(keys=[])
    garage_init.ensure_key(api, "GK0123", "secret")
    assert (
        "POST",
        "ImportKey",
        {"accessKeyId": "GK0123", "secretAccessKey": "secret", "name": "goat"},
    ) in api.calls

    present = FakeApi(keys=["GK0123"])
    garage_init.ensure_key(present, "GK0123", "secret")
    assert "ImportKey" not in present.paths()


def test_bucket_is_created_once_and_granted_to_the_key() -> None:
    api = FakeApi()
    garage_init.ensure_bucket(api, "goat", "GK0123", website=False)
    assert "CreateBucket" in api.calls[1][1]
    grant = next(b for _, p, b in api.calls if p == "AllowBucketKey")
    assert grant == {
        "bucketId": "id-goat",
        "accessKeyId": "GK0123",
        "permissions": {"read": True, "write": True, "owner": True},
    }
    assert not any(p.startswith("UpdateBucket") for p in api.paths())

    existing = FakeApi(buckets={"goat": "b1"})
    garage_init.ensure_bucket(existing, "goat", "GK0123", website=False)
    assert "CreateBucket" not in existing.paths()


def test_assets_bucket_gets_website_access() -> None:
    api = FakeApi(buckets={"goat-assets": "b2"})
    garage_init.ensure_bucket(api, "goat-assets", "GK0123", website=True)
    assert ("POST", "UpdateBucket?id=b2") in [(m, p) for m, p, _ in api.calls]


def test_settings_read_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name, value in {
        "GARAGE_ADMIN_URL": "http://garage:3903/",
        "GARAGE_ADMIN_TOKEN": "t",
        "GARAGE_S3_URL": "http://garage:3900",
        "S3_ACCESS_KEY_ID": "GK0123",
        "S3_SECRET_ACCESS_KEY": "s",
        "GOAT_PUBLIC_URL": "https://goat.example.org/",
    }.items():
        monkeypatch.setenv(name, value)
    monkeypatch.delenv("GARAGE_CORS_ORIGINS", raising=False)
    monkeypatch.delenv("UPLOADS_BUCKET", raising=False)
    s = garage_init.Settings.from_env()
    assert s.admin_url == "http://garage:3903"
    assert s.cors_origins == ["https://goat.example.org"]
    assert (s.uploads_bucket, s.assets_bucket) == ("goat-uploads", "goat-assets")

    monkeypatch.setenv("GARAGE_CORS_ORIGINS", "https://a.example, https://b.example/")
    monkeypatch.setenv("UPLOADS_BUCKET", "goat")
    s = garage_init.Settings.from_env()
    assert s.cors_origins == ["https://a.example", "https://b.example"]
    assert s.uploads_bucket == "goat"
