from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import EmailStr
from sqlmodel import (
    ARRAY,
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
    from .opportunity_config import OpportunityUserConfig
    from .static_layer import StaticLayer

from ._link_model import UserRole, UserStudyArea


class UserBase(SQLModel):
    name: str = Field(sa_column=Column(Text, nullable=False))
    surname: str = Field(sa_column=Column(Text, nullable=False))
    email: EmailStr = Field(sa_column=Column(Text, nullable=False))

    organization_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("customer.organization.id", ondelete="CASCADE"), nullable=False
        )
    )
    active_study_area_id: int = Field(
        sa_column=Column(Integer, ForeignKey("basic.study_area.id"), nullable=False)
    )
    active_data_upload_ids: List[int] = Field(
        sa_column=Column(ARRAY(Integer()), server_default=text("'{}'::int[]"))
    )
    storage: int = Field(sa_column=Column(Integer), nullable=False)
    limit_scenarios: int = Field(sa_column=Column(Integer), nullable=False)


class User(UserBase, table=True):
    __tablename__ = "user"
    __table_args__ = {"schema": "customer"}

    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    hashed_password: Optional[str] = Field(sa_column=Column(Text, nullable=False))
    is_active: Optional[bool] = Field(default=False)
    newsletter: Optional[bool] = Field(default=False)
    occupation: Optional[str] = Field(sa_column=Column(Text, nullable=True))
    domain: Optional[str] = Field(sa_column=Column(Text, nullable=True))
    creation_date: Optional[datetime] = Field(
        sa_column=Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    )
    organization_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("customer.organization.id", ondelete="CASCADE"), nullable=False
        )
    )
    active_study_area_id: int = Field(
        sa_column=Column(Integer, ForeignKey("basic.study_area.id"), nullable=False)
    )
    language_preference: str = Field(sa_column=Column(Text, nullable=False))

    organization: "Organization" = Relationship(back_populates="users")
    roles: List["Role"] = Relationship(back_populates="users", link_model=UserRole)
    scenarios: List["Scenario"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all,delete,delete-orphan"}
    )
    study_areas: List["StudyArea"] = Relationship(back_populates="users", link_model=UserStudyArea)
    data_uploads: List["DataUpload"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all,delete,delete-orphan"}
    )
    isochrone_calculations: List["IsochroneCalculation"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all,delete,delete-orphan"}
    )
    user_customizations: List["UserCustomization"] = Relationship(
        back_populates="users", sa_relationship_kwargs={"cascade": "all,delete,delete-orphan"}
    )
    opportunity_user_configs: List["OpportunityUserConfig"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all,delete,delete-orphan"}
    )
    static_layers: List["StaticLayer"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all,delete,delete-orphan"}
    )
    # active_study_area: "StudyArea" = Relationship(back_populates="users_active")

    class Config:
        search_fields = ["name", "email", "surname"]
