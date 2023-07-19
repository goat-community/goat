from typing import TYPE_CHECKING, Optional

from geoalchemy2 import Geometry
from sqlmodel import (
    BigInteger,
    Column,
    Field,
    ForeignKey,
    Index,
    Integer,
    Relationship,
    SQLModel,
)

if TYPE_CHECKING:
    from .scenario import Scenario


class Node(SQLModel, table=True):
    __tablename__ = "node"
    __table_args__ = {"schema": "basic"}

    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True))
    osm_id: Optional[int] = Field(sa_column=Column(BigInteger()))
    geom: str = Field(
        sa_column=Column(
            Geometry(geometry_type="Point", srid="4326", spatial_index=False),
            nullable=False,
        )
    )
    scenario_id: Optional[int] = Field(
        sa_column=Column(
            Integer, ForeignKey("customer.scenario.id", ondelete="CASCADE"), index=True
        )
    )

    scenario: Optional["Scenario"] = Relationship(back_populates="nodes")

    # TODO: Add edge_source and edge_node here..


Index("idx_node_geom", Node.__table__.c.geom, postgresql_using="gist")
