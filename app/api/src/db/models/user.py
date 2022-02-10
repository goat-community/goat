from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import (
    JSON,
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
    from .customization import Customization
    from .data_upload import DataUpload
    from .organization import Organization
    from .role import Role
    from .study_area import StudyArea


class UserRole(SQLModel, table=True):
    __tablename__ = "user_role"
    __table_args__ = {"schema": "customer"}

    id: int = Field(primary_key=True)
    user_id: int = Field(default=None, foreign_key="customer.user.id", primary_key=True)
    role_id: int = Field(default=None, foreign_key="customer.role.id", primary_key=True)


class UserStudyArea(SQLModel, table=True):
    __tablename__ = "user_study_area"
    __table_args__ = {"schema": "customer"}

    id: int = Field(primary_key=True)
    creation_date: datetime = Field(
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


class UserCustomization(SQLModel, table=True):
    __tablename__ = "user_customization"
    __table_args__ = {"schema": "customer"}

    id: int = Field(primary_key=True)
    setting: str = Field(sa_column=Column(JSON, nullable=False))
    creation_date: datetime = Field(
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


class User(SQLModel, table=True):
    __tablename__ = "user"
    __table_args__ = {"schema": "customer"}

    id: int = Field(primary_key=True)
    name: str = Field(sa_column=Column(Text, nullable=False))
    surname: str = Field(sa_column=Column(Text, nullable=False))
    email: str = Field(sa_column=Column(Text, nullable=False))
    hashed_password: str = Field(sa_column=Column(Text, nullable=False))
    is_active: Optional[bool] = Field(default=True)
    storage: Optional[int]
    creation_date: datetime = Field(
        sa_column=Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    )
    organization_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("customer.organization.id", ondelete="CASCADE"), nullable=False
        )
    )

    organization: "Organization" = Relationship(back_populates="users")
    roles: List["Role"] = Relationship(back_populates="users", link_model=UserRole)
    study_areas: List["StudyArea"] = Relationship(back_populates="users", link_model=UserStudyArea)
    data_uploads: List["DataUpload"] = Relationship(back_populates="user")
    customizations: List["Customization"] = Relationship(
        back_populates="user", link_model=UserCustomization
    )
