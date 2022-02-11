from typing import TYPE_CHECKING, List, Optional

from sqlmodel import (
    JSON,
    Column,
    Field,
    ForeignKey,
    Integer,
    Relationship,
    SQLModel,
    Text,
    DateTime,
    text
)
from datetime import datetime

if TYPE_CHECKING:
    from .role import Role
    from .user import User



class Customization(SQLModel, table=True):
    __tablename__ = "customization"
    __table_args__ = {"schema": "customer"}

    id: Optional[int] = Field(primary_key=True)
    type: str = Field(sa_column=Column(Text, nullable=False))
    default_setting: dict = Field(sa_column=Column(JSON, nullable=False))
    role_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("customer.role.id", ondelete="CASCADE"), nullable=False
        )
    )

    role: "Role" = Relationship(back_populates="customizations")
    user_customizations: Optional[List["UserCustomization"]] = Relationship(back_populates="customizations")


class UserCustomization(SQLModel, table=True):
    __tablename__ = "user_customization"
    __table_args__ = {"schema": "customer"}

    id: Optional[int] = Field(primary_key=True)
    setting: dict = Field(sa_column=Column(JSON, nullable=False))
    creation_date: Optional[datetime] = Field(
        sa_column=Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    )
    user_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("customer.user.id", ondelete="CASCADE"), nullable=False
        )
    )
    customization_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("customer.customization.id", ondelete="CASCADE"), nullable=False
        )
    )
    customizations: "Customization" = Relationship(back_populates="user_customizations")
    users: "User" = Relationship(back_populates="user_customizations")