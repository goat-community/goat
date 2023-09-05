from fastapi import APIRouter, Body, Depends, Path, Query, status, HTTPException
from fastapi_pagination import Page
from pydantic import parse_obj_as, ValidationError
from fastapi_pagination import Params as PaginationParams
from pydantic import UUID4

from src.crud.crud_project import project as crud_project
from src.crud.crud_user_project import user_project as crud_user_project
from src.crud.crud_layer_project import layer_project as crud_layer_project
from src.crud.crud_layer import layer as crud_layer
from src.db.models.project import Project
from src.db.session import AsyncSession
from src.endpoints.deps import get_db, get_user_id
from src.schemas.common import ContentIdList, OrderEnum
from src.schemas.project import (
    IProjectCreate,
    IProjectRead,
    IProjectBaseUpdate,
    InitialViewState,
    request_examples as project_request_examples,
)
from src.db.models._link_model import UserProjectLink
from src.core.content import (
    create_content,
    delete_content_by_id,
)
from typing import List
from src.schemas.project import (
    ITileLayerProjectRead,
    IImageryLayerProjectRead,
    ITableLayerProjectRead,
    IFeatureLayerStandardProjectRead,
    IFeatureLayerIndicatorProjectRead,
    IFeatureLayerScenarioProjectRead,
    layer_type_mapping_read,
    layer_type_mapping_update,
)

router = APIRouter()


def layer_projects_to_schemas(layers_project):
    """Convert layer projects to schemas."""
    layer_projects_schemas = []

    # Loop through layer and layer projects
    for layer_project_tuple in layers_project:
        layer = layer_project_tuple[0]
        layer_project = layer_project_tuple[1]

        # Get layer type
        if layer.feature_layer_type is not None:
            layer_type = layer.type + "_" + layer.feature_layer_type
        else:
            layer_type = layer.type

        # Convert to dicts and update layer
        layer = layer.dict()
        layer_project = layer_project.dict()

        # Delete id from layer project
        del layer_project["id"]

        # Update layer
        layer.update(layer_project)

        # Write into correct schema
        layer_projects_schemas.append(layer_type_mapping_read[layer_type](**layer))

    return layer_projects_schemas


### Project endpoints
@router.post(
    "",
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
        other_params={"user_id": user_id},
    )

    # Create link between user and project for initial view state
    await crud_user_project.create(
        async_session,
        obj_in=UserProjectLink(
            user_id=user_id,
            project_id=project.id,
            initial_view_state=project_in.initial_view_state,
        ),
    )

    # Doing unneded type conversion to make sure the relations of project are not loaded
    return IProjectRead(**project.dict())


@router.get(
    "/{id}",
    summary="Retrieve a project by its ID",
    response_model=IProjectRead,
    response_model_exclude_none=True,
    status_code=200,
)
async def read_project(
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID4 = Depends(get_user_id),
    id: UUID4 = Path(
        ...,
        description="The ID of the project to get",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
):
    """Retrieve a project by its ID."""

    # Get project
    project = await crud_project.get(async_session, id=id)
    return IProjectRead(**project.dict())


@router.get(
    "",
    summary="Retrieve a list of projects",
    response_model=Page[IProjectRead],
    response_model_exclude_none=True,
    status_code=200,
)
async def read_projects(
    async_session: AsyncSession = Depends(get_db),
    page_params: PaginationParams = Depends(),
    folder_id: UUID4 = Query(..., description="Folder ID"),
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

    projects = await crud_project.get_projects(
        async_session=async_session,
        user_id=user_id,
        folder_id=folder_id,
        page_params=page_params,
        search=search,
        order_by=order_by,
        order=order,
    )

    return projects


@router.post(
    "/get-by-ids",
    summary="Retrieve a list of projects by their IDs",
    response_model=Page[IProjectRead],
    response_model_exclude_none=True,
    status_code=200,
)
async def read_projects_by_ids(
    async_session: AsyncSession = Depends(get_db),
    page_params: PaginationParams = Depends(),
    user_id: UUID4 = Depends(get_user_id),
    ids: ContentIdList = Body(
        ...,
        example=project_request_examples["get"],
        description="List of project IDs to retrieve",
    ),
):
    """Retrieve a list of projects by their IDs."""

    # Get projects by ids
    projects = await crud_project.get_projects(
        async_session=async_session,
        user_id=user_id,
        page_params=page_params,
        ids=ids.ids,
    )

    return projects


@router.put(
    "/{id}",
    response_model=IProjectRead,
    response_model_exclude_none=True,
    status_code=200,
)
async def update_project(
    async_session: AsyncSession = Depends(get_db),
    id: UUID4 = Path(
        ...,
        description="The ID of the project to get",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
    project_in: IProjectBaseUpdate = Body(
        ..., example=project_request_examples["update"], description="Project to update"
    ),
):
    """Update base attributes of a project by its ID."""

    # Update project
    project = await crud_project.update_base(
        async_session=async_session,
        id=id,
        project=project_in,
    )
    return project

@router.delete(
    "/{id}",
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

@router.get(
    "/{id}/initial-view-state",
    response_model=InitialViewState,
    response_model_exclude_none=True,
    status_code=200,
)
async def read_project_initial_view_state(
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID4 = Depends(get_user_id),
    id: UUID4 = Path(
        ...,
        description="The ID of the project to get",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
):
    """Retrieve initial view state of a project by its ID."""

    # Get initial view state
    user_project = await crud_user_project.get_by_multi_keys(
        async_session, keys={"user_id": user_id, "project_id": id}
    )
    return user_project[0].initial_view_state


@router.put(
    "/{id}/initial-view-state",
    response_model=InitialViewState,
    response_model_exclude_none=True,
    status_code=200,
)
async def update_project_initial_view_state(
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID4 = Depends(get_user_id),
    id: UUID4 = Path(
        ...,
        description="The ID of the project to get",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
    initial_view_state: InitialViewState = Body(
        ...,
        example=project_request_examples["initial_view_state"],
        description="Initial view state to update",
    ),
):
    """Update initial view state of a project by its ID."""

    # Update project
    user_project = await crud_user_project.update_initial_view_state(
        async_session,
        user_id=user_id,
        project_id=id,
        initial_view_state=initial_view_state,
    )
    return user_project.initial_view_state


@router.post(
    "/{id}/layer",
    response_model=List[
        IFeatureLayerStandardProjectRead
        | IFeatureLayerIndicatorProjectRead
        | IFeatureLayerScenarioProjectRead
        | ITableLayerProjectRead
        | ITileLayerProjectRead
        | IImageryLayerProjectRead
    ],
    response_model_exclude_none=True,
    status_code=200,
)
async def add_layers_to_project(
    async_session: AsyncSession = Depends(get_db),
    id: UUID4 = Path(
        ...,
        description="The ID of the project to get",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
    layer_ids: List[UUID4] = Query(
        ...,
        description="List of layer IDs to add to the project",
        example=["3fa85f64-5717-4562-b3fc-2c963f66afa6"],
    ),
):
    """Add layers to a project by its ID."""

    # Add layers to project
    layers = await crud_layer_project.create(
        async_session=async_session,
        project_id=id,
        layer_ids=layer_ids,
    )
    layers = layer_projects_to_schemas(layers)

    return layers


@router.get(
    "/{id}/layer",
    response_model=List[
        IFeatureLayerStandardProjectRead
        | IFeatureLayerIndicatorProjectRead
        | IFeatureLayerScenarioProjectRead
        | ITableLayerProjectRead
        | ITileLayerProjectRead
        | IImageryLayerProjectRead
    ],
    response_model_exclude_none=True,
    status_code=200,
)
async def get_layers_from_project(
    async_session: AsyncSession = Depends(get_db),
    id: UUID4 = Path(
        ...,
        description="The ID of the project to get",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
):
    """Get layers from a project by its ID."""

    # Get layers from project
    layers_project = await crud_layer_project.get_all(
        async_session=async_session,
        project_id=id,
    )
    layers_response = []

    for layer_project in layers_project:
        layer = layer_project[0].dict()
        layer_project_link = layer_project[1].dict()

        # Delete id column
        del layer_project_link["id"]
        # Update layer
        layer.update(layer_project_link)

        # Add feature layer type if exists else ''
        if layer["feature_layer_type"] is not None:
            layer_type = layer["type"] + "_" + layer["feature_layer_type"]
        else:
            layer_type = layer["type"]

        layers_response.append(layer_type_mapping_read[layer_type](**layer))

    return layers_response


@router.put(
    "/{id}/layer",
    response_model=IFeatureLayerStandardProjectRead
    | IFeatureLayerIndicatorProjectRead
    | IFeatureLayerScenarioProjectRead
    | ITableLayerProjectRead
    | ITileLayerProjectRead
    | IImageryLayerProjectRead,
    response_model_exclude_none=True,
    status_code=200,
)
async def update_layer_in_project(
    async_session: AsyncSession = Depends(get_db),
    id: UUID4 = Path(
        ...,
        description="The ID of the project to get",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
    layer_id: UUID4 = Query(
        ...,
        description="Layer ID to update",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
    layer_in: dict = Body(
        ...,
        examples=project_request_examples["update_layer"],
        description="Layer to update",
    ),
):
    """Update layer in a project by its ID."""

    # Get base layer object
    layer = await crud_layer.get(async_session, id=layer_id)

    # Get layer type
    if layer.feature_layer_type is not None:
        layer_type = layer.type + "_" + layer.feature_layer_type
    else:
        layer_type = layer.type

    # Determine the type based on the retrieved layer
    model_type = layer_type_mapping_update.get(layer_type)

    # Parse and validate the data against the model
    try:
        layer_in = parse_obj_as(model_type, layer_in)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    # Update layer in project
    layer_project = await crud_layer_project.update(
        async_session=async_session,
        project_id=id,
        layer_id=layer_id,
        layer_project=layer_in,
    )

    # Convert to dict
    layer_project = layer_project.dict()
    # Delete id column
    del layer_project["id"]
    # Update layer
    layer = layer.dict()
    layer.update(layer_project)

    return layer_type_mapping_read[layer_type](**layer)


@router.delete(
    "/{id}/layer",
    response_model=None,
    status_code=204,
)
async def delete_layer_from_project(
    async_session: AsyncSession = Depends(get_db),
    id: UUID4 = Path(
        ...,
        description="The ID of the project",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
    layer_id: UUID4 = Query(
        ...,
        description="Layer ID to delete",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
):
    """Delete layer from a project by its ID."""

    # Get layer project
    layer_project = await crud_layer_project.get_by_multi_keys(
        async_session,
        keys={"project_id": id, "layer_id": layer_id},
    )
    if layer_project == []:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Layer project relation not found"
        )

    # Delete layer from project
    await crud_layer_project.delete(
        db=async_session,
        id=layer_project[0].id,
    )

    return None
