from operator import or_
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy import delete, func
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

    def order_by(self, statement: select, ordering: str):
        if not ordering:
            return statement
        orders = ordering.split(",")
        for order in orders:
            order_ = order
            if order.startswith("-"):
                order_ = order[1:]
            if hasattr(self.model, order_):
                attribute_order = getattr(self.model, order_)
                if order.startswith("-"):
                    attribute_order = attribute_order.desc()
                statement = statement.order_by(attribute_order)

        return statement

    def search(self, statement: select, query: str):
        if not hasattr(self.model.Config, "search_fields") or not query:
            return statement
        search_objects = set()
        for field in self.model.Config.search_fields:
            column = getattr(self.model, field)
            containes = column.ilike(query.lower())
            search_objects.add(containes)
        statement = statement.filter(or_(*search_objects))
        return statement

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
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        extra_fields: List[Any] = [],
        ordering: str = None,
        query: str = None,
    ) -> List[ModelType]:
        statement = select(self.model).offset(skip).limit(limit)
        statement = self.extend_statement(statement, extra_fields=extra_fields)
        statement = self.order_by(statement, ordering)
        statement = self.search(statement, query)
        result = await db.execute(statement)
        return result.scalars().all()

    async def get_multi_by_key(
        self,
        db: AsyncSession,
        *,
        key: str,
        value: Any,
        skip: int = 0,
        limit: int = 100,
        extra_fields: List[Any] = [],
    ) -> List[ModelType]:
        statement = (
            select(self.model).offset(skip).limit(limit).where(getattr(self.model, key) == value)
        )
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
