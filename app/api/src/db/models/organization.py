from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Column, DateTime, Field, Relationship, SQLModel, Text, text, Integer

if TYPE_CHECKING:
    from .user import User


class Organization(SQLModel, table=True):
    __tablename__ = "organization"
    __table_args__ = {"schema": "customer"}

    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    name: Optional[str] = Field(sa_column=Column(Text, nullable=False))
    creation_date: Optional[datetime] = Field(
        sa_column=Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    )

    users: List["User"] = Relationship(back_populates="organization")
