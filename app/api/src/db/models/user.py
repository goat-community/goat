from typing import TYPE_CHECKING, List
from sqlmodel import (
    Relationship,
)
from ._base_class import UUIDBase

if TYPE_CHECKING:
    from .content import Content
    from .scenario import Scenario


class User(UUIDBase, table=True):
    __tablename__ = "user"
    __table_args__ = {"schema": "customer"}

    # Relationships
    scenarios: List["Scenario"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    contents: List["Content"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
