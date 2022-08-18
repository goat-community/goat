from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import RelationshipProperty, selectinload

from src.db.models._base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def extend_statement(self, statement: select, *, extra_fields: List[Any] = []) -> select:
        for field in extra_fields:
            if (
                hasattr(field, "property")
                and isinstance(field.property, RelationshipProperty)
                and hasattr(self.model, field.key)
            ):
                statement = statement.options(selectinload(field))
        return statement

    async def get(
        self, db: AsyncSession, id: Any, extra_fields: List[Any] = []
    ) -> Optional[ModelType]:
        statement = select(self.model).where(self.model.id == id)
        statement = self.extend_statement(statement, extra_fields=extra_fields)
        result = await db.execute(statement)
        return result.scalars().first()

    async def get_all(self, db: AsyncSession, *, extra_fields: List[Any] = []) -> List[ModelType]:
        statement = select(self.model)
        statement = self.extend_statement(statement, extra_fields=extra_fields)
        result = await db.execute(statement)
        return result.scalars().all()

    async def get_by_key(
        self, db: AsyncSession, *, key: str, value: Any, extra_fields: List[Any] = []
    ) -> Optional[ModelType]:
        statement = select(self.model).where(getattr(self.model, key) == value)
        statement = self.extend_statement(statement)
        result = await db.execute(statement)
        return result.scalars().all()

    async def get_by_multi_keys(
        self, db: AsyncSession, *, keys: Dict[str, Any], extra_fields: List[Any] = []
    ) -> List[ModelType]:
        statement = select(self.model)
        for key, value in keys.items():
            statement = statement.where(getattr(self.model, key) == value)
        statement = self.extend_statement(statement, extra_fields=extra_fields)
        result = await db.execute(statement)
        return result.scalars().all()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100, extra_fields: List[Any] = []
    ) -> List[ModelType]:
        statement = select(self.model).offset(skip).limit(limit)
        statement = self.extend_statement(statement, extra_fields=extra_fields)
        result = await db.execute(statement)
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        db_obj = self.model.from_orm(obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        fields = obj_in.__fields__.keys()
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in fields:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> ModelType:
        obj = await db.get(self.model, id)
        await db.delete(obj)
        await db.commit()
        return obj

    async def remove_multi(self, db: AsyncSession, *, ids: Union[int, List[int]]) -> ModelType:
        if type(ids) == int:
            ids = [ids]
        statement = delete(self.model).where(self.model.id.in_(ids))
        await db.execute(statement)
        await db.commit()

        # Return empty string at the moment
        # TODO: add removed items instead.
        return ""

    async def remove_multi_by_key(self, db: AsyncSession, *, key: str, values: Any) -> ModelType:
        if not type(values) == list:
            values = [values]
        statement = delete(self.model).where(getattr(self.model, key).in_(values))
        await db.execute(statement)
        await db.commit()

        # Return empty string at the moment
        # TODO: add removed items instead.
        return ""

    async def get_n_rows(self, db: AsyncSession, *, n: int) -> ModelType:
        statement = select(self.model).limit(n)
        result = await db.execute(statement)
        return result.scalars().all()
