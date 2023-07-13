from datetime import datetime
from typing import TYPE_CHECKING, Optional

from geoalchemy2 import Geometry
from sqlmodel import (
    Column,
    DateTime,
    Field,
    ForeignKey,
    Index,
    Integer,
    Relationship,
    SQLModel,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
if TYPE_CHECKING:
    from ..data_upload import DataUpload
    from ..scenario import Scenario


class AoiBase(SQLModel):
    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    category: str = Field(sa_column=Column(Text, index=True, nullable=False))
    name: Optional[str] = Field(sa_column=Column(Text))
    opening_hours: Optional[str] = Field(sa_column=Column(Text))
    wheelchair: Optional[str] = Field(sa_column=Column(Text))
    tags: Optional[dict] = Field(sa_column=Column(JSONB))
    geom: str = Field(
        sa_column=Column(
            Geometry(geometry_type="MultiPolygon", srid="4326", spatial_index=False),
            nullable=False,
        )
    )


class Aoi(AoiBase, table=True):
    __tablename__ = "aoi"
    __table_args__ = {"schema": "basic"}


Index("idx_aoi_geom", Aoi.__table__.c.geom, postgresql_using="gist")


class AoiModified(AoiBase, table=True):
    __tablename__ = "aoi_modified"
    __table_args__ = {"schema": "customer"}

    creation_date: Optional[datetime] = Field(
        sa_column=Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    )
    scenario_id: Optional[int] = Field(
        sa_column=Column(
            Integer, ForeignKey("customer.scenario.id", ondelete="CASCADE"), index=True
        )
    )

    scenario: Optional["Scenario"] = Relationship(back_populates="aois_modified")


Index("idx_aoi_modified_geom", AoiModified.__table__.c.geom, postgresql_using="gist")


class AoiUser(AoiBase, table=True):
    __tablename__ = "aoi_user"
    __table_args__ = {"schema": "customer"}

    creation_date: Optional[datetime] = Field(
        sa_column=Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    )
    data_upload_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("customer.data_upload.id", ondelete="CASCADE"),
            index=True,
            nullable=False,
        )
    )

    data_upload: Optional["DataUpload"] = Relationship(back_populates="aois_user")


Index("idx_aoi_user_geom", AoiUser.__table__.c.geom, postgresql_using="gist")
