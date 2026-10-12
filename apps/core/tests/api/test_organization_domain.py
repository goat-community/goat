"""Endpoint tests for /organizations/{org_id}/domains/.

These tests exercise the sync DNS check + provisioning trigger logic in
the user-facing CRUD endpoints. The k8s side is mocked via FakeProvisioner;
DNS resolution is monkeypatched via ``_resolve``.
"""

from typing import Generator
from uuid import UUID

import pytest
from core.core.config import settings
from core.deps.provisioner import reset_provisioner, set_provisioner
from core.services.provisioner import FakeProvisioner
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from tests.utils import TEST_CNAME_TARGET, fake_dns_resolve


@pytest.fixture(autouse=True)
def _custom_domains_on(monkeypatch: pytest.MonkeyPatch) -> None:
    """Custom domains are off by default; these tests run with them on."""
    monkeypatch.setattr(settings, "CUSTOM_DOMAIN_CNAME_TARGET", TEST_CNAME_TARGET)


@pytest.fixture(autouse=True)
def _isolate_provisioner() -> Generator[None, None, None]:
    """Reset provisioner singleton between tests."""
    reset_provisioner()
    yield
    reset_provisioner()


@pytest.fixture
def fake_provisioner() -> FakeProvisioner:
    fake = FakeProvisioner()
    set_provisioner(fake)
    return fake


@pytest.fixture
async def seeded_org(db_session: AsyncSession) -> str:
    """Insert a test Organization and return its id as a string."""
    from tests.utils import make_organization

    org = make_organization(name="test-org-for-domains")
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    return str(org.id)


@pytest.mark.asyncio
async def test_create_domain_pending_when_dns_not_set(
    client: AsyncClient,
    seeded_org: str,
    fake_provisioner: FakeProvisioner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "core.services.domain_reconciliation._resolve",
        fake_dns_resolve(),
    )

    r = await client.post(
        f"/api/v2/organizations/{seeded_org}/domains/",
        json={"base_domain": "klima.test.example.com"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["base_domain"] == "klima.test.example.com"
    assert body["dns_status"] == "pending"
    assert body["cert_status"] == "pending"
    # No k8s side effect because DNS wasn't verified.
    assert fake_provisioner.created == []


@pytest.mark.asyncio
async def test_create_domain_provisions_when_dns_already_set(
    client: AsyncClient,
    seeded_org: str,
    fake_provisioner: FakeProvisioner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "core.services.domain_reconciliation._resolve",
        fake_dns_resolve(cname=["cname.goat.plan4better.de."]),
    )

    r = await client.post(
        f"/api/v2/organizations/{seeded_org}/domains/",
        json={"base_domain": "klima2.test.example.com"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["dns_status"] == "verified"
    # Caddy issues lazily on first inbound request, so verified DNS flips
    # straight to active without an "issuing" intermediate state.
    assert body["cert_status"] == "active"
    assert fake_provisioner.created == ["klima2.test.example.com"]


@pytest.mark.asyncio
async def test_create_rejects_invalid_hostname(
    client: AsyncClient,
    seeded_org: str,
    fake_provisioner: FakeProvisioner,
) -> None:
    r = await client.post(
        f"/api/v2/organizations/{seeded_org}/domains/",
        json={"base_domain": "INVALID..hostname"},
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_create_accepts_apex_domain(
    client: AsyncClient,
    seeded_org: str,
    fake_provisioner: FakeProvisioner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Apex domains are supported via the A-record path (no CNAME at apex)."""
    monkeypatch.setattr(
        "core.services.domain_reconciliation._resolve",
        fake_dns_resolve(),
    )
    r = await client.post(
        f"/api/v2/organizations/{seeded_org}/domains/",
        json={"base_domain": "example.com"},  # apex
    )
    assert r.status_code == 201, r.text
    assert r.json()["dns_status"] == "pending"


@pytest.mark.asyncio
async def test_create_rejects_duplicate_domain(
    client: AsyncClient,
    seeded_org: str,
    fake_provisioner: FakeProvisioner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "core.services.domain_reconciliation._resolve",
        fake_dns_resolve(),
    )

    payload = {"base_domain": "duplicate.test.example.com"}
    r1 = await client.post(
        f"/api/v2/organizations/{seeded_org}/domains/",
        json=payload,
    )
    assert r1.status_code == 201, r1.text

    r2 = await client.post(
        f"/api/v2/organizations/{seeded_org}/domains/",
        json=payload,
    )
    assert r2.status_code == 409
    assert "already" in r2.json()["detail"].lower()


@pytest.mark.asyncio
async def test_list_domains_for_organization(
    client: AsyncClient,
    seeded_org: str,
    fake_provisioner: FakeProvisioner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "core.services.domain_reconciliation._resolve",
        fake_dns_resolve(),
    )

    for sub in ("a", "b"):
        r = await client.post(
            f"/api/v2/organizations/{seeded_org}/domains/",
            json={"base_domain": f"{sub}.test.example.com"},
        )
        assert r.status_code == 201, r.text

    r = await client.get(f"/api/v2/organizations/{seeded_org}/domains/")
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 2
    domains = sorted(b["base_domain"] for b in body)
    assert domains == ["a.test.example.com", "b.test.example.com"]


@pytest.mark.asyncio
async def test_get_single_domain(
    client: AsyncClient,
    seeded_org: str,
    fake_provisioner: FakeProvisioner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "core.services.domain_reconciliation._resolve",
        fake_dns_resolve(),
    )

    r = await client.post(
        f"/api/v2/organizations/{seeded_org}/domains/",
        json={"base_domain": "single.test.example.com"},
    )
    domain_id = r.json()["id"]

    r = await client.get(f"/api/v2/organizations/{seeded_org}/domains/{domain_id}")
    assert r.status_code == 200
    assert r.json()["base_domain"] == "single.test.example.com"


@pytest.mark.asyncio
async def test_get_404_for_unknown_domain(
    client: AsyncClient,
    seeded_org: str,
    fake_provisioner: FakeProvisioner,
) -> None:
    fake_id = "00000000-0000-0000-0000-000000000099"
    r = await client.get(f"/api/v2/organizations/{seeded_org}/domains/{fake_id}")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_recheck_provisions_when_dns_appears(
    client: AsyncClient,
    seeded_org: str,
    fake_provisioner: FakeProvisioner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # First call: DNS not set -> pending
    monkeypatch.setattr(
        "core.services.domain_reconciliation._resolve",
        fake_dns_resolve(),
    )

    r = await client.post(
        f"/api/v2/organizations/{seeded_org}/domains/",
        json={"base_domain": "recheck.test.example.com"},
    )
    domain_id = r.json()["id"]
    assert fake_provisioner.created == []

    # Now DNS is configured -> recheck should provision
    monkeypatch.setattr(
        "core.services.domain_reconciliation._resolve",
        fake_dns_resolve(cname=["cname.goat.plan4better.de."]),
    )

    r = await client.post(
        f"/api/v2/organizations/{seeded_org}/domains/{domain_id}/recheck"
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["dns_status"] == "verified"
    assert body["cert_status"] == "active"
    assert fake_provisioner.created == ["recheck.test.example.com"]


@pytest.mark.asyncio
async def test_delete_calls_teardown_for_active_domain(
    client: AsyncClient,
    seeded_org: str,
    fake_provisioner: FakeProvisioner,
    monkeypatch: pytest.MonkeyPatch,
    db_session: AsyncSession,
) -> None:
    monkeypatch.setattr(
        "core.services.domain_reconciliation._resolve",
        fake_dns_resolve(cname=["cname.goat.plan4better.de."]),
    )

    r = await client.post(
        f"/api/v2/organizations/{seeded_org}/domains/",
        json={"base_domain": "todelete.test.example.com"},
    )
    domain_id = r.json()["id"]
    assert len(fake_provisioner.created) == 1

    # Manually advance to ACTIVE (the cron would normally do this)
    from core.db.models.organization_domain import CertStatus, OrganizationDomain
    from sqlmodel import select

    result = await db_session.execute(
        select(OrganizationDomain).where(OrganizationDomain.id == UUID(domain_id))
    )
    row = result.scalar_one()
    row.cert_status = CertStatus.ACTIVE
    await db_session.commit()

    r = await client.delete(f"/api/v2/organizations/{seeded_org}/domains/{domain_id}")
    assert r.status_code == 204
    assert fake_provisioner.created == []


@pytest.mark.asyncio
async def test_delete_unknown_domain_404(
    client: AsyncClient,
    seeded_org: str,
    fake_provisioner: FakeProvisioner,
) -> None:
    fake_id = "00000000-0000-0000-0000-000000000099"
    r = await client.delete(f"/api/v2/organizations/{seeded_org}/domains/{fake_id}")
    assert r.status_code == 404


# ----- Project assignment tests -----


async def _create_active_domain(
    client: AsyncClient,
    seeded_org: str,
    base_domain: str,
    monkeypatch: pytest.MonkeyPatch,
    db_session: AsyncSession,
) -> str:
    """Helper: register a domain, advance it to ACTIVE state, return its id."""

    monkeypatch.setattr(
        "core.services.domain_reconciliation._resolve",
        fake_dns_resolve(cname=["cname.goat.plan4better.de."]),
    )

    r = await client.post(
        f"/api/v2/organizations/{seeded_org}/domains/",
        json={"base_domain": base_domain},
    )
    assert r.status_code == 201, r.text
    domain_id = r.json()["id"]

    # Manually flip cert_status to ACTIVE (the cron would do this in prod).
    from core.db.models.organization_domain import (
        CertStatus,
        OrganizationDomain,
    )
    from sqlmodel import select

    result = await db_session.execute(
        select(OrganizationDomain).where(OrganizationDomain.id == UUID(domain_id))
    )
    row = result.scalar_one()
    row.cert_status = CertStatus.ACTIVE
    await db_session.commit()
    return domain_id


@pytest.fixture
async def published_project_id(
    client: AsyncClient,
    fixture_create_folder: dict,
) -> str:
    """Create a project in the test folder and publish it; return its id."""
    project_payload = {
        "folder_id": fixture_create_folder["id"],
        "name": "Test Project For Custom Domain",
        "description": "",
        "initial_view_state": {
            "latitude": 48.1502132,
            "longitude": 11.5696284,
            "zoom": 12,
            "min_zoom": 0,
            "max_zoom": 20,
            "bearing": 0,
            "pitch": 0,
        },
    }
    r = await client.post("/api/v2/project", json=project_payload)
    assert r.status_code in (200, 201), r.text
    project_id = r.json()["id"]

    # Publish it
    r = await client.post(f"/api/v2/project/{project_id}/publish")
    assert r.status_code in (200, 201), r.text

    return project_id


@pytest.mark.asyncio
async def test_assign_custom_domain_to_project(
    client: AsyncClient,
    seeded_org: str,
    fake_provisioner: FakeProvisioner,
    monkeypatch: pytest.MonkeyPatch,
    db_session: AsyncSession,
    published_project_id: str,
) -> None:
    domain_id = await _create_active_domain(
        client, seeded_org, "assignme.test.example.com", monkeypatch, db_session
    )

    r = await client.post(
        f"/api/v2/project/{published_project_id}/public/custom-domain",
        json={"domain_id": domain_id},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["custom_domain_id"] == domain_id


@pytest.mark.asyncio
async def test_assign_rejects_inactive_domain(
    client: AsyncClient,
    seeded_org: str,
    fake_provisioner: FakeProvisioner,
    monkeypatch: pytest.MonkeyPatch,
    db_session: AsyncSession,
    published_project_id: str,
) -> None:
    """Domain whose cert_status is not ACTIVE cannot be assigned."""

    monkeypatch.setattr(
        "core.services.domain_reconciliation._resolve",
        fake_dns_resolve(),
    )

    r = await client.post(
        f"/api/v2/organizations/{seeded_org}/domains/",
        json={"base_domain": "pendingdomain.test.example.com"},
    )
    domain_id = r.json()["id"]

    r = await client.post(
        f"/api/v2/project/{published_project_id}/public/custom-domain",
        json={"domain_id": domain_id},
    )
    assert r.status_code == 400
    assert "active" in r.json()["detail"].lower()


@pytest.mark.asyncio
async def test_assign_404_for_unpublished_project(
    client: AsyncClient,
    seeded_org: str,
    fake_provisioner: FakeProvisioner,
    monkeypatch: pytest.MonkeyPatch,
    db_session: AsyncSession,
) -> None:
    domain_id = await _create_active_domain(
        client, seeded_org, "orphan.test.example.com", monkeypatch, db_session
    )
    fake_project_id = "00000000-0000-0000-0000-000000000099"

    r = await client.post(
        f"/api/v2/project/{fake_project_id}/public/custom-domain",
        json={"domain_id": domain_id},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_unassign_custom_domain_from_project(
    client: AsyncClient,
    seeded_org: str,
    fake_provisioner: FakeProvisioner,
    monkeypatch: pytest.MonkeyPatch,
    db_session: AsyncSession,
    published_project_id: str,
) -> None:
    domain_id = await _create_active_domain(
        client, seeded_org, "tounassign.test.example.com", monkeypatch, db_session
    )

    r = await client.post(
        f"/api/v2/project/{published_project_id}/public/custom-domain",
        json={"domain_id": domain_id},
    )
    assert r.status_code == 200

    r = await client.delete(
        f"/api/v2/project/{published_project_id}/public/custom-domain"
    )
    assert r.status_code == 204

    # Confirm it's gone
    from core.db.models.project import ProjectPublic
    from sqlmodel import select

    result = await db_session.execute(
        select(ProjectPublic).where(
            ProjectPublic.project_id == UUID(published_project_id)
        )
    )
    row = result.scalar_one_or_none()
    assert row is not None
    assert row.custom_domain_id is None


# ----- Anonymous lookup tests -----


@pytest.mark.asyncio
async def test_lookup_returns_project_id_for_active_assigned_domain(
    client: AsyncClient,
    seeded_org: str,
    fake_provisioner: FakeProvisioner,
    monkeypatch: pytest.MonkeyPatch,
    db_session: AsyncSession,
    published_project_id: str,
) -> None:
    base_domain = "lookup.test.example.com"
    domain_id = await _create_active_domain(
        client, seeded_org, base_domain, monkeypatch, db_session
    )

    r = await client.post(
        f"/api/v2/project/{published_project_id}/public/custom-domain",
        json={"domain_id": domain_id},
    )
    assert r.status_code == 200

    # No auth header needed - lookup is anonymous
    r = await client.get(
        "/api/v2/custom-domain-lookup",
        params={"host": base_domain},
    )
    assert r.status_code == 200
    assert r.json() == {"project_id": published_project_id}


@pytest.mark.asyncio
async def test_lookup_404_for_unknown_host(client: AsyncClient) -> None:
    r = await client.get(
        "/api/v2/custom-domain-lookup",
        params={"host": "unknown.test.example.com"},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_lookup_404_for_unassigned_domain(
    client: AsyncClient,
    seeded_org: str,
    fake_provisioner: FakeProvisioner,
    monkeypatch: pytest.MonkeyPatch,
    db_session: AsyncSession,
) -> None:
    """A domain that exists and is active, but isn't assigned to any project,
    must NOT be found by the lookup."""
    base_domain = "unassigned-active.test.example.com"
    await _create_active_domain(
        client, seeded_org, base_domain, monkeypatch, db_session
    )

    r = await client.get(
        "/api/v2/custom-domain-lookup",
        params={"host": base_domain},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_lookup_404_for_inactive_domain(
    client: AsyncClient,
    seeded_org: str,
    fake_provisioner: FakeProvisioner,
    monkeypatch: pytest.MonkeyPatch,
    db_session: AsyncSession,
    published_project_id: str,
) -> None:
    """If a domain is assigned but its cert is no longer active, lookup must 404."""
    base_domain = "inactive-assigned.test.example.com"
    domain_id = await _create_active_domain(
        client, seeded_org, base_domain, monkeypatch, db_session
    )

    r = await client.post(
        f"/api/v2/project/{published_project_id}/public/custom-domain",
        json={"domain_id": domain_id},
    )
    assert r.status_code == 200

    # Flip cert_status back to FAILED (simulate cert revocation / drift)
    from core.db.models.organization_domain import (
        CertStatus,
        OrganizationDomain,
    )
    from sqlmodel import select

    result = await db_session.execute(
        select(OrganizationDomain).where(OrganizationDomain.id == UUID(domain_id))
    )
    row = result.scalar_one()
    row.cert_status = CertStatus.FAILED
    await db_session.commit()

    r = await client.get(
        "/api/v2/custom-domain-lookup",
        params={"host": base_domain},
    )
    assert r.status_code == 404
