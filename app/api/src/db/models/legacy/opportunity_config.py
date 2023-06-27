from typing import TYPE_CHECKING, List, Optional

from sqlmodel import (
    Column,
    Field,
    ForeignKey,
    Integer,
    Relationship,
    SQLModel,
    Text,
    ARRAY,
    UniqueConstraint,
    Boolean,
)

if TYPE_CHECKING:
    from .user import User
    from .study_area import StudyArea


class OpportunityGroup(SQLModel, table=True):
    __tablename__ = "opportunity_group"
    __table_args__ = {"schema": "basic"}

    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    type: str = Field(sa_column=Column(Text, nullable=False))
    group: str = Field(sa_column=Column(Text, nullable=False))
    icon: str = Field(sa_column=Column(Text, nullable=False))
    color: List[str] = Field(sa_column=Column(ARRAY(Text()), nullable=False))

    opportunity_default_configs: Optional[List["OpportunityDefaultConfig"]] = Relationship(
        back_populates="opportunity_group"
    )
    opportunity_study_area_configs: Optional[List["OpportunityStudyAreaConfig"]] = Relationship(
        back_populates="opportunity_group"
    )
    opportunity_user_configs: Optional[List["OpportunityUserConfig"]] = Relationship(
        back_populates="opportunity_group"
    )

UniqueConstraint(OpportunityGroup.__table__.c.group)


class OpportunityConfigBase(SQLModel):
    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    category: str = Field(sa_column=Column(Text, nullable=False))
    icon: str = Field(sa_column=Column(Text, nullable=False))
    color: List[str] = Field(sa_column=Column(ARRAY(Text()), nullable=False))
    sensitivity: Optional[int] = Field(sa_column=Column(Integer))
    multiple_entrance: Optional[bool] = Field(sa_column=Column(Boolean))


class OpportunityDefaultConfig(OpportunityConfigBase, table=True):
    __tablename__ = "opportunity_default_config"
    __table_args__ = {"schema": "basic"}

    opportunity_group_id: Optional[int] = Field(
        sa_column=Column(Integer, ForeignKey("basic.opportunity_group.id"), nullable=False)
    )
    opportunity_group: "OpportunityGroup" = Relationship(
        back_populates="opportunity_default_configs"
    )


UniqueConstraint(OpportunityDefaultConfig.__table__.c.category)


class OpportunityStudyAreaConfig(OpportunityConfigBase, table=True):
    __tablename__ = "opportunity_study_area_config"
    __table_args__ = {"schema": "basic"}

    opportunity_group_id: Optional[int] = Field(
        sa_column=Column(Integer, ForeignKey("basic.opportunity_group.id"), nullable=False)
    )
    study_area_id: int = Field(
        sa_column=Column(Integer, ForeignKey("basic.study_area.id"), nullable=False)
    )
    is_active: bool = Field(sa_column=Column(Boolean, nullable=False))
    study_area: "StudyArea" = Relationship(back_populates="opportunity_study_area_configs")

    opportunity_group: "OpportunityGroup" = Relationship(
        back_populates="opportunity_study_area_configs"
    )


UniqueConstraint(
    OpportunityStudyAreaConfig.__table__.c.category,
    OpportunityStudyAreaConfig.__table__.c.study_area_id,
)


class OpportunityUserConfig(OpportunityConfigBase, table=True):
    __tablename__ = "opportunity_user_config"
    __table_args__ = {"schema": "customer"}

    opportunity_group_id: Optional[int] = Field(
        sa_column=Column(Integer, ForeignKey("basic.opportunity_group.id"), nullable=False)
    )
    study_area_id: int = Field(sa_column=Column(Integer, ForeignKey("basic.study_area.id")))
    user_id: int = Field(
        default=None,
        sa_column=Column(Integer, ForeignKey("customer.user.id", ondelete="CASCADE"))
    )
    data_upload_id: Optional[int] = Field(
        sa_column=Column(Integer, ForeignKey("customer.data_upload.id", ondelete="CASCADE"))
    )

    study_area: "StudyArea" = Relationship(back_populates="opportunity_user_configs")
    user: "User" = Relationship(back_populates="opportunity_user_configs")

    opportunity_group: "OpportunityGroup" = Relationship(back_populates="opportunity_user_configs")


UniqueConstraint(
    OpportunityUserConfig.__table__.c.category,
    OpportunityUserConfig.__table__.c.study_area_id,
    OpportunityUserConfig.__table__.c.user_id,
)
