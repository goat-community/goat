import datetime
import json
from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud, schemas
from src.core.config import settings
from src.crud.base import CRUDBase
from src.db import models
from src.endpoints.legacy import deps
from src.schemas import Msg
from src.schemas.user import request_examples
from src.utils import generate_token, send_email, to_feature_collection, verify_token

router = APIRouter()


@router.get("", response_model=List[models.User], response_model_exclude={"hashed_password"})
async def read_users(
    response: Response,
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    ordering: str = None,
    q: str = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve users.
    """
    is_superuser = crud.user.is_superuser(current_user)
    total_count = await crud.user.count(db)
    response.headers["X-Total-Count"] = str(total_count)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")

    users = await crud.user.get_multi(db, skip=skip, limit=limit, ordering=ordering, query=q)
    return users


@router.get("/me", response_model=models.User, response_model_exclude={"hashed_password"})
async def read_user_me(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.get("/me/study-area", response_class=JSONResponse)
async def read_user_study_area(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user's active study area.
    """
    study_area = await crud.user.get_active_study_area(db, current_user)

    features = to_feature_collection(
        study_area, exclude_properties=["default_setting", "buffer_geom_heatmap"]
    )
    return features


@router.get(
    "/me/study-areas-list",
    response_model=List[schemas.UserStudyAreaList],
)
async def read_user_study_areas(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get user study areas.
    """
    user = await crud.user.get(db, id=current_user.id, extra_fields=[models.User.study_areas])
    study_area_list = []
    for study_area in user.study_areas:
        study_area_list.append(schemas.UserStudyAreaList(id=study_area.id, name=study_area.name))
    return study_area_list


@router.put("/me/preference", response_model=models.User)
async def update_user_preference(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    preference: schemas.UserPreference = Body(
        ..., examples=request_examples["update_user_preference"]
    ),
) -> Any:
    """
    Update user preference.
    """
    if preference.active_study_area_id is not None:
        owns_study_area = await CRUDBase(models.UserStudyArea).get_by_multi_keys(
            db, keys={"user_id": current_user.id, "study_area_id": preference.active_study_area_id}
        )
        if owns_study_area == []:
            raise HTTPException(status_code=400, detail="The user doesn't own the study area")

    user = await crud.user.get(db, id=current_user.id)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="User not found",
        )
    user = await CRUDBase(models.User).update(db, db_obj=user, obj_in=preference)
    return user


@router.post("")
async def create_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: schemas.UserCreate = Body(..., example=request_examples["create"]),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new user.
    """

    user = await crud.user.get_by_key(db, key="email", value=user_in.email)
    if user and len(user) > 0:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = await crud.user.create(db, obj_in=user_in)
    user = await crud.user.get(
        db, id=user.id, extra_fields=[models.User.roles, models.User.study_areas]
    )
    user_json = jsonable_encoder(user)
    user_json["roles"] = [json.loads(role.json()) for role in user.roles]
    user_json["study_areas"] = [study_area.id for study_area in user.study_areas]
    del user_json["hashed_password"]
    return user_json


@router.post("/demo", response_model=models.User, response_model_exclude={"hashed_password"})
async def create_demo_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: schemas.UserCreateDemo = Body(..., example=request_examples["create_demo_user"]),
) -> Any:
    """
    Create new user.
    """
    user = await crud.user.get_by_key(db, key="email", value=user_in.email)
    if user and len(user) > 0:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    organization_demo = await crud.organization.get_by_key(db, key="name", value="demo")
    study_area_demo = await crud.study_area.get_by_key(
        db, key="id", value=settings.DEMO_USER_STUDY_AREA_ID
    )

    if len(organization_demo) == 0 or len(study_area_demo) == 0:
        raise HTTPException(
            status_code=400,
            detail="Can't create a demo user at this time. Please contact the administrator.",
        )
    organization_demo = organization_demo[0]
    study_area_demo = study_area_demo[0]
    user_in = user_in.dict()
    user_in.update(
        {
            "organization_id": organization_demo.id,
            "roles": ["user"],
            "active_study_area_id": study_area_demo.id,
            "active_data_upload_ids": [],
            "storage": 0,
            "limit_scenarios": settings.DEMO_USER_SCENARIO_LIMIT,
            "is_active": False,
        }
    )
    user_obj = schemas.UserCreate(**user_in)
    user = await crud.user.create(db, obj_in=user_obj)
    activate_token = generate_token(email=user.email)
    if settings.EMAILS_ENABLED and user.email:
        send_email(
            type="activate_new_account",
            email_to=user.email,
            name=user.name,
            surname=user.surname,
            token=activate_token,
            email_language=user.language_preference,
        )
    return user


@router.post(
    "/demo/activate", response_model=models.User, response_model_exclude={"hashed_password"}
)
async def activate_demo_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    token: str = Query(None, description="Activation token"),
) -> Any:
    """
    Activate a demo user.
    """
    email = verify_token(token=token)
    if not email:
        raise HTTPException(
            status_code=400,
            detail="The activation token is invalid.",
        )
    user = await crud.user.get_by_key(db, key="email", value=email)
    if user and len(user) > 0 and user[0].is_active is False:
        user = user[0]
        user = await CRUDBase(models.User).update(db, db_obj=user, obj_in={"is_active": True})
        send_email(
            type="account_trial_started",
            email_to=user.email,
            name=user.name,
            surname=user.surname,
            token="",
            email_language=user.language_preference,
        )
        return user
    else:
        raise HTTPException(
            status_code=400,
            detail="The user with this email doesn't exist in the system.",
        )


@router.get("/demo/deactivate", response_model=Msg)
async def deactivate_demo_users(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Deactivate demo user.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")

    organization_demo = await crud.organization.get_by_key(db, key="name", value="demo")
    if len(organization_demo) == 0:
        raise HTTPException(
            status_code=400,
            detail="Can't deactivate demo users at this time.",
        )
    organization_demo = organization_demo[0]
    users = await crud.user.get_by_key(db, key="organization_id", value=organization_demo.id)
    for user in users:
        time_diff = datetime.datetime.now() - user.creation_date
        if (time_diff.days > settings.DEMO_USER_DEACTIVATION_DAYS) and user.is_active:
            user = await CRUDBase(models.User).update(db, db_obj=user, obj_in={"is_active": False})
            if settings.EMAILS_ENABLED and user.email:
                send_email(
                    type="account_expired",
                    email_to=user.email,
                    name=user.name,
                    surname=user.surname,
                    token="",
                    email_language=user.language_preference,
                )
        elif (time_diff.days == settings.DEMO_USER_DEACTIVATION_DAYS - 3) and user.is_active:
            if settings.EMAILS_ENABLED and user.email:
                send_email(
                    type="account_expiring",
                    email_to=user.email,
                    name=user.name,
                    surname=user.surname,
                    token="",
                    email_language=user.language_preference,
                )

    return {"msg": "Demo users deactivated"}


@router.get("/{user_id}")
async def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = await crud.user.get(
        db, id=user_id, extra_fields=[models.User.roles, models.User.study_areas]
    )

    user_json = jsonable_encoder(user)
    user_json["roles"] = [json.loads(role.json()) for role in user.roles]
    user_json["study_areas"] = [study_area.id for study_area in user.study_areas]

    del user_json["hashed_password"]

    return user_json


@router.delete("/")
async def delete_users(
    *,
    id: List[int] = Query(default=None, gt=0),
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete users.
    """

    return await crud.user.remove_multi(db, ids=id)


@router.put("/{user_id}", response_model=models.User, response_model_exclude={"hashed_password"})
async def update_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UserUpdate = Body(..., example=request_examples["update"]),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """

    user = await crud.user.get(
        db, id=user_id, extra_fields=[models.User.study_areas, models.User.roles]
    )
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user = await crud.user.update(db, db_obj=user, obj_in=user_in)
    return user
