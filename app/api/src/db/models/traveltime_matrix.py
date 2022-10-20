from typing import TYPE_CHECKING, List, Optional
from numpy import byte
from sqlalchemy import LargeBinary, SmallInteger

from sqlmodel import (
    Column,
    Field,
    Float,
    ForeignKey,
    Integer,
    SQLModel,
    BigInteger,
    BINARY,
    Relationship,
    ARRAY
)

if TYPE_CHECKING:
    from .population import Population, PopulationModified
    from .scenario import Scenario
    from .grid import GridCalculation



class TravelTimeMatrixBase(SQLModel):
    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    grid_calculation_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("basic.grid_calculation.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
            unique=True,
        )
    )
    northwest: Optional[List[int]] = Field(sa_column=Column(ARRAY(Integer())), nullable=False)
    heigth: Optional[int] = Field(sa_column=Column(SmallInteger), nullable=False)
    width: Optional[int] = Field(sa_column=Column(SmallInteger), nullable=False)
    costs: Optional[bytes] = Field(sa_column=Column(LargeBinary), nullable=False)


class TravelTimeMatrixWalking(TravelTimeMatrixBase, table=True):
    __tablename__ = "traveltime_matrix_walking"
    __table_args__ = {"schema": "customer"}


    grid_calculation: "GridCalculation" = Relationship(back_populates="traveltime_matrix_walking")
