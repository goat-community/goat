from typing import TYPE_CHECKING, List
from sqlmodel import (
    Column,
    Field,
    SQLModel,
    Text,
    Relationship,
    text,
)
from uuid import UUID
from ._base_class import DateTimeBase
if TYPE_CHECKING:
    from .layer import Layer
    from src.schemas.data_store import DataStoreType
    
#TODO: Add further attributes for the different data store types 

class DataStoreBase(SQLModel):
    type: "DataStoreType" = Field(sa_column=Column(Text, nullable=False), description="Data store type")


class DataStore(DataStoreBase, DateTimeBase, table=True):
    """Content model."""
    __tablename__ = "data_store"
    __table_args__ = {"schema": "customer"}

    id: UUID | None = Field(
        sa_column=Column(Text, primary_key=True, nullable=False, server_default=text("uuid_generate_v4()"))
    )
    # Relationships
    layers: List["Layer"] = Relationship(back_populates="data_store")
