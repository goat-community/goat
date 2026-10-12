from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4, BaseModel
from sqlalchemy import select

from core.crud.crud_organization_analytics import (
    organization_analytics as crud_organization_analytics,
)
from core.crud.crud_organization_domain import (
    organization_domain as crud_organization_domain,
)
from core.crud.crud_project import project as crud_project
from core.db.models.organization_domain import CertStatus
from core.db.models.project import Project, ProjectPublic
from core.db.models.user import User
from core.db.session import AsyncSession
from core.deps.auth import auth_z
from core.endpoints.deps import get_db, get_user_id
from core.schemas.project import ProjectPublicRead

router = APIRouter()


@router.get(
    "/{project_id}/public",
    summary="Get public project",
    response_model=ProjectPublicRead,
    response_model_exclude_none=True,
)
async def get_public_project(
    project_id: str,
    async_session: AsyncSession = Depends(get_db),
) -> ProjectPublicRead:
    """Get the public config for a published project.

    404 both when the project was never published and when it has since
    been unpublished (a soft delete unpublishes the project) — a project's
    public page must never keep resolving after either.
    """
    result = await crud_project.get_public_project(
        async_session=async_session, project_id=project_id
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    return result


@router.post(
    "/{project_id}/publish",
    summary="Publish a project",
    dependencies=[Depends(auth_z)],
)
async def publish_project(
    project_id: str,
    user_id: UUID4 = Depends(get_user_id),
    async_session: AsyncSession = Depends(get_db),
) -> ProjectPublicRead:
    """
    Publish a project
    """
    # 404 if the project itself is trashed — publishing
    # a project nobody can see must not resurrect a public page for it.
    await crud_project.get_live_or_404(async_session, UUID(project_id))

    result = ProjectPublicRead.model_validate(
        await crud_project.publish_project(
            async_session=async_session, project_id=project_id, user_id=user_id
        )
    )

    return result


@router.delete(
    "/{project_id}/unpublish",
    summary="Unpublish a project",
    dependencies=[Depends(auth_z)],
)
async def unpublish_project(
    project_id: str,
    async_session: AsyncSession = Depends(get_db),
) -> None:
    """
    Unpublish a project
    """
    # 404 if the project itself is trashed. A delete
    # already unpublishes internally (crud_project.delete) — this only
    # guards a direct call to this endpoint against an already-trashed
    # project.
    await crud_project.get_live_or_404(async_session, UUID(project_id))

    await crud_project.unpublish_project(
        async_session=async_session, project_id=project_id
    )


##############################################
### Custom domain assignment endpoints
##############################################


class AssignCustomDomainPayload(BaseModel):
    """Body of POST /project/{project_id}/public/custom-domain."""

    domain_id: UUID4


@router.post(
    "/{project_id}/public/custom-domain",
    summary="Assign a custom domain to a published project",
    dependencies=[Depends(auth_z)],
)
async def assign_custom_domain(
    project_id: str,
    payload: AssignCustomDomainPayload,
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID4 = Depends(get_user_id),
) -> ProjectPublicRead:
    """Bind an active custom domain to a published project."""
    # 404 if the project itself is trashed.
    await crud_project.get_live_or_404(async_session, UUID(project_id))

    result = await async_session.execute(
        select(ProjectPublic).where(ProjectPublic.project_id == UUID(project_id))
    )
    project_public = result.scalar_one_or_none()
    if project_public is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="project is not published",
        )

    domain = await crud_organization_domain.get(async_session, id=payload.domain_id)
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="domain not found",
        )
    if domain.cert_status != CertStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="domain must be active before assignment",
        )

    project_public.custom_domain_id = payload.domain_id
    await async_session.commit()
    await async_session.refresh(project_public)
    return ProjectPublicRead.model_validate(project_public)


@router.delete(
    "/{project_id}/public/custom-domain",
    summary="Unassign the custom domain from a published project",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(auth_z)],
)
async def unassign_custom_domain(
    project_id: str,
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID4 = Depends(get_user_id),
) -> None:
    """Clear the custom-domain assignment from a published project."""
    # 404 if the project itself is trashed.
    await crud_project.get_live_or_404(async_session, UUID(project_id))

    result = await async_session.execute(
        select(ProjectPublic).where(ProjectPublic.project_id == UUID(project_id))
    )
    project_public = result.scalar_one_or_none()
    if project_public is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="project is not published",
        )

    project_public.custom_domain_id = None
    await async_session.commit()


class TrackingSettingsPayload(BaseModel):
    """Body of PUT /project/{project_id}/public/tracking.

    Fields are updated independently — clients can send either or both.
    ``analytics_id`` selects which of the org's analytics instances this
    dashboard reports to; explicit null switches tracking off.
    ``require_consent`` controls whether the tracker waits for the
    visitor's consent banner.
    """

    analytics_id: UUID4 | None = None
    require_consent: bool | None = None


@router.put(
    "/{project_id}/public/tracking",
    summary="Update analytics tracking settings for a published project",
    dependencies=[Depends(auth_z)],
)
async def set_tracking_settings(
    project_id: str,
    payload: TrackingSettingsPayload,
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID4 = Depends(get_user_id),
) -> ProjectPublicRead:
    """Assign an analytics instance to a published project (or clear it).

    The instance must belong to the project owner's organization. Presence
    of ``analytics_id`` in the body is detected via ``model_fields_set`` so
    an explicit null (= tracking off) is distinguishable from omission.
    """
    # 404 if the project itself is trashed.
    await crud_project.get_live_or_404(async_session, UUID(project_id))

    if not payload.model_fields_set:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="at least one of 'analytics_id' or 'require_consent' is required",
        )

    result = await async_session.execute(
        select(ProjectPublic).where(ProjectPublic.project_id == UUID(project_id))
    )
    project_public = result.scalar_one_or_none()
    if project_public is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="project is not published",
        )

    if "analytics_id" in payload.model_fields_set:
        if payload.analytics_id is None:
            project_public.analytics_id = None
        else:
            analytics_row = await crud_organization_analytics.get(
                async_session, id=payload.analytics_id
            )
            if analytics_row is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="analytics instance not found",
                )
            owner_org_id = (
                await async_session.execute(
                    select(User.organization_id)
                    .join(Project, Project.user_id == User.id)
                    .where(Project.id == UUID(project_id))
                )
            ).scalar_one_or_none()
            if owner_org_id is None or analytics_row.organization_id != owner_org_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "analytics instance does not belong to the project "
                        "owner's organization"
                    ),
                )
            project_public.analytics_id = payload.analytics_id

    if payload.require_consent is not None:
        project_public.tracking_require_consent = payload.require_consent

    await async_session.commit()
    await async_session.refresh(project_public)
    return ProjectPublicRead.model_validate(project_public)
