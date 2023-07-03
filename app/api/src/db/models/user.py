from typing import TYPE_CHECKING, List
from sqlmodel import (
    Relationship,
    Text, 
    Field,
    Column,
    SQLModel,
)
from uuid import UUID

if TYPE_CHECKING:
    from .content import Content
    from .scenario import Scenario


class User(SQLModel, table=True):
    __tablename__ = "user"
    __table_args__ = {"schema": "customer"}

    id: UUID = Field(sa_column=Column(Text, primary_key=True, nullable=False))
    # Relationships
    scenarios: List["Scenario"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    contents: List["Content"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
