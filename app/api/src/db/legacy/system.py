from typing import TYPE_CHECKING, Optional

from sqlmodel import (
    Column,
    Field,
    Integer,
    SQLModel,
    Text,
    text
)

from sqlalchemy.dialects.postgresql import JSONB


class System(SQLModel, table=True):
    __tablename__ = "system"
    __table_args__ = {"schema": "customer"}

    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    type: str = Field(sa_column=Column(Text, nullable=False))
    setting: dict = Field(sa_column=Column(JSONB, nullable=False))
