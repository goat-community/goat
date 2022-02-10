from datetime import datetime
from typing import TYPE_CHECKING, Optional

from geoalchemy2 import Geometry
from sqlmodel import (
    JSON,
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
    from .edge import Edge
    from .scenario import Scenario
    from .user import User


class IsochroneCalculation(SQLModel, table=True):
    __tablename__ = "isochrone_calculation"
    __table_args__ = {"schema": "customer"}

    id: int = Field(primary_key=True)
    calculation_type: str = Field(sa_column=Column(Text, nullable=False))
    starting_point: str = Field(sa_column=Column(Text, nullable=False))
    routing_profile: str = Field(sa_column=Column(Text, nullable=False))
    speed: float = Field(sa_column=Column(Float(53), nullable=False))
    modus: str = Field(sa_column=Column(Text, nullable=False))
    creation_date: datetime = Field(
        sa_column=Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    )
    parent_id: Optional[int] = Field(
        sa_column=Column(
            Integer, ForeignKey("customer.isochrone_calculation.id", ondelete="CASCADE")
        )
    )
    scenario_id: Optional[int] = Field(
        sa_column=Column(Integer, ForeignKey("customer.scenario.id", ondelete="CASCADE"))
    )
    user_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("customer.user.id", ondelete="CASCADE"), nullable=False
        )
    )

    scenario: Optional["Scenario"] = Relationship(back_populates="isochrone_calculations")
    user: "User" = Relationship(back_populates="isochrone_calculations")
    isochrone_features: "IsochroneFeature" = Relationship(back_populates="isochrone_calculation")
    isochrone_edges: "IsochroneEdge" = Relationship(back_populates="isochrone_calculation")


class IsochroneFeature(SQLModel, table=True):
    __tablename__ = "isochrone_feature"
    __table_args__ = {"schema": "customer"}

    id: int = Field(primary_key=True)
    step: int = Field(nullable=False)
    reached_opportunities: Optional[str] = Field(sa_column=Column(JSON))
    geom: str = Field(
        sa_column=Column(
            Geometry(geometry_type="MultiPolygon", srid="4326", spatial_index=False),
            nullable=False,
        )
    )
    isochrone_calculation_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("customer.isochrone_calculation.id", ondelete="CASCADE"),
            index=True,
            nullable=False,
        )
    )

    isochrone_calculation: "IsochroneCalculation" = Relationship(
        back_populates="isochrone_features"
    )


Index("idx_isochrone_feature_geom", IsochroneFeature.__table__.c.geom, postgresql_using="gist")


class IsochroneEdge(SQLModel, table=True):
    __tablename__ = "isochrone_edge"
    __table_args__ = {"schema": "customer"}

    id: int = Field(primary_key=True)
    cost: float = Field(sa_column=Column(Float(53), nullable=False))
    start_cost: float = Field(sa_column=Column(Float(53), nullable=False))
    end_cost: float = Field(sa_column=Column(Float(53), nullable=False))
    start_perc: float = Field(sa_column=Column(Float(53)))
    end_perc: float = Field(sa_column=Column(Float(53)))
    partial_edge: Optional[bool]
    geom: str = Field(
        sa_column=Column(Geometry(geometry_type="Linestring", srid="4326", spatial_index=False))
    )
    edge_id: Optional[int] = Field(foreign_key="basic.edge.id")
    isochrone_calculation_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("customer.isochrone_calculation.id", ondelete="CASCADE"),
            index=True,
            nullable=False,
        )
    )

    edge: Optional["Edge"] = Relationship(back_populates="isochrone_edges")
    isochrone_calculation: "IsochroneCalculation" = Relationship(back_populates="isochrone_edges")
