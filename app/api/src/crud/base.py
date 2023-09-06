from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import BaseModel
from sqlalchemy import delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import RelationshipProperty, selectinload
from sqlmodel import SQLModel
from sqlmodel.sql.expression import Select

from src.db.models._base_class import Base
from src.schemas import OrderEnum

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
T = TypeVar("T", bound=SQLModel)


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
        """
        Example of usage:
        get_by_multi_keys(db, keys={"name": "John", "age": 2})
        """

        statement = select(self.model)
        for key, value in keys.items():
            statement = statement.where(getattr(self.model, key) == value)
        statement = self.extend_statement(statement, extra_fields=extra_fields)
        result = await db.execute(statement)
        return result.scalars().all()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        query: T | Select[T] | None = None,
        page_params: Params | None = None,
        order_by: str | None = None,
        order: OrderEnum | None = OrderEnum.ascendent,
        extra_fields: List[Any] = [],
        search_text: dict | None = None,
    ) -> Page[ModelType] | List[ModelType]:
        if query is None:
            query = select(self.model)
        query = self.extend_statement(query, extra_fields=extra_fields)

        # Search for text in specified column
        if search_text is not None:
            for key, value in search_text.items():
                # Search for text in specified column make both input and column lowercase
                query = query.where(func.lower(getattr(self.model, key)).contains(value.lower()))

        columns = self.model.__table__.columns
        if order_by and order_by in columns:
            if order == OrderEnum.ascendent:
                query = query.order_by(columns[order_by].asc())
            else:
                query = query.order_by(columns[order_by].desc())

        if page_params is None:
            result = await db.execute(query)
            items = result.all()
            return items
        else:
            result = await paginate(db, query, page_params)
            return result

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        db_obj = self.model.from_orm(obj_in)
        db_obj = obj_in
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
        if isinstance(obj_in, dict):
            update_data = obj_in
            fields = obj_in.keys()
        else:
            update_data = obj_in.dict(exclude_unset=True)
            fields = obj_in.__fields__.keys()
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

    async def delete(self, db: AsyncSession, *, id: int) -> ModelType:
        return await self.remove(db, id=id)

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

    async def count(self, db: AsyncSession) -> int:
        """
        Count the number of rows in the table.
        """
        statement = select(func.count(self.model.id))
        result = await db.execute(statement)
        return result.scalar_one()
