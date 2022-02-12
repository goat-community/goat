from typing import TYPE_CHECKING, List, Optional

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
)

if TYPE_CHECKING:
    from .edge import Edge
    from .grid import GridCalculation
    from .poi import Poi
    from .scenario import Scenario


class ReachedEdgeHeatmap(SQLModel, table=True):
    __tablename__ = "reached_edge_heatmap"
    __table_args__ = {"schema": "basic"}

    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    start_perc: float = Field(sa_column=Column(Float(53), nullable=False))
    end_perc: float = Field(sa_column=Column(Float(53), nullable=False))
    partial_edge: bool = Field(nullable=False)
    geom: str = Field(
        sa_column=Column(
            Geometry(geometry_type="Linestring", srid="4326", spatial_index=False),
            nullable=False,
        )
    )
    edge_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("basic.edge.id", ondelete="CASCADE"), index=True, nullable=False
        ),
    )
    edge: "Edge" = Relationship(back_populates="reached_edge_heatmaps")
    scenario_id: Optional[int] = Field(
        sa_column=Column(
            Integer, ForeignKey("customer.scenario.id", ondelete="CASCADE"), index=True
        ),
    )
    scenario: Optional["Scenario"] = Relationship(back_populates="reached_edge_heatmaps")
    reached_edge_heatmap_grid_calculations: List[
        "ReachedEdgeHeatmapGridCalculation"
    ] = Relationship(back_populates="reached_edge_heatmap")


Index(
    "idx_reached_edge_heatmap_geom", ReachedEdgeHeatmap.__table__.c.geom, postgresql_using="gist"
)


class ReachedEdgeHeatmapGridCalculation(SQLModel, table=True):
    __tablename__ = "reached_edge_heatmap_grid_calculation"
    __table_args__ = {"schema": "basic"}

    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True, autoincrement=True))
    start_cost: int = Field(sa_column=Column(SmallInteger, nullable=False))
    end_cost: int = Field(sa_column=Column(SmallInteger, nullable=False))
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
            ForeignKey("basic.reached_edge_heatmap.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )

    grid_calculation: "GridCalculation" = Relationship(
        back_populates="reached_edge_heatmap_grid_calculations"
    )
    reached_edge_heatmap: ReachedEdgeHeatmap = Relationship(
        back_populates="reached_edge_heatmap_grid_calculations"
    )


class ReachedPoiHeatmap(SQLModel, table=True):
    __tablename__ = "reached_poi_heatmap"
    __table_args__ = {"schema": "basic"}

    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    cost: int = Field(nullable=False)
    grid_calculation_id = Column(
        ForeignKey("basic.grid_calculation.id", ondelete="CASCADE"), nullable=False
    )
    grid_calculation_id: int = Field(
        sa_column=Column(
            BigInteger(),
            ForeignKey("basic.grid_calculation.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    grid_calculation: "GridCalculation" = Relationship(back_populates="reached_poi_heatmaps")
    poi_id: int = Field(
        sa_column=Column(Integer, ForeignKey("basic.poi.id", ondelete="CASCADE"), nullable=False)
    )
    scenario_id: Optional[int] = Field(
        sa_column=Column(
            Integer, ForeignKey("customer.scenario.id", ondelete="CASCADE"), index=True
        ),
    )

    poi: "Poi" = Relationship(back_populates="reached_poi_heatmaps")
    reached_poi_heatmap_accessibilities: List["ReachedPoiHeatmapAccessibility"] = Relationship(
        back_populates="reached_poi_heatmap"
    )
    scenario: Optional["Scenario"] = Relationship(back_populates="reached_poi_heatmaps")


class ReachedPoiHeatmapAccessibility(SQLModel, table=True):
    __tablename__ = "reached_poi_heatmap_accessibility"
    __table_args__ = {"schema": "basic"}

    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    sensitivity: int = Field(nullable=False)
    accessibility_index: int = Field(nullable=False)
    reached_poi_heatmap_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("basic.reached_poi_heatmap.id", ondelete="CASCADE"), nullable=False
        )
    )

    reached_poi_heatmap: ReachedPoiHeatmap = Relationship(
        back_populates="reached_poi_heatmap_accessibilities"
    )
