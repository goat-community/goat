from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

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
    from .customization import Customization, UserCustomization
    from .data_upload import DataUpload
    from .isochrone import IsochroneCalculation
    from .organization import Organization
    from .role import Role
    from .scenario import Scenario
    from .study_area import StudyArea

from ._link_model import UserRole, UserStudyArea


class User(SQLModel, table=True):
    __tablename__ = "user"
    __table_args__ = {"schema": "customer"}

    id: Optional[int] = Field(primary_key=True)
    name: str = Field(sa_column=Column(Text, nullable=False))
    surname: str = Field(sa_column=Column(Text, nullable=False))
    email: str = Field(sa_column=Column(Text, nullable=False))
    hashed_password: str = Field(sa_column=Column(Text, nullable=False))
    is_active: Optional[bool] = Field(default=True)
    storage: Optional[int]
    creation_date: Optional[datetime] = Field(
        sa_column=Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    )
    organization_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("customer.organization.id", ondelete="CASCADE"), nullable=False
        )
    )

    organization: "Organization" = Relationship(back_populates="users")
    roles: List["Role"] = Relationship(back_populates="users", link_model=UserRole)
    scenarios: List["Scenario"] = Relationship(back_populates="user")
    study_areas: List["StudyArea"] = Relationship(back_populates="users", link_model=UserStudyArea)
    data_uploads: List["DataUpload"] = Relationship(back_populates="user")
    isochrone_calculations: List["IsochroneCalculation"] = Relationship(back_populates="user")

    user_customizations: List["UserCustomization"] = Relationship(back_populates="users")
