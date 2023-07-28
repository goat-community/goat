from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlmodel import (
    Column,
    Field,
    ForeignKey,
    Relationship,
    Text,
    text,
)

from ._base_class import DateTimeBase

if TYPE_CHECKING:
    from .layer import Layer
    from .user import User


class Scenario(DateTimeBase, table=True):
    __tablename__ = "scenario"
    __table_args__ = {"schema": "customer"}

    id: Optional[UUID] = Field(
        sa_column=Column(
            Text, primary_key=True, nullable=False, server_default=text("uuid_generate_v4()")
        )
    )
    name: str = Field(sa_column=Column(Text, nullable=False))
    user_id: UUID = Field(
        default=None,
        sa_column=Column(Text, ForeignKey("customer.user.id", ondelete="CASCADE"), nullable=False),
    )

    user: "User" = Relationship(back_populates="scenarios")
    # layers: List["Layer"] = Relationship(back_populates="scenario")
