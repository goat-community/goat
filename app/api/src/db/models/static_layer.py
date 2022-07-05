from datetime import datetime
from tokenize import String
from typing import TYPE_CHECKING, Optional

from sqlmodel import (
    ARRAY,
    Column,
    DateTime,
    Field,
    ForeignKey,
    Integer,
    Relationship,
    SQLModel,
    String,
    Text,
    text,
)

if TYPE_CHECKING:
    from .user import User


class StaticLayer(SQLModel, table=True):

    __tablename__ = "static_layer"
    __table_args__ = {"schema": "customer"}

    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    creation_date: Optional[datetime] = Field(
        sa_column=Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    )
    user_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("customer.user.id", ondelete="CASCADE"), nullable=False
        )
    )
    table_name: str = Field(sa_column=Column(String(63), nullable=False, unique=True))

    user: "User" = Relationship(back_populates="data_uploads")
