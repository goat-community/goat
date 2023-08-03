from typing import TYPE_CHECKING, List
from uuid import UUID

from sqlmodel import (
    Column,
    Field,
    Relationship,
    SQLModel,
)

from sqlalchemy.dialects.postgresql import UUID as UUID_PG

if TYPE_CHECKING:
    from .scenario import Scenario
    from .folder import Folder


class User(SQLModel, table=True):
    __tablename__ = "user"
    __table_args__ = {"schema": "customer"}

    id: UUID = Field(sa_column=Column(UUID_PG(as_uuid=True), primary_key=True, nullable=False))
    # Relationships
    scenarios: List["Scenario"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    folders: List["Folder"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
