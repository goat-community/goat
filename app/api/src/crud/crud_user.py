from typing import Any, Dict, Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.core.security import get_password_hash, verify_password
from src.crud.base import CRUDBase
from src.db.models.customer.user import User as UserDB
from src.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[UserDB, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[UserDB]:
        result = await db.execute(select(UserDB).filter(UserDB.email == email))
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> UserDB:
        db_obj = UserDB(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            name=obj_in.name,
            surname=obj_in.surname,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: UserDB,
        obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> UserDB:
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
    ) -> Optional[UserDB]:
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: UserDB) -> bool:
        return user.is_active

    def is_superuser(self, user: UserDB) -> bool:
        return user.is_superuser


user = CRUDUser(UserDB)
