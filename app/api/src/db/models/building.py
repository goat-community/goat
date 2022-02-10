from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from geoalchemy2 import Geometry
from sqlalchemy import SmallInteger
from sqlmodel import (
    Column,
    DateTime,
    Field,
    Float,
    ForeignKey,
    Index,
    Integer,
    Relationship,
    SQLModel,
    Text,
    text,
)

if TYPE_CHECKING:
    from .population import Population, PopulationModified
    from .scenario import Scenario


class BuildingBase(SQLModel):
    id: int = Field(primary_key=True)
    building: Optional[str] = Field(sa_column=Column(Text))
    amenity: Optional[str] = Field(sa_column=Column(Text))
    residential_status: Optional[str] = Field(sa_column=Column(Text))
    housenumber: Optional[str] = Field(sa_column=Column(Text))
    street: Optional[str] = Field(sa_column=Column(Text))
    building_levels: Optional[int] = Field(sa_column=Column(SmallInteger))
    building_levels_residential: Optional[int] = Field(sa_column=Column(SmallInteger))
    roof_levels: Optional[int] = Field(sa_column=Column(SmallInteger))
    height: Optional[float] = Field(sa_column=Column(Float(53)))
    area: Optional[int]
    gross_floor_area_residential: Optional[int]
    geom: str = Field(
        sa_column=Column(
            Geometry(geometry_type="Polygon", srid="4326", spatial_index=False),
            nullable=False,
        )
    )


class Building(BuildingBase, table=True):
    __tablename__ = "building"
    __table_args__ = {"schema": "basic"}

    osm_id: Optional[int]

    populations: List["Population"] = Relationship(back_populates="building")
    buildings_modified: List["BuildingModified"] = Relationship(back_populates="building")


Index("idx_building_geom", Building.__table__.c.geom, postgresql_using="gist")


class BuildingModified(BuildingBase, table=True):
    __tablename__ = "building_modified"
    __table_args__ = {"schema": "customer"}

    creation_date: datetime = Field(
        sa_column=Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    )
    building_id: Optional[int] = Field(
        sa_column=Column(
            Integer, ForeignKey("basic.building.id", ondelete="CASCADE"), default=None
        ),
    )
    scenario_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("customer.scenario.id", ondelete="CASCADE"),
            index=True,
            nullable=False,
        ),
    )

    building: Optional["Building"] = Relationship(back_populates="buildings_modified")
    scenario: "Scenario" = Relationship(back_populates="buildings_modified")
    populations_modified: Optional[List["PopulationModified"]] = Relationship(
        back_populates="building_modified"
    )


Index("idx_building_modified_geom", BuildingModified.__table__.c.geom, postgresql_using="gist")
