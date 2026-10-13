from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, ForeignKey, Text, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as UUID_PG
from sqlmodel import Column, Field, SQLModel

from core.core.config import settings


class LayerSerialCounter(SQLModel, table=True):
    """The highest number a layer's serial column has ever handed out.

    A serial column's next value is one past the larger of this mark and the
    highest number still in the layer, so a number is never handed out twice —
    not even after the feature that held the highest one is deleted, which a
    plain ``max + 1`` would reuse.

    Written by geoapi only, in the same transaction that holds the layer's
    advisory write lock, after the rows have been inserted. Kept here rather
    than in ``field_config`` so a counter that moves on every create does not
    rewrite the column definitions each time, and so it goes away with its
    layer: the foreign key cascades when the layer is purged. A soft-deleted
    layer keeps its counter, because it can be restored.

    A copy of a layer starts without a row and continues from the highest
    number it holds; the column endpoints drop the row when a column is
    dropped or added, and move it when a column is renamed.
    """

    __tablename__ = "layer_serial_counter"
    __table_args__ = {"schema": settings.SCHEMA}

    layer_id: UUID = Field(
        sa_column=Column(
            UUID_PG(as_uuid=True),
            ForeignKey(f"{settings.SCHEMA}.layer.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        )
    )
    field_name: str = Field(sa_column=Column(Text, primary_key=True, nullable=False))
    last_value: int = Field(sa_column=Column(BigInteger, nullable=False))
    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
        ),
    )
