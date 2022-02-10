from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import (
    ARRAY,
    Column,
    DateTime,
    Field,
    ForeignKey,
    Integer,
    Relationship,
    SQLModel,
    Text,
    text,
)

if TYPE_CHECKING:
    from .aoi import AoiModified
    from .building import BuildingModified
    from .edge import Edge, WayModified
    from .heatmap import ReachedEdgeHeatmap, ReachedPoiHeatmap
    from .isochrone import IsochroneCalculation
    from .node import Node
    from .poi import PoiModified
    from .population import PopulationModified
    from .user import User


class Scenario(SQLModel, table=True):
    __tablename__ = "scenario"
    __table_args__ = {"schema": "customer"}

    id: int = Field(primary_key=True)
    scenario_name: str = Field(sa_column=Column(Text, nullable=False))
    deleted_ways: List[int] = Field(
        sa_column=Column(ARRAY(Integer()), server_default=text("'{}'::int[]"))
    )
    deleted_pois: List[str] = Field(
        sa_column=Column(ARRAY(Text()), server_default=text("'{}'::text[]"))
    )
    deleted_buildings: List[int] = Field(
        sa_column=Column(ARRAY(Integer()), server_default=text("'{}'::int[]"))
    )
    routing_heatmap_computed: Optional[bool]
    creation_date: datetime = Field(
        sa_column=Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    )
    user_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("customer.user.id", ondelete="CASCADE"), nullable=False
        ),
    )

    user: "User" = Relationship(back_populates="scenarios")
    isochrone_calculations: List["IsochroneCalculation"] = Relationship(back_populates="scenario")
    pois_modified: List["PoiModified"] = Relationship(back_populates="scenario")
    aois_modified: List["AoiModified"] = Relationship(back_populates="scenario")
    populations_modified: List["PopulationModified"] = Relationship(back_populates="scenario")
    buildings_modified: List["BuildingModified"] = Relationship(back_populates="scenario")
    edges: List["Edge"] = Relationship(back_populates="scenario")
    ways_modified: List["WayModified"] = Relationship(back_populates="scenario")
    nodes: List["Node"] = Relationship(back_populates="scenario")
    reached_edge_heatmaps: List["ReachedEdgeHeatmap"] = Relationship(back_populates="scenario")
    reached_poi_heatmaps: List["ReachedPoiHeatmap"] = Relationship(back_populates="scenario")
