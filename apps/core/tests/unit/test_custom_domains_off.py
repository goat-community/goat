"""An empty CUSTOM_DOMAIN_CNAME_TARGET switches the custom-domain feature off."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from core.core.config import settings
from core.endpoints.v2 import custom_domain_lookup, organization_domain
from core.schemas.organization_domain import OrganizationDomainCreate
from core.scripts import reconcile_domains
from fastapi import HTTPException


@pytest.fixture(autouse=True)
def _feature_off(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "CUSTOM_DOMAIN_CNAME_TARGET", "")


def _unused_session() -> MagicMock:
    session = MagicMock()
    session.execute = AsyncMock(side_effect=AssertionError("no query expected"))
    session.flush = AsyncMock(side_effect=AssertionError("no insert expected"))
    return session


@pytest.mark.unit
async def test_config_reports_no_target_without_resolving(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    resolver = MagicMock(side_effect=AssertionError("no DNS lookup expected"))
    monkeypatch.setattr(custom_domain_lookup.dns.asyncresolver, "Resolver", resolver)
    assert await custom_domain_lookup.custom_domain_config() == {
        "cname_target": "",
        "apex_ipv4": None,
    }


@pytest.mark.unit
async def test_lookup_is_not_found() -> None:
    with pytest.raises(HTTPException) as exc:
        await custom_domain_lookup.custom_domain_lookup(
            host="maps.example.org", domain=None, async_session=_unused_session()
        )
    assert exc.value.status_code == 404


@pytest.mark.unit
async def test_lookup_still_requires_a_host() -> None:
    with pytest.raises(HTTPException) as exc:
        await custom_domain_lookup.custom_domain_lookup(
            host=None, domain=None, async_session=_unused_session()
        )
    assert exc.value.status_code == 422


@pytest.mark.unit
async def test_create_domain_is_refused() -> None:
    session = _unused_session()
    with pytest.raises(HTTPException) as exc:
        await organization_domain.create_domain(
            organization_id=uuid4(),
            payload=OrganizationDomainCreate(base_domain="maps.example.org"),
            async_session=session,
            user_id=uuid4(),
            provisioner=MagicMock(),
        )
    assert exc.value.status_code == 400
    assert "CUSTOM_DOMAIN_CNAME_TARGET" in exc.value.detail
    session.add.assert_not_called()


@pytest.mark.unit
async def test_recheck_domain_is_refused() -> None:
    with pytest.raises(HTTPException) as exc:
        await organization_domain.recheck_domain(
            organization_id=uuid4(),
            domain_id=uuid4(),
            async_session=_unused_session(),
            user_id=uuid4(),
            provisioner=MagicMock(),
        )
    assert exc.value.status_code == 400


@pytest.mark.unit
async def test_reconcile_skips_without_touching_the_database(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    init = MagicMock(side_effect=AssertionError("no database expected"))
    monkeypatch.setattr(reconcile_domains.session_manager, "init", init)
    assert await reconcile_domains.reconcile() == (0, 0)
