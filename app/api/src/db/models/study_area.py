from typing import TYPE_CHECKING, List, Optional

from geoalchemy2 import Geometry
from sqlmodel import (
    Column,
    Field,
    Float,
    Index,
    Relationship,
    SmallInteger,
    SQLModel,
    Text,
    Integer
)

if TYPE_CHECKING:
    from .grid import GridVisualization
    from .user import User

from ._link_model import StudyAreaGridVisualization, UserStudyArea


class StudyArea(SQLModel, table=True):
    __tablename__ = "study_area"
    __table_args__ = {"schema": "basic"}

    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    name: str = Field(sa_column=Column(Text, nullable=False))
    population: int = Field(nullable=False)
    geom: str = Field(
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
