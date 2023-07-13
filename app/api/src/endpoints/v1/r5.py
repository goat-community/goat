from typing import Any, List

import requests
from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse

from src import crud
from src.core.config import settings
from src.db import models
from src.endpoints.legacy import deps
from src.schemas.msg import Msg
from src.schemas.r5 import (
    R5ProjectCreateDTO,
    R5ProjectInDB,
    R5ProjectUpdateDTO,
    R5RegionCreateDTO,
    R5RegionInDB,
    request_examples,
)

router = APIRouter()

# ----------------------ACTIVITY ENDPOINTS------------------------
# ----------------------------------------------------------------

headers = {}
if settings.R5_AUTHORIZATION:
    headers["Authorization"] = settings.R5_AUTHORIZATION


@router.get("/activity")
async def get_activity(
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Get all activities.
    """
    response = requests.delete(settings.R5_API_URL + "/activity", headers=headers)
    return response.json()


# ------------------------REGION ENDPOINTS------------------------
# ----------------------------------------------------------------


@router.get("/region", response_model=List[R5RegionInDB])
async def get_regions(
    *,
    db: AsyncSession = Depends(deps.get_r5_mongo_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get all regions.
    """
    regions = await crud.r5.get_all_regions(db)
    return regions


@router.get("/region/{region_id}", response_model=R5RegionInDB)
async def get_region(
    *,
    region_id: str,
    db: AsyncSession = Depends(deps.get_r5_mongo_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get region.
    """
    region = await crud.r5.get_region(db, region_id)
    return region


@router.get("/region/{region_id}/project", response_model=List[R5ProjectInDB])
async def get_projects_for_region(
    *,
    region_id: str,
    db: AsyncSession = Depends(deps.get_r5_mongo_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get all projects.
    """
    projects = await crud.r5.get_projects_for_region(db, region_id)
    return projects


@router.post("/region", response_model=R5RegionInDB)
async def region_create(
    *,
    db: AsyncSession = Depends(deps.get_r5_mongo_db),
    region_in: R5RegionCreateDTO = Body(..., example=request_examples["region"]["create"]),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new region.
    """
    region = await crud.r5.create_region(db=db, region_in=region_in)
    return region


# TODO: Add region update


@router.delete("/region/{region_id}", response_model=Msg)
async def region_delete(
    *,
    db: AsyncSession = Depends(deps.get_r5_mongo_db),
    region_id: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete region.
    """
    region = await crud.r5.get_region(db=db, region_id=region_id)
    if not region:
        raise HTTPException(status_code=400, detail="The region doesn't exist")

    result = await crud.r5.delete_region(db=db, region_id=region_id)

    return result


# -----------------------PROJECT ENDPOINTS------------------------
# ----------------------------------------------------------------


@router.get("/project", response_model=List[R5ProjectInDB])
async def get_projects(
    *,
    db: AsyncSession = Depends(deps.get_r5_mongo_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get all projects.
    """
    projects = await crud.r5.get_all_projects(db)
    return projects


@router.get("/project/{project_id}", response_model=R5ProjectInDB)
async def get_project(
    *,
    project_id: str,
    db: AsyncSession = Depends(deps.get_r5_mongo_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get project.
    """
    project = await crud.r5.get_project(db, project_id)
    return project


@router.post("/project", response_model=R5ProjectInDB)
async def project_create(
    *,
    db: AsyncSession = Depends(deps.get_r5_mongo_db),
    project_in: R5ProjectCreateDTO = Body(..., example=request_examples["project"]["create"]),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new project.
    """
    project = await crud.r5.create_project(db=db, project_in=project_in)
    return project


@router.put("/project", response_model=Msg)
async def project_update(
    *,
    db: AsyncSession = Depends(deps.get_r5_mongo_db),
    project_in: R5ProjectUpdateDTO = Body(..., example=request_examples["project"]["update"]),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update project.
    """
    project = await crud.r5.update_project(db=db, project_in=project_in)
    return project


@router.delete("/project/{project_id}", response_model=Msg)
async def project_delete(
    *,
    db: AsyncSession = Depends(deps.get_r5_mongo_db),
    project_id: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete project.
    """
    result = await crud.r5.delete_project(db=db, project_id=project_id)
    return result


# ------------------------BUNDLE ENDPOINTS------------------------
# ----------------------------------------------------------------


@router.get("/bundle", response_class=JSONResponse)
async def get_bundles(
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get all bundles.
    """
    result = requests.get(settings.R5_API_URL + "/bundle", headers=headers)
    return result.json()


@router.get("/bundle/{bundle_id}", response_class=JSONResponse)
async def get_bundle(
    *,
    bundle_id: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get bundle.
    """
    result = requests.get(settings.R5_API_URL + "/bundle/" + bundle_id, headers=headers)
    return result.json()


@router.post("/bundle", response_class=JSONResponse)
async def create_bundle(
    *,
    bundle_name: str = Form(...),
    osm: UploadFile = File(...),
    feed_group: UploadFile = File(...),
    region_id: str = Form(...),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new bundle.
    """
    response = requests.post(
        settings.R5_API_URL + "/bundle",
        files={
            "bundleName": bundle_name,
            "osm": osm.file,
            "feedGroup": feed_group.file,
            "regionId": region_id,
        },
        headers=headers,
    )
    return response.json()


@router.delete("/bundle/{bundle_id}", response_class=JSONResponse)
async def delete_bundle(
    *,
    bundle_id: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete bundle.
    """
    response = requests.delete(settings.R5_API_URL + "/bundle/" + bundle_id, headers=headers)
    return response.json()
