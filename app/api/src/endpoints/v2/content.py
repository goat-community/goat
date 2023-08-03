from typing import Callable, List, Type

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from fastapi_pagination import Page
from fastapi_pagination import Params as PaginationParams
from pydantic import UUID4
from sqlalchemy import and_, or_, select
from sqlalchemy.sql import Select
from sqlmodel import SQLModel

from src.crud.crud_folder import folder as crud_folder
from src.crud.crud_layer import layer as crud_layer
from src.crud.crud_project import project as crud_project
from src.crud.crud_report import report as crud_report
from src.db.models.folder import Folder
from src.db.models.layer import FeatureLayerType, Layer, LayerType
from src.db.models.project import Project
from src.db.models.report import Report
from src.db.session import AsyncSession
from src.endpoints.deps import get_db, get_user_id
from src.schemas.common import ContentIdList, OrderEnum
from src.schemas.folder import (
    FolderCreate,
    FolderRead,
    FolderUpdate,
    request_examples as folder_request_examples,
)
from src.schemas.layer import (
    ILayerCreate,
    ILayerRead,
    ILayerUpdate,
)
from src.schemas.layer import (
    request_examples as layer_request_examples,
)
from src.schemas.project import (
    IProjectCreate,
    IProjectRead,
    initial_view_state_example,
    request_examples as project_request_examples,
)
from src.schemas.report import (
    IReportCreate,
    IReportRead,
    IReportUpdate,
    request_examples as report_request_examples,
)
from src.db.models._link_model import LayerProjectLink

router = APIRouter()


### Folder endpoints
@router.post(
    "/content/folder",
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
    "/content/folder/{folder_id}",
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
    "/content/folder",
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
):
    """Retrieve a list of folders."""
    query = select(Folder).where(Folder.user_id == user_id)
    folders = await crud_folder.get_multi(
        async_session,
        query=query,
        page_params=page_params,
        search_text={"name": search} if search else {},
    )

    if len(folders.items) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Folders Found")

    return folders


@router.put(
    "/content/folder/{folder_id}",
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
    "/content/folder/{folder_id}",
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
    db_obj = await crud_content.get(async_session, id=id)
    if db_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{model.__name__} not found"
        )
    await crud_content.remove(async_session, id=id)
    return


## Layer endpoints
@router.post(
    "/content/layer",
    summary="Create a new layer",
    response_model=ILayerRead,
    response_model_exclude_none=True,
    status_code=201,
)
async def create_layer(
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID4 = Depends(get_user_id),
    layer_in: ILayerCreate = Body(
        ..., examples=layer_request_examples["create"], description="Layer to create"
    ),
):
    """Create a new layer."""
    return await create_content(
        async_session=async_session,
        model=Layer,
        crud_content=crud_layer,
        content_in=layer_in,
        other_params={"user_id": user_id},
    )


@router.get(
    "/layer/{id}",
    summary="Retrieve a layer by its ID",
    response_model=ILayerRead,
    response_model_exclude_none=True,
    status_code=200,
)
async def read_layer(
    async_session: AsyncSession = Depends(get_db),
    id: UUID4 = Path(
        ...,
        description="The ID of the layer to get",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
):
    """Retrieve a layer by its ID."""
    return await read_content_by_id(
        async_session=async_session, id=id, model=Layer, crud_content=crud_layer
    )


@router.post(
    "/layer/get-by-ids",
    summary="Retrieve a list of layers by their IDs",
    response_model=Page[ILayerRead],
    response_model_exclude_none=True,
    status_code=200,
)
async def read_layers_by_ids(
    async_session: AsyncSession = Depends(get_db),
    page_params: PaginationParams = Depends(),
    ids: ContentIdList = Body(
        ...,
        example=layer_request_examples["get"],
        description="List of layer IDs to retrieve",
    ),
):
    return await read_contents_by_ids(
        async_session=async_session,
        ids=ids,
        model=Layer,
        crud_content=crud_layer,
        page_params=page_params,
    )


@router.get(
    "/layer",
    response_model=Page[ILayerRead],
    response_model_exclude_none=True,
    status_code=200,
    summary="Retrieve a list of layers using different filters",
)
async def read_layers(
    async_session: AsyncSession = Depends(get_db),
    page_params: PaginationParams = Depends(),
    folder_id: UUID4 = Query(..., description="Folder ID"),
    user_id: UUID4 = Depends(get_user_id),
    layer_type: List[LayerType]
    | None = Query(
        None,
        description="Layer type to filter by. Can be multiple. If not specified, all layer types will be returned.",
    ),
    feature_layer_type: List[FeatureLayerType]
    | None = Query(
        None,
        description="Feature layer type. Can be multiple. If not specified, all feature layer types will be returned. Can only be used if 'layer_type' contains 'feature_layer'.",
    ),
    search: str = Query(
        None,
        description="Searches the 'name' column of the layer. It will convert the text into lower case and see if the passed text is part of the name.",
        example="Münch",
    ),
    order_by: str = Query(
        None,
        description="Specify the column name that should be used to order. You can check the Layer model to see which column names exist.",
        example="created_at",
    ),
    order: OrderEnum = Query(
        "ascendent",
        description="Specify the order to apply. There are the option ascendent or descendent.",
        example="ascendent",
    ),
):
    """This endpoints returns a list of layers based one the specified filters."""

    # Additional server side validation for feature_layer_type
    if feature_layer_type is not None and LayerType.feature_layer not in layer_type:
        raise HTTPException(
            status_code=400,
            detail="Feature layer type can only be set when layer type is feature_layer",
        )
    # TODO: Put this in CRUD layer
    sql_and_filters = [Layer.user_id == user_id, Layer.folder_id == folder_id]

    # Add conditions to filter by layer_type and feature_layer_type
    if layer_type is not None:
        sql_and_filters.append(or_(Layer.type.in_(layer_type)))

    if feature_layer_type is not None:
        sql_and_filters.append(or_(Layer.feature_layer_type.in_(feature_layer_type)))

    # Build query
    query = select(Layer).where(and_(*sql_and_filters))

    # Build params
    params = {
        "search_text": {"name": search} if search else None,
        "order_by": order_by,
        "order": order,
    }

    # Filter out None values
    params = {k: v for k, v in params.items() if v is not None}

    layers = await crud_layer.get_multi(
        async_session,
        query=query,
        page_params=page_params,
        **params,
    )

    if len(layers.items) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Layers Found")

    return layers


@router.put(
    "/layer/{id}",
    response_model=ILayerRead,
    response_model_exclude_none=True,
    status_code=200,
)
async def update_layer(
    async_session: AsyncSession = Depends(get_db),
    id: UUID4 = Path(
        ...,
        description="The ID of the layer to get",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
    layer_in: ILayerUpdate = Body(
        ..., examples=layer_request_examples["update"], description="Layer to update"
    ),
):
    return await update_content_by_id(
        async_session=async_session,
        id=id,
        model=Layer,
        crud_content=crud_layer,
        content_in=layer_in,
    )


@router.delete(
    "/layer/{id}",
    response_model=None,
    status_code=204,
)
async def delete_layer(
    async_session: AsyncSession = Depends(get_db),
    id: UUID4 = Path(
        ...,
        description="The ID of the layer to get",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
):
    return await delete_content_by_id(
        async_session=async_session, id=id, model=Layer, crud_content=crud_layer
    )


### Project endpoints
@router.post(
    "/project",
    summary="Create a new project",
    response_model=IProjectRead,
    response_model_exclude_none=True,
    status_code=201,
)
async def create_project(
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID4 = Depends(get_user_id),
    *,
    project_in: IProjectCreate = Body(
        ..., example=project_request_examples["create"], description="Project to create"
    ),
):
    """This will create an empty project with a default initial view state. The project does not contains layers or reports."""
    project = await create_content(
        async_session=async_session,
        model=Project,
        crud_content=crud_project,
        content_in=project_in,
        other_params={"user_id": user_id, "initial_view_state": initial_view_state_example},
    )
    # Doing unneded typed conversion to make sure the relations of project are not loaded
    return IProjectRead(**project.dict())


@router.get(
    "/project/{id}",
    summary="Retrieve a project by its ID",
    response_model=IProjectRead,
    response_model_exclude_none=True,
    status_code=200,
)
async def read_project(
    async_session: AsyncSession = Depends(get_db),
    id: UUID4 = Path(
        ...,
        description="The ID of the project to get",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
):
    """Retrieve a project by its ID."""

    # TODO: Move parts into crud_project
    project = await crud_project.get(async_session, id=id, extra_fields=[Project.reports])

    project = IProjectRead(**project.dict(), reports=project.reports)
    # Get layer from project
    layers = await crud_layer.get_multi(
        async_session,
        query=select(Layer)
        .join(LayerProjectLink)
        .where(and_(LayerProjectLink.project_id == id, LayerProjectLink.layer_id == Layer.id)),
    )

    # Add layer to project
    project.layers = layers
    return project


@router.get(
    "/project",
    summary="Retrieve a list of projects",
    response_model=Page[IProjectRead],
    response_model_exclude_none=True,
    status_code=200,
)
async def read_projects(
    async_session: AsyncSession = Depends(get_db),
    page_params: PaginationParams = Depends(),
    user_id: UUID4 = Depends(get_user_id),
    search: str = Query(None, description="Searches the name of the project"),
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
    """Retrieve a list of projects."""
    query = select(Project).where(Project.user_id == user_id)
    projects = await crud_project.get_multi(
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


@router.post(
    "/project/get-by-ids",
    summary="Retrieve a list of projects by their IDs",
    response_model=Page[IProjectRead],
    response_model_exclude_none=True,
    status_code=200,
)
async def read_projects_by_ids(
    async_session: AsyncSession = Depends(get_db),
    page_params: PaginationParams = Depends(),
    ids: ContentIdList = Body(
        ...,
        example=project_request_examples["get"],
        description="List of project IDs to retrieve",
    ),
):
    return await read_contents_by_ids(
        async_session=async_session,
        ids=ids,
        model=Project,
        crud_content=crud_project,
        page_params=page_params,
    )


# TODO: Finish PUT endpoint
# @router.put(
#     "/project/{}/{id}",
#     response_model=IProjectRead,
#     response_model_exclude_none=True,
#     status_code=200,
# )
# async def update_project(
#     async_session: AsyncSession = Depends(get_db),
#     id: UUID4 = Path(
#         ...,
#         description="The ID of the project to get",
#         example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
#     ),
#     project_in: IProjectUpdate = Body(
#         ..., example=project_request_examples["update"], description="Project to update"
#     ),
# ):
#     return await update_content_by_id(
#         Project, IProjectUpdate, get_db, crud_project, id, async_session, project_in
#     )
# # TODO: Read all contents with filters


@router.delete(
    "/project/{id}",
    response_model=None,
    status_code=204,
)
async def delete_project(
    async_session: AsyncSession = Depends(get_db),
    id: UUID4 = Path(
        ...,
        description="The ID of the project to get",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
):
    return await delete_content_by_id(
        async_session=async_session, id=id, model=Project, crud_content=crud_project
    )


# Report endpoints
@router.post(
    "/report",
    summary="Create a new report",
    response_model=IReportRead,
    response_model_exclude_none=True,
    status_code=201,
)
async def create_report(
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID4 = Depends(get_user_id),
    *,
    report_in: IReportCreate = Body(
        ..., example=report_request_examples["create"], description="Project to create"
    ),
):
    """This will create an empty report."""
    return await create_content(
        async_session=async_session,
        model=Report,
        crud_content=crud_report,
        content_in=report_in,
        other_params={"user_id": user_id},
    )


@router.post(
    "/report/get-by-ids",
    summary="Retrieve a list of reports by their IDs",
    response_model=Page[IReportRead],
    response_model_exclude_none=True,
    status_code=200,
)
async def read_reports_by_ids(
    async_session: AsyncSession = Depends(get_db),
    page_params: PaginationParams = Depends(),
    ids: ContentIdList = Body(
        ...,
        example=report_request_examples["get"],
        description="List of report IDs to retrieve",
    ),
):
    return await read_contents_by_ids(
        async_session=async_session,
        ids=ids,
        model=Report,
        crud_content=crud_report,
        page_params=page_params,
    )


@router.get(
    "/report/{id}",
    summary="Retrieve a report by its ID",
    response_model=IReportRead,
    response_model_exclude_none=True,
    status_code=200,
)
async def read_report(
    async_session: AsyncSession = Depends(get_db),
    id: UUID4 = Path(
        ...,
        description="The ID of the report to get",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
):
    """Retrieve a report by its ID."""
    return await read_content_by_id(
        async_session=async_session, id=id, model=Report, crud_content=crud_report
    )


@router.get(
    "/report",
    summary="Retrieve a list of reports",
    response_model=Page[IReportRead],
    response_model_exclude_none=True,
    status_code=200,
)
async def read_reports(
    async_session: AsyncSession = Depends(get_db),
    page_params: PaginationParams = Depends(),
    user_id: UUID4 = Depends(get_user_id),
    search: str = Query(None, description="Searches the name of the report"),
    order_by: str = Query(
        None,
        description="Specify the column name that should be used to order. You can check the Report model to see which column names exist.",
        example="created_at",
    ),
    order: OrderEnum = Query(
        "ascendent",
        description="Specify the order to apply. There are the option ascendent or descendent.",
        example="ascendent",
    ),
):
    """Retrieve a list of reports."""
    query = select(Report).where(Report.user_id == user_id)
    reports = await crud_report.get_multi(
        async_session,
        query=query,
        page_params=page_params,
        search_text={"name": search} if search else {},
        order_by=order_by,
        order=order,
    )

    if len(reports.items) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Reports Found")

    return reports


@router.put(
    "/report/{id}",
    response_model=IReportRead,
    response_model_exclude_none=True,
    status_code=200,
)
async def update_report(
    async_session: AsyncSession = Depends(get_db),
    id: UUID4 = Path(
        ...,
        description="The ID of the report to update",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
    report_in: IReportUpdate = Body(
        ..., example=report_request_examples["update"], description="Report to update"
    ),
):
    return await update_content_by_id(
        async_session=async_session,
        id=id,
        model=Report,
        crud_content=crud_report,
        content_in=report_in,
    )


@router.delete(
    "/report/{id}",
    response_model=None,
    status_code=204,
)
async def delete_report(
    async_session: AsyncSession = Depends(get_db),
    id: UUID4 = Path(
        ...,
        description="The ID of the report to update",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
):
    return await delete_content_by_id(
        async_session=async_session, id=id, model=Report, crud_content=crud_report
    )
