from datetime import date
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.dialects.postgresql import JSONB

if TYPE_CHECKING:
    from .study_area import StudyArea

from geoalchemy2 import Geometry
from sqlmodel import Column, Field, Integer, Relationship, SQLModel, Text, UniqueConstraint, ARRAY, DateTime, Index

from src.resources.enums import GeostoreType

from ._link_model import StudyAreaGeostore


class RegionR5(SQLModel, table=True):
    __tablename__ = "region_r5"
    __table_args__ = {"schema": "basic"}

    id: Optional[int] = Field(sa_column=Column(Text, primary_key=True))
    name: str = Field(sa_column=Column(Text), nullable=False)
    reference_dates: list[date] = Field(sa_column=Column(ARRAY(DateTime()), nullable=False))
    geom: str = Field(
        sa_column=Column(
            Geometry(geometry_type="MultiPolygon", srid="4326", spatial_index=False),
            nullable=False,
        )
    )
    buffer_geom: str = Field(
        sa_column=Column(
            Geometry(geometry_type="MultiPolygon", srid="4326", spatial_index=False),
            nullable=False,
        )
    )


Index("idx_region_r5_geom", RegionR5.__table__.c.geom, postgresql_using="gist")
Index("idx_region_r5_buffer_geom", RegionR5.__table__.c.buffer_geom, postgresql_using="gist")
UniqueConstraint(RegionR5.__table__.c.name)