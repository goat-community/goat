from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from fastapi_pagination import Page
from fastapi_pagination import Params as PaginationParams
from pydantic import UUID4
from sqlalchemy import select

from src.crud.crud_folder import folder as crud_folder
from src.db.models.folder import Folder
from src.db.session import AsyncSession
from src.endpoints.deps import get_db, get_user_id
from src.schemas.common import OrderEnum
from src.schemas.folder import (
    FolderCreate,
    FolderRead,
    FolderUpdate,
    request_examples as folder_request_examples,
)

router = APIRouter()


### Folder endpoints
@router.post(
    "",
    summary="Create a new folder",
    response_model=FolderRead,
    status_code=201,
)
async def create_folder(
    *,
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID4 = Depends(get_user_id),
    folder_in: FolderCreate = Body(..., example=folder_request_examples["create"]),
):
    """Create a new folder."""
    folder_in.user_id = user_id
    folder = await crud_folder.create(async_session, obj_in=folder_in)
    return folder


@router.get(
    "/{folder_id}",
    summary="Retrieve a folder by its ID",
    response_model=FolderRead,
    status_code=200,
)
async def read_folder(
    *,
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID4 = Depends(get_user_id),
    folder_id: UUID4 = Path(
        ...,
        description="The ID of the folder to get",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
):
    """Retrieve a folder by its ID."""
    folder = await crud_folder.get_by_multi_keys(
        async_session, keys={"id": folder_id, "user_id": user_id}
    )

    if len(folder) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found")

    return folder[0]


@router.get(
    "",
    summary="Retrieve a list of folders",
    response_model=Page[FolderRead],
    response_model_exclude_none=True,
    status_code=200,
)
async def read_folders(
    *,
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID4 = Depends(get_user_id),
    page_params: PaginationParams = Depends(),
    search: str = Query(None, description="Searches the name of the folder"),
    order_by: str = Query(
        None,
        description="Specify the column name that should be used to order. You can check the Project model to see which column names exist.",
        example="created_at",
    ),
    order: OrderEnum = Query(
        "ascendent",
        description="Specify the order to apply. There are the option ascendent or descendent.",
        example="ascendent",
    ),
):
    """Retrieve a list of folders."""
    query = select(Folder).where(Folder.user_id == user_id)
    folders = await crud_folder.get_multi(
        async_session,
        query=query,
        page_params=page_params,
        search_text={"name": search} if search else {},
        order_by=order_by,
        order=order,
    )

    if len(folders.items) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Folders Found")

    return folders


@router.put(
    "/{folder_id}",
    summary="Update a folder with new data",
    response_model=FolderUpdate,
    status_code=200,
)
async def update_folder(
    *,
    async_session: AsyncSession = Depends(get_db),
    folder_id: UUID4 = Path(
        ...,
        description="The ID of the folder to update",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
    user_id: UUID4 = Depends(get_user_id),
    folder_in: FolderUpdate = Body(..., example=folder_request_examples["update"]),
):
    """Update a folder with new data."""
    db_obj = await crud_folder.get_by_multi_keys(
        async_session, keys={"id": folder_id, "user_id": user_id}
    )

    if len(db_obj) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found")

    folder = await crud_folder.update(async_session, db_obj=db_obj[0], obj_in=folder_in)
    return folder


@router.delete(
    "/{folder_id}",
    summary="Delete a folder and all its contents",
    response_model=None,
    status_code=204,
)
async def delete_folder(
    *,
    async_session: AsyncSession = Depends(get_db),
    folder_id: UUID4 = Path(
        ...,
        description="The ID of the folder to delete",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
    user_id: UUID4 = Depends(get_user_id),
):
    """Delete a folder and all its contents"""
    db_obj = await crud_folder.get_by_multi_keys(
        async_session, keys={"id": folder_id, "user_id": user_id}
    )
    # Check if folder exists
    if len(db_obj) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found")

    await crud_folder.remove(async_session, id=db_obj[0].id)
    return

