from datetime import datetime
from tokenize import String
from typing import TYPE_CHECKING, Optional

import sqlalchemy
from sqlalchemy.dialects import postgresql
from sqlmodel import (
    Column,
    DateTime,
    Field,
    ForeignKey,
    Integer,
    Relationship,
    SQLModel,
    String,
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
        default=None,
        sa_column=Column(
            Integer, ForeignKey("customer.user.id", ondelete="CASCADE"), nullable=False
        )
    )
    table_name: str = Field(sa_column=Column(String(63), nullable=False, unique=True))

    user: "User" = Relationship(back_populates="static_layers")

    def data_frame_raw_sql(self, limit: int = 100, offset: int = 0) -> str:
        """
        Raw sql to get data frame using geopands
        """
        metadata_obj = sqlalchemy.MetaData()
        table = sqlalchemy.Table(self.table_name, metadata_obj, schema="extra")
        query = sqlalchemy.select(table, "*").limit(limit).offset(offset)
        raw_query = query.compile(
            dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}
        )
        return str(raw_query)
