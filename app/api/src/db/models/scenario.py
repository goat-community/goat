from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy.dialects import postgresql
from sqlmodel import (
    Column,
    Field,
    ForeignKey,
    Integer,
    Relationship,
    SQLModel,
    Text,
    text,
)
from uuid import UUID
from ._base_class import UUIDAutoBase, DateTimeBase

if TYPE_CHECKING:
    from .user import User
    from .layer import Layer


class Scenario(UUIDAutoBase, DateTimeBase, table=True):
    __tablename__ = "scenario"
    __table_args__ = {"schema": "customer"}

    name: str = Field(sa_column=Column(Text, nullable=False))
    user_id: UUID = Field(
        default=None,
        sa_column=Column(
            Integer, ForeignKey("customer.user.id", ondelete="CASCADE"), nullable=False
        ),
    )

    user: "User" = Relationship(back_populates="scenarios")
    layers: List["Layer"] = Relationship(back_populates="scenario")
