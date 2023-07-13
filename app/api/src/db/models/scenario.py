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
    SQLModel,
)
from uuid import UUID
from ._base_class import DateTimeBase

if TYPE_CHECKING:
    from .user import User
    from .layer import Layer


class Scenario(DateTimeBase, table=True):
    __tablename__ = "scenario"
    __table_args__ = {"schema": "customer"}

    id: Optional[UUID] = Field(
        sa_column=Column(Text, primary_key=True, nullable=False, server_default=text("uuid_generate_v4()"))
    )
    name: str = Field(sa_column=Column(Text, nullable=False))
    user_id: UUID = Field(
        default=None,
        sa_column=Column(
            Text, ForeignKey("customer.user.id", ondelete="CASCADE"), nullable=False
        ),
    )

    user: "User" = Relationship(back_populates="scenarios")
    layers: List["Layer"] = Relationship(back_populates="scenario")
