from email.policy import default

from sqlalchemy import BigInteger
from sqlmodel import Column, Field, ForeignKey, Integer, SQLModel


class StudyAreaGridVisualization(SQLModel, table=True):
    __tablename__ = "study_area_grid_visualization"
    __table_args__ = {"schema": "basic"}

    id: int = Field(primary_key=True)
    study_area_id: int = Field(
        sa_column=Column(Integer, ForeignKey("basic.study_area.id"), nullable=False, index=True)
    )
    grid_visualization_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("basic.grid_visualization.id"),
            nullable=False,
        )
    )
