from typing import TYPE_CHECKING, List

from sqlmodel import Column, Field, Relationship, SQLModel, Text

if TYPE_CHECKING:
    from .customization import Customization


class Role(SQLModel, table=True):
    __tablename__ = "role"
    __table_args__ = {"schema": "customer"}

    id: int = Field(primary_key=True)
    name: str = Field(sa_column=Column(Text, nullable=False))

    customizations: List["Customization"] = Relationship(back_populates="role")
