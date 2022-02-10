from typing import Any, Dict, Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.core.security import get_password_hash, verify_password
from src.crud.base import CRUDBase
from src.db import models
from src.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[models.User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[models.User]:
        result = await db.execute(select(models.User).filter(models.User.email == email))
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> models.User:
        db_obj = models.User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            name=obj_in.name,
            surname=obj_in.surname,
            is_active=obj_in.is_active,
            organization_id=obj_in.organization_id,
        )
        roles = await db.execute(select(models.Role).filter(models.Role.name.in_(obj_in.roles)))
        db_obj.roles = roles.scalars().all()
        study_areas = await db.execute(
            select(models.StudyArea).filter(models.StudyArea.id.in_(obj_in.study_areas))
        )
        db_obj.study_areas = study_areas.scalars().all()
        obj_out = await super().create(db, obj_in=db_obj)
        for study_area in obj_out.study_areas:
            delattr(study_area, "geom")
        delattr(obj_out, "hashed_password")
        return obj_out

    async def update(
        self, db: AsyncSession, *, db_obj: models.User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> models.User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def authenticate(
        self, db: AsyncSession, *, email: str, password: str
    ) -> Optional[models.User]:
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def create_role(self, db: AsyncSession, *, name: str) -> models.Role:
        role = await db.execute(select(models.Role).filter(models.Role.name == name))
        if not role.scalars().first():
            role = models.Role(name=name)
            db.add(role)
            await db.commit()
            await db.refresh(role)
            return role
        else:
            return role

    async def create_study_area(
        self, db: AsyncSession, *, user_id: int, study_area_id
    ) -> models.User:
        user = await db.execute(select(models.User).filter(models.User.id == user_id))
        if not user.scalars().first():
            raise ValueError("User not found")
        study_area = await db.execute(
            select(models.StudyArea).filter(models.StudyArea.id == study_area_id)
        )
        if not study_area.scalars().first():
            raise ValueError("Study area not found")
        user.study_areas.append(study_area.scalars().first())
        await db.commit()
        await db.refresh(user)
        return user

    def is_active(self, user: models.User) -> bool:
        return user.is_active

    def is_superuser(self, user: models.User) -> bool:
        role = user.roles.filter(models.Role.name == "superuser").scalars().first()
        if role:
            return True
        return False


user = CRUDUser(models.User)
