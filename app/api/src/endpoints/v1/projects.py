
from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from src.endpoints.legacy import deps
from src.schemas.project import dummy_projects
import uuid

router = APIRouter()


@router.get("", response_class=JSONResponse)
async def list_projects(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    return dummy_projects


@router.get("/{id:str}", response_class=JSONResponse)
async def read_project_by_id(
    id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
):
    for project in dummy_projects:
        if project["id"] == id:
            return project


# @router.post("", response_class=JSONResponse)
# async def create_a_new_project(
#     project_in: ,
#     db: AsyncSession = Depends(deps.get_db),
#     current_super_user: models.User = Depends(deps.get_current_active_superuser),
# ):
#     project = await crud.project.create(db, obj_in=project_in)
#     return project


# @router.put("/{id:int}", response_model=models.Project)
# async def update_a_project(
#     id: int,
#     project_in: schemas.CreateProject,
#     db: AsyncSession = Depends(deps.get_db),
#     current_super_user: models.User = Depends(deps.get_current_active_superuser),
# ):
#     project_in_db = await crud.project.get(db, id=id)
#     if not project_in_db:
#         raise HTTPException(status_code=404, detail="project not found.")

#     project = await crud.project.update(db, db_obj=project_in_db, obj_in=project_in)
#     return project


# @router.delete("/")
# async def delete_projects(
#     id: List[int] = Query(default=None, gt=0),
#     db: AsyncSession = Depends(deps.get_db),
#     current_super_user: models.User = Depends(deps.get_current_active_superuser),
# ):

#     return await crud.project.remove_multi(db, ids=id)
