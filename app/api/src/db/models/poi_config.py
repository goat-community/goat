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
    Boolean
)

if TYPE_CHECKING:
    from .user import User
    from .study_area import StudyArea

class PoiGroup(SQLModel, table=True):
    __tablename__ = "poi_group"
    __table_args__ = {"schema": "basic"}

    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    group: str = Field(sa_column=Column(Text, nullable=False))

UniqueConstraint(PoiGroup.__table__.c.group)

class PoiConfigBase(SQLModel):
    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    category: str = Field(sa_column=Column(Text, nullable=False))
    group: str = Field(sa_column=Column(Text,  ForeignKey("basic.poi_group.group"), nullable=False))
    icon: str = Field(sa_column=Column(Text, nullable=False))
    color: List[str] = Field(
        sa_column=Column(ARRAY(Text()), nullable=False)
    )
    sensitivity: int = Field(sa_column=Column(Integer))

class PoiDefaultConfig(PoiConfigBase, table=True):
    __tablename__ = "poi_default_config"
    __table_args__ = {"schema": "basic"}

class PoiStudyAreaConfig(PoiConfigBase, table=True):
    __tablename__ = "poi_study_area_config"
    __table_args__ = {"schema": "basic"}

    study_area_id: int = Field(sa_column=Column(Integer, ForeignKey("basic.study_area.id"), nullable=False))
    is_active: bool = Field(sa_column=Column(Boolean, nullable=False))
    study_area: "StudyArea" = Relationship(back_populates="poi_study_area_configs")


class PoiUserConfig(PoiConfigBase, table=True):
    __tablename__ = "poi_user_config"
    __table_args__ = {"schema": "customer"}

    study_area_id: int = Field(sa_column=Column(Integer, ForeignKey("basic.study_area.id")))
    user_id: int = Field(sa_column=Column(Integer, ForeignKey("customer.user.id")))
    data_upload_id: int = Field(sa_column=Column(Integer, ForeignKey("customer.data_upload.id")))

    study_area: "StudyArea" = Relationship(back_populates="poi_user_configs")
    user: "User" = Relationship(back_populates="poi_user_configs")