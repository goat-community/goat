from typing import TYPE_CHECKING, List, Optional

from geoalchemy2 import Geometry
from pydantic import validator
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import (
    Column,
    Field,
    Float,
    Index,
    Integer,
    Relationship,
    SmallInteger,
    SQLModel,
    Text,
)

from shapely.wkb import loads
from geoalchemy2.shape import to_shape

if TYPE_CHECKING:
    from .user import User
    from .customization import UserCustomization
    from .data_upload import DataUpload
    from .opportunity_config import OpportunityStudyAreaConfig, OpportunityUserConfig
    from .geostore import Geostore

from ._link_model import UserStudyArea, StudyAreaGeostore
from ._pydantic_geometry import dump_geom


class StudyArea(SQLModel, table=True):
    __tablename__ = "study_area"
    __table_args__ = {"schema": "basic"}

    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    name: str = Field(sa_column=Column(Text, nullable=False))
    population: int = Field(nullable=False)
    setting: dict = Field(sa_column=Column(JSONB, nullable=False))
    geom: str = Field(
        sa_column=Column(
            Geometry(geometry_type="MultiPolygon", srid="4326", spatial_index=False),
            nullable=False,
        )
    )
    # Buffer geom by 1600 meters which is the flying bird distance for 20 minutes walking with a speed of 5km/h
    buffer_geom_heatmap: str = Field(
        sa_column=Column(
            Geometry(geometry_type="MultiPolygon", srid="4326", spatial_index=False),
            nullable=False,
        )
    )
    sub_study_areas: List["SubStudyArea"] = Relationship(back_populates="study_area")
    users: List["User"] = Relationship(back_populates="study_areas", link_model=UserStudyArea)
    user_customizations: List["UserCustomization"] = Relationship(back_populates="study_areas")
    data_uploads: List["DataUpload"] = Relationship(back_populates="study_area")
    opportunity_study_area_configs: List["OpportunityStudyAreaConfig"] = Relationship(
        back_populates="study_area"
    )
    opportunity_user_configs: List["OpportunityUserConfig"] = Relationship(
        back_populates="study_area"
    )
    geostores: List["Geostore"] = Relationship(
        back_populates="study_areas", link_model=StudyAreaGeostore
    )
    _validate_geom = validator("geom", pre=True, allow_reuse=True)(dump_geom)

    @property
    def shape_of_geom(self):
        return loads(bytes.fromhex(to_shape(self.geom).wkb_hex))


Index("idx_study_area_geom", StudyArea.__table__.c.geom, postgresql_using="gist")


class SubStudyArea(SQLModel, table=True):
    __tablename__ = "sub_study_area"
    __table_args__ = {"schema": "basic"}

    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    name: str = Field(sa_column=Column(Text, nullable=False))
    population: int = Field(nullable=False)
    default_building_levels: Optional[int] = Field(sa_column=Column(SmallInteger))
    default_roof_levels: Optional[int] = Field(sa_column=Column(SmallInteger))
    area: Optional[float] = Field(sa_column=Column(Float(53)))
    geom: str = Field(
        sa_column=Column(
            Geometry(geometry_type="MultiPolygon", srid="4326", spatial_index=False),
            nullable=False,
        )
    )
    study_area_id: int = Field(foreign_key="basic.study_area.id", index=True, nullable=False)

    study_area: "StudyArea" = Relationship(back_populates="sub_study_areas")


Index("idx_sub_study_area_geom", SubStudyArea.__table__.c.geom, postgresql_using="gist")
