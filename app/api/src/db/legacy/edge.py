from datetime import datetime
from typing import TYPE_CHECKING, Optional

from geoalchemy2 import Geometry
from sqlalchemy import SmallInteger
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
    Boolean
)

if TYPE_CHECKING:
    from .node import Node
    from .scenario import Scenario


class EdgeBase(SQLModel):
    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True))
    class_id: int = Field(nullable=False)
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


class Edge(EdgeBase, table=True):
    __tablename__ = "edge"
    __table_args__ = {"schema": "basic"}

    length_m: float = Field(sa_column=Column(Float(53), nullable=False))
    length_3857: float = Field(sa_column=Column(Float(53), nullable=False))
    coordinates_3857: Optional[dict] = Field(sa_column=Column(JSON, nullable=False))
    source: int = Field(index=True, nullable=False, foreign_key="basic.node.id")
    target: int = Field(index=True, nullable=False, foreign_key="basic.node.id")
    edge_id: Optional[int] = Field(index=True, default=None, foreign_key="basic.edge.id")
    scenario_id: Optional[int] = Field(
        sa_column=Column(
            Integer, ForeignKey("customer.scenario.id", ondelete="CASCADE"), index=True
        )
    )

    node_source: "Node" = Relationship(
        sa_relationship_kwargs={"primaryjoin": "Edge.source==Node.id", "lazy": "joined"}
    )
    node_target: "Node" = Relationship(
        sa_relationship_kwargs={"primaryjoin": "Edge.target==Node.id", "lazy": "joined"}
    )
    scenario: Optional["Scenario"] = Relationship(back_populates="edges")


Index("idx_edge_geom", Edge.__table__.c.geom, postgresql_using="gist")


class WayModified(EdgeBase, table=True):
    __tablename__ = "way_modified"
    __table_args__ = {"schema": "customer"}
    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    way_type: Optional[str] = Field(sa_column=Column(Text))
    edit_type: Optional[str] = Field(sa_column=Column(Text))
    creation_date: Optional[datetime] = Field(
        sa_column=Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    )
    way_id: Optional[int] = Field(index=True, default=None)
    scenario_id: Optional[int] = Field(
        sa_column=Column(
            Integer, ForeignKey("customer.scenario.id", ondelete="CASCADE"), index=True
        )
    )
    outdated: Optional[bool] = Field(sa_column=Column(Boolean, default=False))
    scenario: Optional["Scenario"] = Relationship(back_populates="ways_modified")



Index("idx_way_modified_geom", WayModified.__table__.c.geom, postgresql_using="gist")
