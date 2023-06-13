from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import (
    Column,
    DateTime,
    Field,
    ForeignKey,
    Integer,
    Relationship,
    SQLModel,
    Text,
    text,
)

if TYPE_CHECKING:
    from .role import Role
    from .study_area import StudyArea
    from .user import User


class CustomizationBase(SQLModel):
    type: str
    setting: dict
    role_id: int


class Customization(CustomizationBase, table=True):
    __tablename__ = "customization"
    __table_args__ = {"schema": "customer"}

    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    type: str = Field(sa_column=Column(Text, nullable=False))
    setting: dict = Field(sa_column=Column(JSONB, nullable=False))
    role_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("customer.role.id", ondelete="CASCADE"), nullable=False
        )
    )
    role: "Role" = Relationship(back_populates="customizations")
    user_customizations: Optional[List["UserCustomization"]] = Relationship(
        back_populates="customizations"
    )


class UserCustomization(SQLModel, table=True):
    __tablename__ = "user_customization"
    __table_args__ = {"schema": "customer"}

    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    setting: dict = Field(sa_column=Column(JSONB, nullable=False))
    creation_date: Optional[datetime] = Field(
        sa_column=Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    )
    user_id: int = Field(
        default=None,
        sa_column=Column(
            Integer, ForeignKey("customer.user.id", ondelete="CASCADE"), nullable=False
        ),
    )
    customization_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("customer.customization.id", ondelete="CASCADE"), nullable=False
        )
    )
    study_area_id: int = Field(
        sa_column=Column(Integer, ForeignKey("basic.study_area.id"), nullable=False)
    )
    customizations: "Customization" = Relationship(back_populates="user_customizations")
    users: "User" = Relationship(back_populates="user_customizations")
    study_areas: "StudyArea" = Relationship(back_populates="user_customizations")
