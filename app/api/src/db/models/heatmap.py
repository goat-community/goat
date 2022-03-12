from cgitb import text
from typing import TYPE_CHECKING, List, Optional
from xmlrpc.client import Boolean

from geoalchemy2 import Geometry
from sqlmodel import (
    BigInteger,
    Column,
    Field,
    Float,
    ForeignKey,
    Index,
    Integer,
    Relationship,
    SmallInteger,
    SQLModel,
    String,
    Text,
    ARRAY
)

if TYPE_CHECKING:
    from .edge import Edge
    from .grid import GridVisualization
    from .poi import Poi
    from .scenario import Scenario


class ReachedEdgeFullHeatmap(SQLModel, table=True):
    __tablename__ = "reached_edge_full_heatmap"
    __table_args__ = {"schema": "customer"}

    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    geom: str = Field(
        sa_column=Column(
            Geometry(geometry_type="Linestring", srid="4326", spatial_index=False),
            nullable=False,
        )
    )
    edge_id: int = Field(
        sa_column=Column(
            Integer, index=True, nullable=False
        ),
    )
    scenario_id: Optional[int] = Field(
        sa_column=Column(
            Integer, ForeignKey("customer.scenario.id", ondelete="CASCADE"), index=True
        ),
    )
Index(
    "idx_reached_edge_full_heatmap_geom", ReachedEdgeFullHeatmap.__table__.c.geom, postgresql_using="gist"
)

class ReachedEdgeHeatmapGridCalculation(SQLModel, table=True):
    __tablename__ = "reached_edge_heatmap_grid_calculation"
    __table_args__ = {"schema": "customer"}

    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True, autoincrement=True))
    start_cost: int = Field(sa_column=Column(SmallInteger, nullable=False))
    end_cost: int = Field(sa_column=Column(SmallInteger, nullable=False))
    start_perc: int = Field(sa_column=Column(SmallInteger, nullable=True))
    end_perc: int = Field(sa_column=Column(SmallInteger, nullable=True))
    grid_calculation_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("basic.grid_calculation.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    reached_edge_heatmap_id: int = Field(
        sa_column=Column(
            Integer,
            nullable=False,
            index=True,
        )
    )
    edge_type: str = Field(sa_column=Column(String(2)))


class ReachedPoiHeatmap(SQLModel, table=True):
    __tablename__ = "reached_poi_heatmap"
    __table_args__ = {"schema": "customer"}

    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    costs: int = Field(
        sa_column=Column(ARRAY(Integer()), nullable=False)
    )
    grid_visualization_ids: int = Field(
        sa_column=Column(
            ARRAY(BigInteger()),
            nullable=False,
        ),
    )
    poi_uid: str = Field(
        sa_column=Column(Text, nullable=False), index=True
    )
    scenario_id: Optional[int] = Field(
        sa_column=Column(
            Integer, ForeignKey("customer.scenario.id", ondelete="CASCADE"), index=True
        ),
    )
    data_upload_id: Optional[int] = Field(
        sa_column=Column(
            Integer, ForeignKey("customer.data_upload.id", ondelete="CASCADE"), index=True
        ),
    )
    accessibility_indices: list = Field(
        sa_column=Column(ARRAY(Integer()), nullable=False)
    )