# Standard Libraries
import json
import os
from typing import Any, Dict, Optional
from uuid import UUID

# Third-party Libraries
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    File,
    HTTPException,
    Path,
    Query,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse, JSONResponse
from fastapi_pagination import Page
from fastapi_pagination import Params as PaginationParams
from pydantic import UUID4, BaseModel
from sqlmodel import SQLModel, select

from core.core.config import settings

# Local application imports
from core.core.content import (
    read_content_by_id,
)
from core.crud.crud_job import job as crud_job
from core.crud.crud_layer import (
    CRUDLayerDatasetUpdate,
    CRUDLayerExport,
    CRUDLayerImport,
)
from core.crud.crud_layer import layer as crud_layer
from core.crud.crud_layer_project import layer_project as crud_layer_project
from core.db.models._link_model import LayerProjectLink
from core.db.models.layer import (
    FeatureUploadType,
    FileUploadType,
    Layer,
    LayerType,
    TableUploadType,
)
from core.db.models.project import ProjectPublic
from core.db.session import AsyncSession
from core.deps.auth import auth_z, auth_z_lite
from core.endpoints.deps import get_db, get_user_id
from core.schemas.common import OrderEnum
from core.schemas.error import HTTPErrorHandler
from core.schemas.job import JobType
from core.schemas.layer import (
    AreaStatisticsOperation,
    ComputeBreakOperation,
    ICatalogLayerGet,
    IFileUploadExternalService,
    IFileUploadMetadata,
    ILayerExport,
    ILayerFromDatasetCreate,
    ILayerGet,
    ILayerRead,
    IMetadataAggregate,
    IMetadataAggregateRead,
    IRasterCreate,
    IRasterRead,
    IUniqueValue,
    MaxFileSizeType,
)
from core.schemas.layer import (
    request_examples as layer_request_examples,
)
from core.utils import build_where, check_file_size

router = APIRouter()


@router.post(
    "/file-upload",
    summary="Upload file to server and validate",
    response_model=IFileUploadMetadata,
    status_code=201,
    dependencies=[Depends(auth_z)],
)
async def file_upload(
    *,
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_user_id),
    file: UploadFile,
) -> IFileUploadMetadata:
    """
    Upload file and validate.
    """

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File name is required.",
        )
    file_ending = os.path.splitext(file.filename)[-1][1:]

    # Check if file is feature or table
    if file_ending in TableUploadType.__members__:
        layer_type = LayerType.table
    elif file_ending in FeatureUploadType.__members__:
        layer_type = LayerType.feature
    else:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type not allowed. Allowed file types are: {', '.join(FileUploadType.__members__.keys())}",
        )

    if (
        await check_file_size(file=file, max_size=MaxFileSizeType[file_ending].value)
        is False
    ):
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size too large. Max file size is {round(MaxFileSizeType[file_ending].value / 1048576, 2)} MB",
        )

    # Run the validation
    metadata = await crud_layer.upload_file(
        async_session=async_session,
        user_id=user_id,
        source=file,
        layer_type=layer_type,
    )
    return metadata


@router.post(
    "/file-upload-external-service",
    summary="Fetch data from external service into a file, upload file to server and validate",
    response_model=IFileUploadMetadata,
    status_code=201,
    dependencies=[Depends(auth_z)],
)
async def file_upload_external_service(
    *,
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_user_id),
    external_service: IFileUploadExternalService = Body(
        ...,
        description="External service to fetch data from.",
    ),
) -> IFileUploadMetadata:
    """
    Fetch data from external service into a file, upload file to server and validate.
    """

    # This endpoint only supports external services providing feature data
    layer_type = LayerType.feature

    # Run the validation
    metadata = await crud_layer.upload_file(
        async_session=async_session,
        user_id=user_id,
        source=external_service,
        layer_type=layer_type,
    )
    return metadata


def _validate_and_fetch_metadata(
    user_id: UUID,
    dataset_id: UUID,
) -> Dict[str, Any]:
    # Check if user owns folder by checking if it exists
    folder_path = os.path.join(settings.DATA_DIR, str(user_id), str(dataset_id))
    if os.path.exists(folder_path) is False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found or not owned by user.",
        )

    # Get metadata from file in folder
    metadata_path = None
    for root, _dirs, files in os.walk(folder_path):
        if "metadata.json" in files:
            metadata_path = os.path.join(root, "metadata.json")

    if metadata_path is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metadata file not found.",
        )

    with open(os.path.join(metadata_path)) as f:
        file_metadata = dict(json.loads(json.load(f)))

    return file_metadata


async def _create_layer_from_dataset(
    background_tasks: BackgroundTasks,
    async_session: AsyncSession,
    user_id: UUID,
    project_id: Optional[UUID] = Query(
        None,
        description="The ID of the project to add the layer to",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
    layer_in: ILayerFromDatasetCreate = Body(
        ...,
        examples=layer_request_examples["create"],
        description="Layer to create",
    ),
) -> Dict[str, UUID]:
    """Create a feature standard or table layer from a dataset."""

    # Validate and fetch dataset file metadata
    file_metadata = _validate_and_fetch_metadata(
        user_id=user_id,
        dataset_id=layer_in.dataset_id,
    )

    # Create job and check if user can create a new job
    job = await crud_job.check_and_create(
        async_session=async_session,
        user_id=user_id,
        job_type=JobType.file_import,
        project_id=project_id,
    )

    # Run the import
    await CRUDLayerImport(
        background_tasks=background_tasks,
        async_session=async_session,
        user_id=user_id,
        job_id=job.id,
    ).import_file_job(
        file_metadata=file_metadata,
        layer_in=layer_in,
        project_id=project_id,
    )
    return {"job_id": job.id}


@router.post(
    "/feature-standard",
    summary="Create a new feature standard layer",
    response_class=JSONResponse,
    status_code=201,
    description="Generate a new layer from a file that was previously uploaded using the file-upload endpoint.",
    dependencies=[Depends(auth_z)],
)
async def create_layer_feature_standard(
    background_tasks: BackgroundTasks,
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_user_id),
    project_id: Optional[UUID] = Query(
        None,
        description="The ID of the project to add the layer to",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
    layer_in: ILayerFromDatasetCreate = Body(
        ...,
        examples=layer_request_examples["create"][LayerType.feature],
        description="Layer to create",
    ),
) -> Dict[str, Any]:
    """Create a new feature standard layer from a previously uploaded dataset."""

    return await _create_layer_from_dataset(
        background_tasks=background_tasks,
        async_session=async_session,
        user_id=user_id,
        project_id=project_id,
        layer_in=layer_in,
    )


@router.post(
    "/raster",
    summary="Create a new raster layer",
    response_model=IRasterRead,
    status_code=201,
    description="Generate a new layer based on a URL for a raster service hosted externally.",
    dependencies=[Depends(auth_z)],
)
async def create_layer_raster(
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID4 = Depends(get_user_id),
    layer_in: IRasterCreate = Body(
        ...,
        examples=layer_request_examples["create"][LayerType.raster],
        description="Layer to create",
    ),
) -> BaseModel:
    """Create a new raster layer from a service hosted externally."""

    layer = await crud_layer.create(
        db=async_session,
        obj_in=Layer(**layer_in.model_dump(), user_id=user_id).model_dump(),
    )
    return layer


@router.post(
    "/table",
    summary="Create a new table layer",
    response_class=JSONResponse,
    status_code=201,
    description="Generate a new layer from a file that was previously uploaded using the file-upload endpoint.",
    dependencies=[Depends(auth_z)],
)
async def create_layer_table(
    background_tasks: BackgroundTasks,
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_user_id),
    project_id: Optional[UUID] = Query(
        None,
        description="The ID of the project to add the layer to",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
    layer_in: ILayerFromDatasetCreate = Body(
        ...,
        examples=layer_request_examples["create"][LayerType.table],
        description="Layer to create",
    ),
) -> Dict[str, Any]:
    """Create a new table layer from a previously uploaded dataset."""

    return await _create_layer_from_dataset(
        background_tasks=background_tasks,
        async_session=async_session,
        user_id=user_id,
        project_id=project_id,
        layer_in=layer_in,
    )


@router.post(
    "/{layer_id}/export",
    summary="Export a layer to a file",
    response_class=FileResponse,
    status_code=201,
    description="Export a layer to a zip file.",
    dependencies=[Depends(auth_z)],
)
async def export_layer(
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID4 = Depends(get_user_id),
    layer_id: UUID4 = Path(
        ...,
        description="The ID of the layer to export",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
    layer_in: ILayerExport = Body(
        ...,
        examples=layer_request_examples["export"],
        description="Layer to export",
    ),
) -> FileResponse:
    # Run the export
    crud_export = CRUDLayerExport(
        id=layer_id,
        async_session=async_session,
        user_id=user_id,
    )
    with HTTPErrorHandler():
        zip_file_path = await crud_export.export_file_run(layer_in=layer_in)
    # Return file
    file_name = os.path.basename(zip_file_path)
    return FileResponse(zip_file_path, media_type="application/zip", filename=file_name)


@router.get(
    "/{layer_id}",
    summary="Retrieve a layer by its ID",
    response_model=ILayerRead,
    response_model_exclude_none=True,
    status_code=200,
    dependencies=[Depends(auth_z)],
)
async def read_layer(
    async_session: AsyncSession = Depends(get_db),
    layer_id: UUID4 = Path(
        ...,
        description="The ID of the layer to get",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
) -> SQLModel:
    """Retrieve a layer by its ID."""
    return await read_content_by_id(
        async_session=async_session, id=layer_id, model=Layer, crud_content=crud_layer
    )


@router.post(
    "",
    response_model=Page[ILayerRead],
    response_model_exclude_none=True,
    status_code=200,
    summary="Retrieve a list of layers using different filters including a spatial filter. If not filter is specified, all layers will be returned.",
    dependencies=[Depends(auth_z)],
)
async def read_layers(
    async_session: AsyncSession = Depends(get_db),
    page_params: PaginationParams = Depends(),
    user_id: UUID4 = Depends(get_user_id),
    obj_in: ILayerGet = Body(
        None,
        examples={},
        description="Layer to get",
    ),
    team_id: UUID | None = Query(
        None,
        description="The ID of the team to get the layers from",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
    organization_id: UUID | None = Query(
        None,
        description="The ID of the organization to get the layers from",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
    order_by: str = Query(
        None,
        description="Specify the column name that should be used to order. You can check the Layer model to see which column names exist.",
        example="created_at",
    ),
    order: OrderEnum = Query(
        "descendent",
        description="Specify the order to apply. There are the option ascendent or descendent.",
        example="descendent",
    ),
):
    """This endpoints returns a list of layers based one the specified filters."""

    with HTTPErrorHandler():
        # Make sure that team_id and organization_id are not both set
        if team_id is not None and organization_id is not None:
            raise ValueError("Only one of team_id and organization_id can be set.")

        # Get layers from CRUD
        layers = await crud_layer.get_layers_with_filter(
            async_session=async_session,
            user_id=user_id,
            params=obj_in,
            order_by=order_by,
            order=order,
            page_params=page_params,
            team_id=team_id,
            organization_id=organization_id,
        )
    return layers


@router.post(
    "/catalog",
    response_model=Page[ILayerRead],
    response_model_exclude_none=True,
    status_code=200,
    summary="Retrieve a list of layers using different filters including a spatial filter. If not filter is specified, all layers will be returned.",
    dependencies=[Depends(auth_z)],
)
async def read_catalog_layers(
    async_session: AsyncSession = Depends(get_db),
    page_params: PaginationParams = Depends(),
    user_id: UUID4 = Depends(get_user_id),
    obj_in: ICatalogLayerGet = Body(
        None,
        examples={},
        description="Layer to get",
    ),
    order_by: str = Query(
        None,
        description="Specify the column name that should be used to order. You can check the Layer model to see which column names exist.",
        example="created_at",
    ),
    order: OrderEnum = Query(
        "descendent",
        description="Specify the order to apply. There are the option ascendent or descendent.",
        example="descendent",
    ),
):
    """This endpoints returns a list of layers based one the specified filters."""

    with HTTPErrorHandler():
        # Get layers from CRUD
        layers = await crud_layer.get_layers_with_filter(
            async_session=async_session,
            user_id=user_id,
            params=obj_in,
            order_by=order_by,
            order=order,
            page_params=page_params,
        )
    return layers


@router.put(
    "/{layer_id}",
    response_model=ILayerRead,
    response_model_exclude_none=True,
    status_code=200,
    dependencies=[Depends(auth_z)],
)
async def update_layer(
    async_session: AsyncSession = Depends(get_db),
    layer_id: UUID4 = Path(
        ...,
        description="The ID of the layer to get",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
    layer_in: Dict[Any, Any] = Body(
        ..., examples=layer_request_examples["update"], description="Layer to update"
    ),
):
    with HTTPErrorHandler():
        return await crud_layer.update(
            async_session=async_session,
            id=layer_id,
            layer_in=layer_in,
        )


@router.put(
    "/{layer_id}/dataset",
    response_class=JSONResponse,
    status_code=200,
    dependencies=[Depends(auth_z)],
)
async def update_layer_dataset(
    background_tasks: BackgroundTasks,
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_user_id),
    layer_id: UUID4 = Path(
        ...,
        description="The ID of the layer to get",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
    dataset_id: UUID = Query(
        ..., description="The ID of the dataset to update the layer with"
    ),
):
    """Update the dataset of a layer."""

    # Ensure updating the dataset of this layer is permitted
    with HTTPErrorHandler():
        existing_layer = await crud_layer.get_internal(
            async_session=async_session,
            id=layer_id,
        )
        if str(existing_layer.user_id) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to update this layer.",
            )

        # Validate and fetch dataset file metadata
        file_metadata = _validate_and_fetch_metadata(
            user_id=user_id,
            dataset_id=dataset_id,
        )

    # Create job and check if user can create a new job
    job = await crud_job.check_and_create(
        async_session=async_session,
        user_id=user_id,
        job_type=JobType.update_layer_dataset,
    )

    # Run the import
    layer_in = ILayerFromDatasetCreate(
        name=existing_layer.name,
        description=existing_layer.description,
        folder_id=existing_layer.folder_id,
        properties=existing_layer.properties,
        data_type=existing_layer.data_type,
        url=existing_layer.url,
        other_properties=existing_layer.other_properties,
        dataset_id=dataset_id,
    )
    await CRUDLayerDatasetUpdate(
        background_tasks=background_tasks,
        async_session=async_session,
        user_id=user_id,
        job_id=job.id,
    ).update(
        existing_layer_id=existing_layer.id,
        file_metadata=file_metadata,
        layer_in=layer_in,
    )

    return {"job_id": job.id}


@router.delete(
    "/{layer_id}",
    response_model=None,
    summary="Delete a layer and its data in case of an internal layer.",
    status_code=204,
    dependencies=[Depends(auth_z)],
)
async def delete_layer(
    async_session: AsyncSession = Depends(get_db),
    layer_id: UUID4 = Path(
        ...,
        description="The ID of the layer to get",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
):
    """Delete a layer and its data in case of an internal layer."""

    with HTTPErrorHandler():
        await crud_layer.delete(
            async_session=async_session,
            id=layer_id,
        )
    return


@router.get(
    "/{layer_id}/feature-count",
    summary="Get feature count",
    response_class=JSONResponse,
    status_code=200,
    dependencies=[Depends(auth_z)],
)
async def get_feature_count(
    async_session: AsyncSession = Depends(get_db),
    layer_id: UUID4 = Path(
        ...,
        description="The ID of the layer to get",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
    query: str = Query(
        None,
        description="CQL2-Filter in JSON format",
        example='{"op": "=", "args": [{"property": "category"}, "bus_stop"]}',
    ),
):
    """Get feature count. Based on the passed CQL-filter."""

    with HTTPErrorHandler():
        # Get layer
        layer = await crud_layer.get_internal(
            async_session=async_session,
            id=layer_id,
        )
        where_query = build_where(
            layer.id, layer.table_name, query, layer.attribute_mapping
        )
        count = await crud_layer_project.get_feature_cnt(
            async_session=async_session,
            layer_project=layer,
            where_query=where_query,
        )

    # Return result
    return count


@router.get(
    "/{layer_id}/area/{operation}",
    summary="Get area statistics of a layer",
    response_class=JSONResponse,
    status_code=200,
    dependencies=[Depends(auth_z)],
)
async def get_area_statistics(
    async_session: AsyncSession = Depends(get_db),
    layer_id: UUID4 = Path(
        ...,
        description="The ID of the layer to get",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
    operation: AreaStatisticsOperation = Path(
        ...,
        description="The operation to perform",
        example="sum",
    ),
    query: str = Query(
        None,
        description="CQL2-Filter in JSON format",
        example='{"op": ">", "args": [{"property": "id"}, "10"]}',
    ),
):
    """Get statistics on the area size of a polygon layer. The area is computed using geography datatype and the unit is m²."""

    with HTTPErrorHandler():
        statistics = await crud_layer.get_area_statistics(
            async_session=async_session,
            id=layer_id,
            operation=operation,
            query=query,
        )

    # Return result
    return statistics


@router.get(
    "/{layer_id}/unique-values/{column_name}",
    summary="Get unique values of a column",
    response_model=Page[IUniqueValue],
    status_code=200,
    # dependencies=[Depends(auth_z)],
)
async def get_unique_values(
    request: Request,
    async_session: AsyncSession = Depends(get_db),
    page_params: PaginationParams = Depends(),
    layer_id: UUID4 = Path(
        ...,
        description="The ID of the layer to get",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
    column_name: str = Path(
        ...,
        description="The column name to get the unique values from",
        example="name",
    ),
    query: str = Query(
        None,
        description="CQL2-Filter in JSON format",
        example={"op": "=", "args": [{"property": "category"}, "bus_stop"]},
    ),
    order: OrderEnum = Query(
        "descendent",
        description="Specify the order to apply. There are the option ascendent or descendent.",
        example="descendent",
    ),
):
    """Get unique values of a column. Based on the passed CQL-filter and order."""

    # Check authorization status
    try:
        await auth_z_lite(request, async_session)
    except HTTPException:

        public_layer = (
            select(LayerProjectLink)
            .join(
                ProjectPublic,
                LayerProjectLink.project_id == ProjectPublic.project_id,
            )
            .where(
                LayerProjectLink.layer_id == layer_id,
            )
            .limit(1)
        )
        result = await async_session.execute(public_layer)
        public_layer = result.scalars().first()
        # Check if layer is public
        if not public_layer:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )

    with HTTPErrorHandler():
        values = await crud_layer.get_unique_values(
            async_session=async_session,
            id=layer_id,
            column_name=column_name,
            query=query,
            page_params=page_params,
            order=order,
        )

    # Return result
    return values


@router.get(
    "/{layer_id}/class-breaks/{operation}/{column_name}",
    summary="Get statistics of a column",
    response_class=JSONResponse,
    status_code=200,
    dependencies=[Depends(auth_z)],
)
async def class_breaks(
    async_session: AsyncSession = Depends(get_db),
    layer_id: UUID4 = Path(
        ...,
        description="The ID of the layer to get",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ),
    operation: ComputeBreakOperation = Path(
        ...,
        description="The operation to perform",
        example="quantile",
    ),
    column_name: str = Path(
        ...,
        description="The column name to get the statistics from. It needs to be a number column.",
        example="name",
    ),
    breaks: int | None = Query(
        None,
        description="Number of class breaks to create",
        example=5,
    ),
    query: str | None = Query(
        None,
        description="CQL2-Filter in JSON format",
        example={"op": "=", "args": [{"property": "category"}, "bus_stop"]},
    ),
    stripe_zeros: bool | None = Query(
        True,
        description="Stripe zeros from the column before performing the operation",
        example=True,
    ),
):
    """Get statistics of a column. Based on the saved layer filter in the project."""

    with HTTPErrorHandler():
        statistics = await crud_layer.get_class_breaks(
            async_session=async_session,
            id=layer_id,
            operation=operation,
            column_name=column_name,
            breaks=breaks,
            query=query,
            stripe_zeros=stripe_zeros,
        )

    # Return result
    return statistics


@router.post(
    "/metadata/aggregate",
    summary="Return the count of layers for different metadata values acting as filters",
    response_model=IMetadataAggregateRead,
    status_code=200,
    dependencies=[Depends(auth_z)],
)
async def metadata_aggregate(
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID4 = Depends(get_user_id),
    obj_in: IMetadataAggregate = Body(
        None,
        description="Filter for metadata to aggregate",
    ),
):
    """Return the count of layers for different metadata values acting as filters."""
    with HTTPErrorHandler():
        result = await crud_layer.metadata_aggregate(
            async_session=async_session,
            user_id=user_id,
            params=obj_in,
        )
    return result
