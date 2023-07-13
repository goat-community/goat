from typing import Any, Dict, Optional, Union

from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Polygon
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from shapely import Point
from src.core.security import get_password_hash, verify_password
from src.crud.base import CRUDBase
from src.db import models
from src.schemas.legacy.user import UserCreate, UserUpdate
from src.schemas.isochrone import IsochroneStartingPointCoord


class CRUDUser(CRUDBase[models.User, UserCreate, UserUpdate]):
    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> models.User:
        db_obj = models.User.from_orm(obj_in)
        db_obj.hashed_password = get_password_hash(obj_in.password)
        roles = await db.execute(
            select(models.Role).filter(models.Role.name.in_(obj_in.roles))
        )
        db_obj.roles = roles.scalars().all()

        # combine study_area_ids with active_study_area_id
        user_study_area_ids = set()
        if obj_in.active_study_area_id:
            user_study_area_ids.add(obj_in.active_study_area_id)
        user_study_area_ids.update(obj_in.study_areas)

        study_areas = await db.execute(
            select(models.StudyArea).filter(
                models.StudyArea.id.in_(user_study_area_ids)
            )
        )
        db_obj.study_areas = study_areas.scalars().all()
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: models.User,
        obj_in: Union[UserUpdate, Dict[str, Any]],
    ) -> models.User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        if update_data.get("roles") or update_data.get("roles") == []:
            roles = await db.execute(
                select(models.Role).filter(models.Role.name.in_(obj_in.roles))
            )
            db_obj.roles = roles.scalars().all()
            del update_data["roles"]
        if update_data.get("study_areas") or update_data.get("study_areas") == []:
            study_areas = await db.execute(
                select(models.StudyArea).filter(
                    models.StudyArea.id.in_(obj_in.study_areas)
                )
            )
            db_obj.study_areas = study_areas.scalars().all()
            del update_data["study_areas"]

        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def authenticate(
        self, db: AsyncSession, *, email: str, password: str
    ) -> Optional[models.User]:
        user = await self.get_by_key(db, key="email", value=email)

        if not user or len(user) == 0:
            return None
        else:
            user = user[0]
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def get_active_study_area(self, db: AsyncSession, user: models.User):
        study_area = await CRUDBase(models.StudyArea).get(
            db, id=user.active_study_area_id
        )

        world_extent = Polygon(
            [[-180, 85], [-180, -85], [180, -85], [180, 85], [-180, 85]]
        )
        study_area_geom = to_shape(study_area.geom)
        buffer_geom_heatmap = to_shape(study_area.buffer_geom_heatmap)

        study_area_crop = world_extent.difference(study_area_geom)
        study_area.geom = from_shape(study_area_crop)

        study_area_dict = dict(study_area)
        study_area_dict["bounds"] = buffer_geom_heatmap.bounds

        return study_area_dict

    def is_active(self, user: models.User) -> bool:
        return user.is_active

    def is_superuser(self, user: models.User) -> bool:
        role = [r for r in user.roles if r.name == "superuser"]
        if len(role) > 0:
            return True
        return False

    async def user_study_area_starting_point_access(
        self, db: AsyncSession, user_id: int, points: list[IsochroneStartingPointCoord]
    ) -> bool:
        user = await self.get(db, id=user_id, extra_fields=[models.User.study_areas])

        points = [Point(point.lon, point.lat) for point in points]
        study_area_geoms = [study_area.shape_of_geom for study_area in user.study_areas]
        for point in points:
            for study_area in study_area_geoms:
                if study_area.contains(point):
                    break
            else:
                # if no study area contains the point, return False
                return False

        # if all if statements breaked (i.e. all points are in a study area), return True
        return True


user = CRUDUser(models.User)
