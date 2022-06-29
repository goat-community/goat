import time
from typing import Any, List

import requests
from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    Form,
    HTTPException,
    Response,
    UploadFile,
)
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse

from src import crud
from src.core.config import settings
from src.db import models
from src.endpoints import deps
from src.jsoline import jsolines
from src.resources.responses import OctetStreamResponse
from src.schemas.msg import Msg
from src.schemas.r5 import (
    R5IsochroneAnalysisDTO,
    R5ProjectCreateDTO,
    R5ProjectInDB,
    R5ProjectUpdateDTO,
    R5RegionCreateDTO,
    R5RegionInDB,
    request_examples,
)
from src.utils import compute_single_value_surface, decode_r5_grid

router = APIRouter()

# ----------------------ACTIVITY ENDPOINTS------------------------
# ----------------------------------------------------------------


@router.get("/activity")
async def get_activity(
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get all activities.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")

    response = requests.delete(settings.R5_API_URL + "/activity")
    return response.json()


# ------------------------REGION ENDPOINTS------------------------
# ----------------------------------------------------------------


@router.get("/region", response_model=List[R5RegionInDB])
async def get_regions(
    *,
    db: AsyncSession = Depends(deps.get_r5_mongo_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all regions.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")

    regions = await crud.r5.get_all_regions(db)
    return regions


@router.get("/region/{region_id}", response_model=R5RegionInDB)
async def get_region(
    *,
    region_id: str,
    db: AsyncSession = Depends(deps.get_r5_mongo_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get region.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")

    region = await crud.r5.get_region(db, region_id)
    return region


@router.get("/region/{region_id}/project", response_model=List[R5ProjectInDB])
async def get_projects_for_region(
    *,
    region_id: str,
    db: AsyncSession = Depends(deps.get_r5_mongo_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all projects.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")

    projects = await crud.r5.get_projects_for_region(db, region_id)
    return projects


# ------------------------REGION ENDPOINTS------------------------
# ----------------------------------------------------------------


@router.post("/region", response_model=R5RegionInDB)
async def region_create(
    *,
    db: AsyncSession = Depends(deps.get_r5_mongo_db),
    region_in: R5RegionCreateDTO = Body(..., example=request_examples["region"]["create"]),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:

    """
    Create new region.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")

    region = await crud.r5.create_region(db=db, region_in=region_in)

    return region


# TODO: Add region update


@router.delete("/region/{region_id}", response_model=Msg)
async def region_delete(
    *,
    db: AsyncSession = Depends(deps.get_r5_mongo_db),
    region_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete region.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")

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
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all projects.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")

    projects = await crud.r5.get_all_projects(db)
    return projects


@router.get("/project/{project_id}", response_model=R5ProjectInDB)
async def get_project(
    *,
    project_id: str,
    db: AsyncSession = Depends(deps.get_r5_mongo_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get project.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")

    project = await crud.r5.get_project(db, project_id)
    return project


@router.post("/project", response_model=R5ProjectInDB)
async def project_create(
    *,
    db: AsyncSession = Depends(deps.get_r5_mongo_db),
    project_in: R5ProjectCreateDTO = Body(..., example=request_examples["project"]["create"]),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new project.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")

    project = await crud.r5.create_project(db=db, project_in=project_in)

    return project


@router.put("/project", response_model=Msg)
async def project_update(
    *,
    db: AsyncSession = Depends(deps.get_r5_mongo_db),
    project_in: R5ProjectUpdateDTO = Body(..., example=request_examples["project"]["update"]),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update project.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")

    project = await crud.r5.update_project(db=db, project_in=project_in)
    return project


@router.delete("/project/{project_id}", response_model=Msg)
async def project_delete(
    *,
    db: AsyncSession = Depends(deps.get_r5_mongo_db),
    project_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete project.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")

    result = await crud.r5.delete_project(db=db, project_id=project_id)

    return result


# ------------------------BUNDLE ENDPOINTS------------------------
# ----------------------------------------------------------------


@router.get("/bundle", response_class=JSONResponse)
async def get_bundles(current_user: models.User = Depends(deps.get_current_active_user)) -> Any:
    """
    Get all bundles.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")
    result = requests.get(settings.R5_API_URL + "/bundle")
    return result.json()


@router.get("/bundle/{bundle_id}", response_class=JSONResponse)
async def get_bundle(
    *,
    bundle_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get bundle.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")
    result = requests.get(settings.R5_API_URL + "/bundle/" + bundle_id)
    return result.json()


@router.post("/bundle", response_class=JSONResponse)
async def create_bundle(
    *,
    bundle_name: str = Form(...),
    osm: UploadFile = File(...),
    feed_group: UploadFile = File(...),
    region_id: str = Form(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new bundle.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")

    response = requests.post(
        settings.R5_API_URL + "/bundle",
        files={
            "bundleName": bundle_name,
            "osm": osm.file,
            "feedGroup": feed_group.file,
            "regionId": region_id,
        },
    )
    return response.json()


@router.delete("/bundle/{bundle_id}", response_class=JSONResponse)
async def delete_bundle(
    *,
    bundle_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete bundle.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")

    response = requests.delete(settings.R5_API_URL + "/bundle/" + bundle_id)
    return response.json()


# ---------------------ANALYSIS ENDPOINTS-------------------------
# ----------------------------------------------------------------


@router.post("/analysis", response_class=OctetStreamResponse)
async def analysis(
    analysis_in: R5IsochroneAnalysisDTO = Body(..., example=request_examples["analysis"]),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Calculate PT Isochrone.
    """
    payload = analysis_in.dict()
    # TODO: Get the project id and bbox from study area.
    payload["projectId"] = "6294f0ae0cfee1c6747d696c"
    payload["bounds"] = {
        "north": 48.2905,
        "south": 47.99727,
        "east": 11.94489,
        "west": 11.31592,
    }
    result = requests.post(settings.R5_API_URL + "/analysis", json=payload)
    grid_decoded = decode_r5_grid(result.content)
    single_value_surface = compute_single_value_surface(
        grid_decoded["width"],
        grid_decoded["height"],
        grid_decoded["depth"],
        grid_decoded["data"],
        50,
    )
    grid_decoded["surface"] = single_value_surface
    isochrone_coordinates = jsolines(
        grid_decoded["surface"],
        grid_decoded["width"],
        grid_decoded["height"],
        grid_decoded["west"],
        grid_decoded["north"],
        grid_decoded["zoom"],
        120,
    )
    try:
        return Response(bytes(result.content))
    except Exception as e:
        raise e
