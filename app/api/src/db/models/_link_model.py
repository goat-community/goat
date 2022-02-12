from datetime import datetime
from typing import Optional

from sqlmodel import (
    BigInteger,
    Column,
    DateTime,
    Field,
    ForeignKey,
    Integer,
    SQLModel,
    text,
)


class StudyAreaGridVisualization(SQLModel, table=True):
    __tablename__ = "study_area_grid_visualization"
    __table_args__ = {"schema": "basic"}

    id: Optional[int] = Field(primary_key=True)
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


class UserRole(SQLModel, table=True):
    __tablename__ = "user_role"
    __table_args__ = {"schema": "customer"}

    id: Optional[int] = Field(primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="customer.user.id", primary_key=True)
    role_id: Optional[int] = Field(default=None, foreign_key="customer.role.id", primary_key=True)


class UserStudyArea(SQLModel, table=True):
    __tablename__ = "user_study_area"
    __table_args__ = {"schema": "customer"}

    id: Optional[int] = Field(primary_key=True)
    creation_date: Optional[datetime] = Field(
        sa_column=Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    )
    user_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("customer.user.id", ondelete="CASCADE"), nullable=False
        ),
    )
    study_area_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("basic.study_area.id", ondelete="CASCADE"), nullable=False
        )
    )
