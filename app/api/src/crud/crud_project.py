from fastapi import HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import Params as PaginationParams
from src.db.models.project import Project
from src.schemas.project import (
    IProjectRead,
    IProjectBaseUpdate,
)
from uuid import UUID
from .base import CRUDBase
from src.schemas.common import OrderEnum
from fastapi_pagination import Page
from src.core.content import update_content_by_id


class CRUDProject(CRUDBase):
    async def get_projects(
        self,
        async_session: AsyncSession,
        user_id: UUID,
        page_params: PaginationParams,
        folder_id: UUID = None,
        search: str = None,
        order_by: str = None,
        order: OrderEnum = None,
        ids: list = None,
    ) -> Page[IProjectRead]:
        """Get projects for a user and folder"""

        # If ids are provided apply filter by ids, otherwise apply filter by folder_id and user_id
        if ids:
            query = select(Project).where(Project.id.in_(ids))
        else:
            query = select(Project).where(
                and_(
                    Project.user_id == user_id,
                    Project.folder_id == folder_id,
                )
            )

        projects = await self.get_multi(
            async_session,
            query=query,
            page_params=page_params,
            search_text={"name": search} if search else {},
            order_by=order_by,
            order=order,
        )

        if len(projects.items) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Projects Found")

        return projects

    async def update_base(
        self, async_session: AsyncSession, id: UUID, project: IProjectBaseUpdate
    ) -> IProjectRead:
        """Update project base"""

        # Update project
        project = await update_content_by_id(
            async_session=async_session,
            id=id,
            model=Project,
            crud_content=self,
            content_in=project,
        )

        return IProjectRead(**project.dict())


project = CRUDProject(Project)
