from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import (
    Column,
    DateTime,
    Field,
    Float,
    ForeignKey,
    Integer,
    Relationship,
    SQLModel,
    Text,
    text,
)

if TYPE_CHECKING:
    from .scenario import Scenario
    from .user import User


class IsochroneCalculation(SQLModel, table=True):
    __tablename__ = "isochrone_calculation"
    __table_args__ = {"schema": "customer"}

    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    calculation_type: str = Field(sa_column=Column(Text, nullable=False))
    starting_point: str = Field(sa_column=Column(Text, nullable=False))
    routing_profile: str = Field(sa_column=Column(Text, nullable=False))
    speed: float = Field(sa_column=Column(Float(53), nullable=False))
    modus: str = Field(sa_column=Column(Text, nullable=False))
    creation_date: Optional[datetime] = Field(
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
        default=None,
        sa_column=Column(
            Integer, ForeignKey("customer.user.id", ondelete="CASCADE"), nullable=False
        ),
    )

    scenario: Optional["Scenario"] = Relationship(back_populates="isochrone_calculations")
    user: "User" = Relationship(back_populates="isochrone_calculations")
