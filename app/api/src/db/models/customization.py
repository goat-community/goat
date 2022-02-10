from typing import TYPE_CHECKING, Optional

from sqlmodel import (
    JSON,
    Column,
    Field,
    ForeignKey,
    Integer,
    Relationship,
    SQLModel,
    Text,
)

if TYPE_CHECKING:
    from .role import Role


class Customization(SQLModel, table=True):
    __tablename__ = "customization"
    __table_args__ = {"schema": "customer"}

    id: int = Field(primary_key=True)
    type: str = Field(sa_column=Column(Text, nullable=False))
    default_setting: str = Field(sa_column=Column(JSON, nullable=False))
    role_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("customer.role.id", ondelete="CASCADE"), nullable=False
        )
    )

    role: "Role" = Relationship(back_populates="customizations")
