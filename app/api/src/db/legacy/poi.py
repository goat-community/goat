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
    UniqueConstraint,
    text,
    Boolean
)
from sqlalchemy.dialects.postgresql import JSONB
if TYPE_CHECKING:
    from .data_upload import DataUpload
    from .scenario import Scenario


class PoiBase(SQLModel):
    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    category: str = Field(sa_column=Column(Text(), nullable=False, index=True))
    name: Optional[str] = Field(sa_column=Column(Text))
    street: Optional[str] = Field(sa_column=Column(Text))
    housenumber: Optional[str] = Field(sa_column=Column(Text))
    zipcode: Optional[str] = Field(sa_column=Column(Text))
    opening_hours: Optional[str] = Field(sa_column=Column(Text))
    wheelchair: Optional[str] = Field(sa_column=Column(Text))
    tags: Optional[dict] = Field(sa_column=Column(JSONB))
    geom: str = Field(
        sa_column=Column(
            Geometry(geometry_type="Point", srid="4326", spatial_index=False),
            nullable=False,
        )
    )


class Poi(PoiBase, table=True):
    __tablename__ = "poi"
    __table_args__ = {"schema": "basic"}

    uid: str = Field(sa_column=Column(Text, nullable=False, index=True))

Index("idx_poi_geom", Poi.__table__.c.geom, postgresql_using="gist")
UniqueConstraint(Poi.__table__.c.uid)


class PoiModified(PoiBase, table=True):
    __tablename__ = "poi_modified"
    __table_args__ = {"schema": "customer"}
    uid: str = Field(sa_column=Column(Text, nullable=False, index=True))
    edit_type: str = Field(sa_column=Column(Text, nullable=False, index=True))
    creation_date: Optional[datetime] = Field(
        sa_column=Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    )
    scenario_id: Optional[int] = Field(
        sa_column=Column(
            Integer, ForeignKey("customer.scenario.id", ondelete="CASCADE"), nullable=False, index=True
        ),
    )
    data_upload_id: Optional[int] = Field(
        sa_column=Column(
            Integer, ForeignKey("customer.data_upload.id", ondelete="CASCADE"), index=True
        ),
    )
    outdated: Optional[bool] = Field(sa_column=Column(Boolean, default=False))
    scenario: Optional["Scenario"] = Relationship(back_populates="pois_modified")


Index("idx_poi_modified_geom", PoiModified.__table__.c.geom, postgresql_using="gist")


class PoiUser(PoiBase, table=True):
    __tablename__ = "poi_user"
    __table_args__ = {"schema": "customer"}

    uid: str = Field(sa_column=Column(Text, nullable=False, index=True))
    creation_date: Optional[datetime] = Field(
        sa_column=Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    )
    data_upload_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("customer.data_upload.id", ondelete="CASCADE"),
            index=True,
            nullable=False,
        ),
    )

    data_upload: Optional["DataUpload"] = Relationship(back_populates="pois_user")


Index("idx_poi_user_geom", PoiUser.__table__.c.geom, postgresql_using="gist")
