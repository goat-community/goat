from typing import TYPE_CHECKING, Dict, List, Optional

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

from src.db.models import data_upload

if TYPE_CHECKING:
    from .grid import GridVisualization
    from .user import User
    from .customization import UserCustomization
    from .data_upload import DataUpload
    from .poi_config import PoiStudyAreaConfig, PoiUserConfig

from ._link_model import StudyAreaGridVisualization, UserStudyArea
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
    grid_visualizations: List["GridVisualization"] = Relationship(
        back_populates="study_areas", link_model=StudyAreaGridVisualization
    )
    sub_study_areas: List["SubStudyArea"] = Relationship(back_populates="study_area")
    users: List["User"] = Relationship(back_populates="study_areas", link_model=UserStudyArea)
    # users_active: List["User"] = Relationship(back_populates="active_study_area")
    user_customizations: List["UserCustomization"] = Relationship(back_populates="study_areas")
    data_uploads: List["DataUpload"] = Relationship(back_populates="study_area")
    poi_study_area_configs: List["PoiStudyAreaConfig"] = Relationship(back_populates="study_area")
    poi_user_configs: List["PoiUserConfig"] = Relationship(back_populates="study_area")
    _validate_geom = validator("geom", pre=True, allow_reuse=True)(dump_geom)


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
