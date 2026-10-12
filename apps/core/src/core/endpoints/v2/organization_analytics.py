"""User-facing endpoints for the organization's analytics instances.

An organization can register any number of instances (e.g. its own Matomo
plus one per client); dashboards pick one in the Share dialog. Access is
enforced by ``auth_z``: ``read-organization`` to list, ``update-organization``
(organization admins and owners) to change, and the organization in the path
must be the caller's own. The router is mounted under ``/organizations`` with
the rest of the path on each route, so ``route_pattern`` keeps
``{organization_id}`` as a placeholder.
"""

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from pydantic import UUID4

from core.crud.crud_organization_analytics import (
    organization_analytics as crud,
)
from core.db.session import AsyncSession
from core.deps.auth import auth_z
from core.endpoints.deps import get_db, get_user_id
from core.schemas.organization_analytics import (
    AnalyticsDashboardRead,
    AnalyticsDashboardsUpdate,
    OrganizationAnalyticsCreate,
    OrganizationAnalyticsRead,
)

router = APIRouter()


@router.get(
    "/{organization_id}/analytics/",
    summary="List the organization's analytics instances",
    response_model=list[OrganizationAnalyticsRead],
    dependencies=[Depends(auth_z)],
)
async def list_analytics(
    *,
    organization_id: UUID4 = Path(...),
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID4 = Depends(get_user_id),
) -> list[OrganizationAnalyticsRead]:
    """Each instance carries ``usage_count`` — how many published dashboards
    currently report to it — so the UI can hint at reuse before assigning."""
    rows = await crud.list_by_organization(
        async_session, organization_id=organization_id
    )
    return [
        OrganizationAnalyticsRead.model_validate(row).model_copy(
            update={"usage_count": count}
        )
        for row, count in rows
    ]


@router.post(
    "/{organization_id}/analytics/",
    summary="Create an analytics instance",
    response_model=OrganizationAnalyticsRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(auth_z)],
)
async def create_analytics(
    *,
    organization_id: UUID4 = Path(...),
    payload: OrganizationAnalyticsCreate = Body(...),
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID4 = Depends(get_user_id),
) -> OrganizationAnalyticsRead:
    row = await crud.create_instance(
        async_session,
        organization_id=organization_id,
        name=payload.name,
        provider=payload.provider.value,
        # The discriminated union validates fields; persist the plain dict
        # form (HttpUrl serializes to string via mode="json").
        config=payload.config.model_dump(mode="json", exclude={"provider"}),
    )
    return OrganizationAnalyticsRead.model_validate(row)


@router.put(
    "/{organization_id}/analytics/{analytics_id}",
    summary="Update an analytics instance",
    response_model=OrganizationAnalyticsRead,
    dependencies=[Depends(auth_z)],
)
async def update_analytics(
    *,
    organization_id: UUID4 = Path(...),
    analytics_id: UUID4 = Path(...),
    payload: OrganizationAnalyticsCreate = Body(...),
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID4 = Depends(get_user_id),
) -> OrganizationAnalyticsRead:
    """Full replace of the instance's name, provider, and config."""
    row = await crud.update_instance(
        async_session,
        organization_id=organization_id,
        analytics_id=analytics_id,
        name=payload.name,
        provider=payload.provider.value,
        config=payload.config.model_dump(mode="json", exclude={"provider"}),
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="analytics instance not found",
        )
    return OrganizationAnalyticsRead.model_validate(row)


@router.delete(
    "/{organization_id}/analytics/{analytics_id}",
    summary="Delete an analytics instance",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(auth_z)],
)
async def delete_analytics(
    *,
    organization_id: UUID4 = Path(...),
    analytics_id: UUID4 = Path(...),
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID4 = Depends(get_user_id),
) -> None:
    """Dashboards referencing this instance keep working but stop tracking:
    the FK is ON DELETE SET NULL, so their ``analytics_id`` is cleared."""
    deleted = await crud.delete_instance(
        async_session,
        organization_id=organization_id,
        analytics_id=analytics_id,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="analytics instance not found",
        )


@router.get(
    "/{organization_id}/analytics/dashboards",
    summary="List the organization's published dashboards and their analytics assignment",
    response_model=list[AnalyticsDashboardRead],
    dependencies=[Depends(auth_z)],
)
async def list_analytics_dashboards(
    *,
    organization_id: UUID4 = Path(...),
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID4 = Depends(get_user_id),
) -> list[AnalyticsDashboardRead]:
    """Only published dashboards appear — unpublished projects have no
    public row, so there is nothing to assign."""
    rows = await crud.list_org_dashboards(
        async_session, organization_id=organization_id
    )
    return [
        AnalyticsDashboardRead(project_id=pid, name=name, analytics_id=aid)
        for pid, name, aid in rows
    ]


@router.put(
    "/{organization_id}/analytics/{analytics_id}/dashboards",
    summary="Set which dashboards report to an analytics instance",
    response_model=list[AnalyticsDashboardRead],
    dependencies=[Depends(auth_z)],
)
async def set_analytics_dashboards(
    *,
    organization_id: UUID4 = Path(...),
    analytics_id: UUID4 = Path(...),
    payload: AnalyticsDashboardsUpdate = Body(...),
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID4 = Depends(get_user_id),
) -> list[AnalyticsDashboardRead]:
    """Reconcile-style bulk assignment: the body is the desired complete
    set for this instance. Listed dashboards are assigned (reassignment
    from another instance included); dashboards currently on this instance
    but unlisted are cleared. Consent settings are untouched."""
    instance = await crud.get_for_organization(
        async_session,
        organization_id=organization_id,
        analytics_id=analytics_id,
    )
    if instance is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="analytics instance not found",
        )
    try:
        await crud.set_instance_dashboards(
            async_session,
            organization_id=organization_id,
            analytics_id=analytics_id,
            project_ids=payload.project_ids,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"not published dashboards of this organization: {exc}",
        ) from exc
    rows = await crud.list_org_dashboards(
        async_session, organization_id=organization_id
    )
    return [
        AnalyticsDashboardRead(project_id=pid, name=name, analytics_id=aid)
        for pid, name, aid in rows
    ]
