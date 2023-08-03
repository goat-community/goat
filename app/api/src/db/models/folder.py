from typing import List
from uuid import UUID
from src.db.models._base_class import DateTimeBase
from sqlmodel import (
    Column,
    Field,
    Relationship,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as UUID_PG
from sqlalchemy import ForeignKey
from src.db.models.user import User

class Folder(DateTimeBase, table=True):
    __tablename__ = "folder"
    __table_args__ = {"schema": "customer"}

    id: UUID | None = Field(
        sa_column=Column(
            UUID_PG(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=text("uuid_generate_v4()"),
        )
    )
    user_id: UUID = Field(
        sa_column=Column(
            UUID_PG(as_uuid=True),
            ForeignKey("customer.user.id", ondelete="CASCADE"),
            nullable=False,
        ),
        description="Folder owner ID",
    )
    name: str = Field(sa_column=Column(Text, nullable=False), description="Folder name")

    # Relationships
    user: "User" = Relationship(back_populates="folders")
