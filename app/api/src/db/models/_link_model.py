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

class UserRole(SQLModel, table=True):
    __tablename__ = "user_role"
    __table_args__ = {"schema": "customer"}

    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    user_id: Optional[int] = Field(
        sa_column=Column(Integer, ForeignKey("customer.user.id", ondelete="CASCADE"), nullable=False, index=True)
    )
    role_id: Optional[int] = Field(
        sa_column=Column(Integer, ForeignKey("customer.role.id", ondelete="CASCADE"), nullable=False, index=True)
    )

class UserStudyArea(SQLModel, table=True):
    __tablename__ = "user_study_area"
    __table_args__ = {"schema": "customer"}

    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
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

class StudyAreaGeostore(SQLModel, table=True):
    __tablename__ = "study_area_geostore"
    __table_args__ = {"schema": "customer"}

    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    study_area_id: int = Field(
        sa_column=Column(Integer, ForeignKey("basic.study_area.id", ondelete="CASCADE"), nullable=False, index=True)
    )
    geostore_id: int = Field(
        sa_column=Column(Integer, ForeignKey("customer.geostore.id", ondelete="CASCADE"), nullable=False, index=True)
    )