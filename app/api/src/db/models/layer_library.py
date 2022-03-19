from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import (
    Column,
    Field,
    ForeignKey,
    Integer,
    SQLModel,
    Text
)
from sqlalchemy.dialects.postgresql import JSONB
if TYPE_CHECKING:
    from .data_upload import DataUpload
    from .scenario import Scenario


class LayerLibrary(SQLModel, table=True):
    __tablename__ = "layer_library"
    __table_args__ = {"schema": "customer"}

    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    name: str = Field(sa_column=Column(Text(), nullable=False, index=True))
    url: Optional[str] = Field(sa_column=Column(Text))
    access_token: Optional[str] = Field(sa_column=Column(Text))
    type: str = Field(sa_column=Column(Text(), nullable=False, index=True))
    map_attribution: Optional[str] = Field(sa_column=Column(Text))
    attributes: Optional[dict] = Field(sa_column=Column(JSONB))
    style_library_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("customer.style_library.id"),
            nullable=True,
        )
    )
    
class StyleLibrary(SQLModel, table=True):
    __tablename__ = "style_library"
    __table_args__ = {"schema": "customer"}

    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    name: str = Field(sa_column=Column(Text(), nullable=False, index=True))
    style: dict = Field(sa_column=Column(JSONB))
    translations: dict = Field(sa_column=Column(JSONB))
