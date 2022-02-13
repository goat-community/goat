from typing import Any, Dict, List, Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.core.security import get_password_hash, verify_password
from src.crud.base import CRUDBase
from src.db import models
from src.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[models.User, UserCreate, UserUpdate]):
    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> models.User:
        db_obj = models.User.from_orm(obj_in)
        db_obj.hashed_password = get_password_hash(obj_in.password)
        roles = await db.execute(select(models.Role).filter(models.Role.name.in_(obj_in.roles)))
        db_obj.roles = roles.scalars().all()
        study_areas = await db.execute(
            select(models.StudyArea).filter(models.StudyArea.id.in_(obj_in.study_areas))
        )
        db_obj.study_areas = study_areas.scalars().all()
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: models.User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> models.User:

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        if update_data.get("roles") or len(update_data["roles"]) == 0:
            roles = await db.execute(
                select(models.Role).filter(models.Role.name.in_(obj_in.roles))
            )
            db_obj.roles = roles.scalars().all()
            del update_data["roles"]
        if update_data.get("study_areas") or len(update_data["study_areas"]) == 0:
            study_areas = await db.execute(
                select(models.StudyArea).filter(models.StudyArea.id.in_(obj_in.study_areas))
            )
            db_obj.study_areas = study_areas.scalars().all()
            del update_data["study_areas"]

        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def authenticate(
        self, db: AsyncSession, *, email: str, password: str
    ) -> Optional[models.User]:
        user = await self.get_by_key(db, key="email", value=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: models.User) -> bool:
        return user.is_active

    def is_superuser(self, user: models.User) -> bool:
        role = [r for r in user.roles if r.name == "superuser"]
        if len(role) > 0:
            return True
        return False


user = CRUDUser(models.User)
