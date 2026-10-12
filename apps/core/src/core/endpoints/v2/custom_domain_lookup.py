"""Anonymous endpoints related to custom-domain serving + UX hints.

Two callers, two query-param names on the lookup:
- Next.js middleware passes ``?host=<header>`` — its native vocabulary.
- Caddy's on_demand_tls ``ask`` callback hardcodes ``?domain=<sni>`` and
  cannot be reconfigured. Both are accepted here and treated identically.

Must NOT require authentication and must be cheap to call (single indexed
JOIN). Returns 404 when the host is unknown, inactive, or not assigned to
a published project, and for every host while custom domains are off
(``CUSTOM_DOMAIN_CNAME_TARGET`` empty).
"""

from typing import Any, Dict, Optional

import dns.asyncresolver
import dns.exception
import dns.resolver
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select

from core.core.config import settings
from core.db.models.organization_domain import (
    CertStatus,
    OrganizationDomain,
)
from core.db.models.project import ProjectPublic
from core.db.session import AsyncSession
from core.endpoints.deps import get_db

router = APIRouter()


@router.get(
    "/custom-domain-config",
    summary="Public DNS config for the white-label feature",
)
async def custom_domain_config() -> Dict[str, Any]:
    """Public DNS pointers the AddDomain UI shows to admins.

    The CNAME target is the canonical hostname customers point subdomains at;
    ``apex_ipv4`` is the same target's resolved A record, used for apex
    domains where CNAME is illegal (RFC 1034). Resolving on every call keeps
    the UI in sync with whatever ``cname.goat.plan4better.de`` resolves to
    today, so an LB migration only needs the canonical record updated — no
    code or config redeploy.

    With custom domains off the target is empty and nothing is resolved.
    """
    if not settings.custom_domains_enabled:
        return {"cname_target": "", "apex_ipv4": None}
    target = settings.CUSTOM_DOMAIN_CNAME_TARGET
    apex_ipv4: Optional[str] = None
    try:
        # Use public resolvers for the same reason check_dns does — we
        # want to show customers what THEY see in DNS, not what the pod
        # sees through any split-DNS chain.
        resolver = dns.asyncresolver.Resolver(configure=False)
        resolver.nameservers = [
            ip.strip()
            for ip in settings.CUSTOM_DOMAIN_DNS_RESOLVERS.split(",")
            if ip.strip()
        ]
        resolver.lifetime = 5
        answer = await resolver.resolve(target, "A")
        apex_ipv4 = next((str(rdata).strip() for rdata in answer), None)
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.DNSException):
        # Fail soft: subdomain customers don't need apex_ipv4, and the UI
        # can omit the apex hint when it's unavailable.
        apex_ipv4 = None
    return {"cname_target": target, "apex_ipv4": apex_ipv4}


@router.get(
    "/custom-domain-lookup",
    summary="Resolve a custom domain hostname to a published project ID",
)
async def custom_domain_lookup(
    host: Optional[str] = Query(None, max_length=253),
    domain: Optional[str] = Query(None, max_length=253),
    async_session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Anonymous: returns ``{project_id}`` for an active assigned host, else 404.

    Accepts either ``?host=`` (Next.js) or ``?domain=`` (Caddy). Caddy treats
    any 2xx as "issue the cert"; the response body is irrelevant to it.
    """
    raw = host if host is not None else domain
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="missing 'host' or 'domain' query parameter",
        )
    host = raw.strip().lower()
    if not settings.custom_domains_enabled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="custom domains are not enabled",
        )

    result = await async_session.execute(
        select(ProjectPublic.project_id)
        .join(
            OrganizationDomain,
            OrganizationDomain.id == ProjectPublic.custom_domain_id,
        )
        .where(
            OrganizationDomain.base_domain == host,
            OrganizationDomain.cert_status == CertStatus.ACTIVE,
        )
    )
    project_id = result.scalar_one_or_none()
    if project_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="no project assigned to this host",
        )
    return {"project_id": str(project_id)}
