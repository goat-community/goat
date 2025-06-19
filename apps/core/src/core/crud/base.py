from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import BaseModel, ValidationError
from sqlalchemy import delete, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import RelationshipProperty, selectinload
from sqlalchemy.sql import Select
from sqlmodel import SQLModel

from core.schemas import OrderEnum

ModelType = TypeVar("ModelType", bound=BaseModel)
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

    def extend_statement(
        self, statement: select, *, extra_fields: List[Any] = []
    ) -> select:
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
    ) -> SQLModel | None:
        statement = select(self.model).where(self.model.id == id)
        statement = self.extend_statement(statement, extra_fields=extra_fields)
        result = await db.execute(statement)
        return result.scalars().first()

    async def get_all(
        self, db: AsyncSession, *, extra_fields: List[Any] = []
    ) -> List[ModelType]:
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
        query: SQLModel | Select | None = None,
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
            search_query = []
            for key, value in search_text.items():
                # Search for text in specified column make both input and column lowercase
                search_query.append(
                    func.lower(getattr(self.model, key)).contains(value.lower())
                )
            query = query.where(or_(*search_query))

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
            assert type(query) == Select
            result = await paginate(db, query, page_params)
            return result

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        db_obj = self.model.model_validate(obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: SQLModel,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]] | None = None,
    ) -> SQLModel:
        if isinstance(obj_in, dict):
            update_data = obj_in
            fields = obj_in.keys()
        elif isinstance(obj_in, BaseModel):
            update_data = obj_in.dict(exclude_unset=True)
            fields = obj_in.__fields__.keys()
        elif obj_in is None:
            update_data = {}
            fields = []
        else:
            raise ValueError(
                "Obj_in must be either a dict or a Pydantic model or None."
            )

        for field in fields:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        # Create a new object from the updated object to validate it in case the layer has validators.
        if hasattr(self.model, '__pydantic_decorators__') and self.model.__pydantic_decorators__.validators:
            try:
                validated_obj = self.model(**db_obj.model_dump())
                for field in self.model.model_fields.keys():
                    setattr(db_obj, field, getattr(validated_obj, field))
            except ValidationError as e:
                raise e
        return db_obj

    async def update_multi(
        self,
        db: AsyncSession,
        *,
        db_objs: ModelType,
        objs_in: List[Union[UpdateSchemaType, Dict[str, Any]]],
    ) -> List[ModelType]:
        """Update multiple objects at once by id."""
        ids = []
        # Loop through all db_objs and objs_in and update the db_obj with the obj_in.
        for db_obj, obj_in in zip(db_objs, objs_in, strict=True):
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
            ids.append(db_obj.id)
        await db.commit()

        # Get objects again to return them. Refresh cannot be used as it only returns one object.
        ids = [db_obj.id for db_obj in db_objs]
        statement = select(self.model).where(self.model.id.in_(ids))
        result = await db.execute(statement)
        return result.scalars().all()

    async def remove(self, db: AsyncSession, *, id: int) -> ModelType:
        obj = await db.get(self.model, id)
        await db.delete(obj)
        await db.commit()
        return obj

    async def delete(self, db: AsyncSession, *, id: int) -> ModelType:
        return await self.remove(db, id=id)

    async def remove_multi(
        self, db: AsyncSession, *, ids: Union[int, List[int]]
    ) -> ModelType:
        if type(ids) == int:
            ids = [ids]
        statement = delete(self.model).where(self.model.id.in_(ids))
        await db.execute(statement)
        await db.commit()

        # Return empty string at the moment
        # TODO: add removed items instead.
        return ""

    async def remove_multi_by_key(
        self, db: AsyncSession, *, key: str, values: Any
    ) -> ModelType:
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
