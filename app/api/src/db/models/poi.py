from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from geoalchemy2 import Geometry
from sqlmodel import (
    JSON,
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
)

if TYPE_CHECKING:
    from .data_upload import DataUpload
    from .heatmap import ReachedPoiHeatmap
    from .scenario import Scenario


class PoiBase(SQLModel):
    id: int = Field(primary_key=True)
    category: str = Field(sa_column=Column(Text(), nullable=False, index=True))
    name: Optional[str] = Field(sa_column=Column(Text))
    street: Optional[str] = Field(sa_column=Column(Text))
    housenumber: Optional[str] = Field(sa_column=Column(Text))
    zipcode: Optional[str] = Field(sa_column=Column(Text))
    opening_hours: Optional[str] = Field(sa_column=Column(Text))
    wheelchair: Optional[str] = Field(sa_column=Column(Text))
    tags: Optional[str] = Field(sa_column=Column(JSON))
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

    reached_poi_heatmaps: List["ReachedPoiHeatmap"] = Relationship(back_populates="poi")


Index("idx_poi_geom", Poi.__table__.c.geom, postgresql_using="gist")
UniqueConstraint(Poi.__table__.c.uid)


class PoiModified(PoiBase, table=True):
    __tablename__ = "poi_modified"
    __table_args__ = {"schema": "customer"}
    uid: str = Field(sa_column=Column(Text, nullable=False, index=True))
    edit_type: str = Field(sa_column=Column(Text, nullable=False, index=True))
    table_name: str = Field(sa_column=Column(Text, nullable=False, index=True))
    creation_date: datetime = Field(
        sa_column=Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    )
    scenario_id: Optional[int] = Field(
        sa_column=Column(
            Integer, ForeignKey("customer.scenario.id", ondelete="CASCADE"), index=True
        ),
    )

    scenario: Optional["Scenario"] = Relationship(back_populates="pois_modified")


Index("idx_poi_modified_geom", PoiModified.__table__.c.geom, postgresql_using="gist")


class PoiUser(PoiBase, table=True):
    __tablename__ = "poi_user"
    __table_args__ = {"schema": "customer"}

    uid: str = Field(sa_column=Column(Text, nullable=False, index=True))
    creation_date: datetime = Field(
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
