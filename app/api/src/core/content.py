from typing import Callable, List, Type
from fastapi import Depends, HTTPException, status
from fastapi_pagination import Params as PaginationParams
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.sql import Select
from sqlmodel import SQLModel

from src.db.session import AsyncSession
from src.schemas.common import ContentIdList
from src.db.models._link_model import LayerProjectLink
from src.db.models.layer import Layer

### Generic helper functions for content
async def create_content(
    async_session: AsyncSession,
    *,
    model: Type[SQLModel],
    crud_content: Callable,
    content_in: SQLModel,
    other_params: dict = {},
) -> SQLModel:
    """Create a new content."""
    content_in = model(**content_in.dict(exclude_none=True), **other_params)
    content = await crud_content.create(async_session, obj_in=content_in)
    return content


async def read_content_by_id(
    async_session: AsyncSession,
    id: UUID4,
    model: Type[SQLModel],
    crud_content: Callable,
    extra_fields: List = [],
) -> SQLModel:
    """Read a content by its ID."""
    content = await crud_content.get(async_session, id=id, extra_fields=extra_fields)

    if content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{model.__name__} not found"
        )

    return content


async def read_contents_by_ids(
    async_session: AsyncSession,
    ids: ContentIdList,
    model: Type[SQLModel],
    crud_content: Callable,
    page_params: PaginationParams = Depends(),
) -> Select:
    """Read contents by their IDs."""
    # Read contents by IDs
    query = select(model).where(model.id.in_(ids.ids))
    contents = await crud_content.get_multi(async_session, query=query, page_params=page_params)

    # Check if all contents were found
    if len(contents.items) != len(ids.ids):
        not_found_contents = [
            content_id
            for content_id in ids.ids
            if content_id not in [content.id for content in contents.items]
        ]
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} with {not_found_contents} not found",
        )

    return contents


async def update_content_by_id(
    async_session: AsyncSession,
    id: UUID4,
    model: Type[SQLModel],
    crud_content: Callable,
    content_in: SQLModel,
) -> SQLModel:
    """Update a content by its ID."""
    db_obj = await crud_content.get(async_session, id=id)
    if db_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{model.__name__} not found"
        )
    content = await crud_content.update(async_session, db_obj=db_obj, obj_in=content_in)
    return content


async def delete_content_by_id(
    async_session: AsyncSession,
    id: UUID4,
    model: Type[SQLModel],
    crud_content: Callable,
) -> None:
    """Delete a content by its ID."""
    db_obj = await crud_content.get(async_session, id=id)
    if db_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{model.__name__} not found"
        )
    await crud_content.remove(async_session, id=id)
    return