from datetime import datetime
from typing import TYPE_CHECKING, List

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
    from .aoi import AoiUser
    from .poi import PoiUser
    from .user import User


class DataUpload(SQLModel, table=True):

    __tablename__ = "data_upload"
    __table_args__ = {"schema": "customer"}

    id: int = Field(primary_key=True)
    data_type: str = Field(sa_column=Column(Text, nullable=False))
    upload_type: str = Field(sa_column=Column(Text, nullable=False))
    upload_grid_ids: List[str] = Field(
        sa_column=Column(ARRAY(Text()), nullable=False, server_default=text("'{}'::text[]"))
    )
    upload_size: int = Field(nullable=False)
    creation_date: datetime = Field(
        sa_column=Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    )
    user_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("customer.user.id", ondelete="CASCADE"), nullable=False
        )
    )

    user: "User" = Relationship(back_populates="data_uploads")
    pois_user: List["PoiUser"] = Relationship(back_populates="data_upload")
    aois_user: List["AoiUser"] = Relationship(back_populates="data_upload")
