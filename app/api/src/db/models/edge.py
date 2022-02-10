from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from geoalchemy2 import Geometry
from sqlalchemy import SmallInteger
from sqlalchemy.orm import backref
from sqlmodel import (
    JSON,
    BigInteger,
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
    from .heatmap import ReachedEdgeHeatmap
    from .node import Node
    from .scenario import Scenario


class EdgeBase(SQLModel):
    id: int = Field(primary_key=True)
    class_id: int = Field(nullable=False)
    length_m: float = Field(sa_column=Column(Float(53), nullable=False))
    name: Optional[str] = Field(sa_column=Column(Text))
    one_way: Optional[int]
    maxspeed_forward: Optional[int]
    maxspeed_backward: Optional[int]
    osm_id: Optional[int] = Field(sa_column=Column(BigInteger()))
    bicycle: Optional[str] = Field(sa_column=Column(Text, index=True))
    foot: Optional[str] = Field(sa_column=Column(Text, index=True))
    oneway: Optional[str] = Field(sa_column=Column(Text))
    crossing: Optional[str] = Field(sa_column=Column(Text))
    one_link_crossing: Optional[bool]
    crossing_delay_category: Optional[int] = Field(sa_column=Column(SmallInteger))
    bicycle_road: Optional[str] = Field(sa_column=Column(Text))
    cycleway: Optional[str] = Field(sa_column=Column(Text))
    highway: Optional[str] = Field(sa_column=Column(Text))
    incline: Optional[str] = Field(sa_column=Column(Text))
    incline_percent: Optional[int]
    lanes: Optional[float] = Field(sa_column=Column(Float(53)))
    lit: Optional[str] = Field(sa_column=Column(Text))
    lit_classified: Optional[str] = Field(sa_column=Column(Text))
    parking: Optional[str] = Field(sa_column=Column(Text))
    parking_lane_both: Optional[str] = Field(sa_column=Column(Text))
    parking_lane_right: Optional[str] = Field(sa_column=Column(Text))
    parking_lane_left: Optional[str] = Field(sa_column=Column(Text))
    segregated: Optional[str] = Field(sa_column=Column(Text))
    sidewalk: Optional[str] = Field(sa_column=Column(Text))
    sidewalk_both_width: Optional[float] = Field(sa_column=Column(Float(53)))
    sidewalk_left_width: Optional[float] = Field(sa_column=Column(Float(53)))
    sidewalk_right_width: Optional[float] = Field(sa_column=Column(Float(53)))
    smoothness: Optional[str] = Field(sa_column=Column(Text))
    surface: Optional[str] = Field(sa_column=Column(Text))
    wheelchair: Optional[str] = Field(sa_column=Column(Text))
    wheelchair_classified: Optional[str] = Field(sa_column=Column(Text))
    width: Optional[float] = Field(sa_column=Column(Float(53)))
    s_imp: Optional[float] = Field(sa_column=Column(Float(53)))
    rs_imp: Optional[float] = Field(sa_column=Column(Float(53)))
    impedance_surface: Optional[float] = Field(sa_column=Column(Float(53)))
    death_end: Optional[int]
    geom: str = Field(
        sa_column=Column(
            Geometry(geometry_type="Linestring", srid="4326", spatial_index=False),
            nullable=False,
        )
    )
    edge_id: Optional[int] = Field(index=True, default=None, foreign_key="basic.edge.id")
    scenario_id: Optional[int] = Field(
        sa_column=Column(
            Integer, ForeignKey("customer.scenario.id", ondelete="CASCADE"), index=True
        )
    )


class Edge(EdgeBase, table=True):
    __tablename__ = "edge"
    __table_args__ = {"schema": "basic"}

    length_3857: float = Field(sa_column=Column(Float(53), nullable=False))
    coordinates_3857: Optional[str] = Field(sa_column=Column(JSON, nullable=False))
    source: int = Field(index=True, nullable=False, foreign_key="basic.node.id")
    target: int = Field(index=True, nullable=False, foreign_key="basic.node.id")

    node_source: Optional["Node"] = Relationship(back_populates="edges_source")
    node_target: Optional["Node"] = Relationship(back_populates="edges_target")
    reached_edge_heatmaps: List["ReachedEdgeHeatmap"] = Relationship(back_populates="edge")
    scenario: Optional["Scenario"] = Relationship(back_populates="edges")
    children: List["Edge"] = Relationship(
        sa_relationship_kwargs=dict(
            cascade="all",
            backref=backref("parent", remote_side="Edge.id"),
        )
    )


Index("idx_edge_geom", Edge.__table__.c.geom, postgresql_using="gist")


class WayModified(EdgeBase, table=True):
    __tablename__ = "way_modified"
    __table_args__ = {"schema": "customer"}

    way_type: Optional[str] = Field(sa_column=Column(Text))
    edit_type: Optional[str] = Field(sa_column=Column(Text))
    creation_date: datetime = Field(
        sa_column=Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    )
    scenario: Optional["Scenario"] = Relationship(back_populates="ways_modified")

    children: List["WayModified"] = Relationship(
        sa_relationship_kwargs=dict(
            cascade="all",
            backref=backref("parent", remote_side="WayModified.id"),
        )
    )


Index("idx_way_modified_geom", WayModified.__table__.c.geom, postgresql_using="gist")
