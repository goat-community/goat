from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud, schemas
from src.crud.crud_scenario import scenario as crud_scenario
from src.core import security
from src.core.config import settings
from src.db import models
from src.db.session import async_session, r5_mongo_db_client

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")


async def get_db() -> Generator:
    async with async_session() as session:
        yield session


async def get_r5_mongo_db() -> AsyncIOMotorClient:
    return r5_mongo_db_client


async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.User:
    try:
        payload = jwt.decode(token, settings.API_SECRET_KEY, algorithms=[security.ALGORITHM])
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = await crud.user.get(db, id=token_data.sub, extra_fields=[models.User.roles])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_superuser(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have enough privileges")
    return current_user


async def check_user_owns_scenario(
    db: AsyncSession,
    scenario_id: int,
    current_user: models.User,
) -> int:

    if scenario_id == 0 or scenario_id is None:
        return 0

    scenario = await crud_scenario.get_by_multi_keys(
        db, keys={"id": scenario_id, "user_id": current_user.id}
    )
    if scenario == []:
        raise HTTPException(status_code=400, detail="Scenario not found")

    return scenario[0].id


async def check_user_owns_study_area(
    db: AsyncSession,
    study_area_id: int,
    current_user: models.User
) -> int:

    #TODO: Write generic function to check user owns study area

    return study_area_id


def check_user_owns_data_uploads(
    data_upload_ids: list[int], current_user: models.User
) -> list[int]:

    if data_upload_ids == [0] or data_upload_ids is None:
        return [0]

    if set(data_upload_ids).issubset(set(current_user.active_data_upload_ids)) is False:
        raise HTTPException(status_code=400, detail="Data upload not found")

    return data_upload_ids


async def check_user_owns_isochrone_calculation(
    db: AsyncSession,
    isochrone_calculation_id: int,
    current_user: models.User,
) -> int:

    isochrone_calculation = await crud.isochrone_calculation.get_by_multi_keys(
        db, keys={"id": isochrone_calculation_id, "user_id": current_user.id}
    )
    if isochrone_calculation == []:
        raise HTTPException(status_code=400, detail="Isochrone calculation not found")

    return isochrone_calculation[0].id
