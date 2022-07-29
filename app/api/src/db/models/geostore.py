from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.dialects.postgresql import JSONB

if TYPE_CHECKING:
    from .study_area import StudyArea

from ._link_model import StudyAreaGeostore

from sqlmodel import (
    Column,
    Field,
    Integer,
    Relationship,
    SQLModel,
    Text
)

class Geostore(SQLModel, table=True):
    __tablename__ = "geostore"
    __table_args__ = {"schema": "customer"}

    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    name: str = Field(sa_column=Column(Text), nullable=False)
    type: str = Field(sa_column=Column(Text), nullable=False)
    url: str = Field(sa_column=Column(Text), nullable=False)
    configuration: Optional[dict] = Field(sa_column=Column(JSONB))
    attribution: str = Field(sa_column=Column(Text), nullable=False)
    thumbnail_url: str = Field(sa_column=Column(Text), nullable=False)
    study_areas: List["StudyArea"] = Relationship(back_populates="geostores", link_model=StudyAreaGeostore)



