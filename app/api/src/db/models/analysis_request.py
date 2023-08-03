from typing import TYPE_CHECKING, Union
from uuid import UUID

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, Field, ForeignKey, Relationship, SQLModel, Text, text
from sqlalchemy.dialects.postgresql import UUID as UUID_PG

from ._base_class import DateTimeBase

if TYPE_CHECKING:
    from src.schemas.layer import AnalysisType, IndicatorType
    from .layer import Layer


class AnalysisRequestBase(SQLModel):
    """Base model for analysis requests."""

    type: Union["IndicatorType", "AnalysisType"] = Field(
        sa_column=Column(Text, nullable=False), description="Type of the analysis request"
    )
    layer_id: UUID = Field(
        sa_column=Column(
            UUID_PG(as_uuid=True),
            ForeignKey("customer.layer.id", ondelete="CASCADE"),
            index=True,
        ),
        description="Layer ID",
    )
    url: str = Field(
        sa_column=Column(Text, nullable=False), description="URL of the requested service"
    )
    payload: dict = Field(
        sa_column=Column(JSONB, nullable=False), description="Payload of the request"
    )


class AnalysisRequest(AnalysisRequestBase, DateTimeBase, table=True):
    """Analysis Request model."""

    __tablename__ = "analysis_request"
    __table_args__ = {"schema": "customer"}

    id: UUID | None = Field(
        sa_column=Column(
            UUID_PG(as_uuid=True), primary_key=True, nullable=False, server_default=text("uuid_generate_v4()")
        )
    )
    layer_id: UUID = Field(
        sa_column=Column(
            UUID_PG(as_uuid=True),
            ForeignKey("customer.layer.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        description="Layer ID",
    )
    # Relationships
    layer: "Layer" = Relationship(back_populates="analysis_requests")
