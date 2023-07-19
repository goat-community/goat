from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import (
    ARRAY,
    Column,
    Field,
    ForeignKey,
    Integer,
    Relationship,
    SQLModel,
    Text,
    UniqueConstraint,
)

if TYPE_CHECKING:
    pass


class StyleLibrary(SQLModel, table=True):
    __tablename__ = "style_library"
    __table_args__ = {"schema": "customer"}

    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    name: str = Field(sa_column=Column(Text(), nullable=False, index=True))
    style: dict = Field(sa_column=Column(JSONB))
    translation: Optional[dict] = Field(sa_column=Column(JSONB))
    layer_libraries: "LayerLibrary" = Relationship(back_populates="style_library")


UniqueConstraint(StyleLibrary.__table__.c.name)


class LayerLibraryBase(SQLModel):
    name: str = Field(sa_column=Column(Text(), nullable=False, index=True))
    url: Optional[str] = Field(sa_column=Column(Text))
    legend_urls: Optional[List[str]] = Field(sa_column=Column(ARRAY(Text())))
    special_attribute: Optional[dict] = Field(sa_column=Column(JSONB))
    access_token: Optional[str] = Field(sa_column=Column(Text))
    type: str = Field(sa_column=Column(Text(), nullable=False, index=True))
    map_attribution: Optional[str] = Field(sa_column=Column(Text))
    date: Optional[str] = Field(sa_column=Column(Text))
    source: Optional[str]
    date_1: Optional[str] = Field(sa_column=Column(Text))
    source_1: Optional[str]
    style_library_name: Optional[str]
    max_resolution: Optional[str] = Field(sa_column=Column(Text, nullable=True))
    min_resolution: Optional[str] = Field(sa_column=Column(Text, nullable=True))
    doc_url: Optional[str] = Field(sa_column=Column(Text, nullable=True))


class LayerLibrary(LayerLibraryBase, table=True):
    __tablename__ = "layer_library"
    __table_args__ = {"schema": "customer"}

    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    source: Optional[str] = Field(
        sa_column=Column(
            Text,
            ForeignKey("customer.layer_source.name", onupdate="CASCADE"),
            nullable=True,
        )
    )
    source_1: Optional[str] = Field(
        sa_column=Column(
            Text,
            ForeignKey("customer.layer_source.name", onupdate="CASCADE"),
            nullable=True,
        )
    )
    style_library_name: Optional[str] = Field(
        sa_column=Column(
            Text,
            ForeignKey("customer.style_library.name", onupdate="CASCADE"),
            nullable=True,
        )
    )

    style_library: "StyleLibrary" = Relationship(back_populates="layer_libraries")


UniqueConstraint(LayerLibrary.__table__.c.name)


class LayerSource(SQLModel, table=True):
    __tablename__ = "layer_source"
    __table_args__ = {"schema": "customer"}

    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    name: str = Field(sa_column=Column(Text(), nullable=False, index=True))


UniqueConstraint(LayerSource.__table__.c.name)
