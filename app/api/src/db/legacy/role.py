from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Column, Field, Integer, Relationship, SQLModel, Text

if TYPE_CHECKING:
    from .customization import Customization
    from .user import User

from ._link_model import UserRole


class Role(SQLModel, table=True):
    __tablename__ = "role"
    __table_args__ = {"schema": "customer"}

    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    name: str = Field(sa_column=Column(Text, nullable=False))

    customizations: List["Customization"] = Relationship(back_populates="role")
    users: List["User"] = Relationship(back_populates="roles", link_model=UserRole)
