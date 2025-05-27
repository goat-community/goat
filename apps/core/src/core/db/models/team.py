from typing import TYPE_CHECKING, List
from sqlmodel import Field, Text, Relationship
from core.db.models._base_class import DateTimeBase
from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import UUID as UUID_PG
from uuid import UUID
from core.core.config import settings

if TYPE_CHECKING:
    from ._link_model import LayerTeamLink, ProjectTeamLink, UserTeamLink

class Team(DateTimeBase, table=True):
    """
    A stub representation of the Layer model from another repository.
    """

    __tablename__ = "team"
    __table_args__ = {"schema": settings.ACCOUNTS_SCHEMA}

    id: UUID | None = Field(
        sa_column=Column(
            UUID_PG(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=text("uuid_generate_v4()"),
        ),
        description="Team ID",
    )
    name: str = Field(
        sa_column=Column(Text, nullable=False), description="Team name", max_length=255
    )
    avatar: str | None = Field(sa_column=Column(Text, nullable=True))
    layer_links: List["LayerTeamLink"] = Relationship(
        back_populates="team", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    project_links: List["ProjectTeamLink"] = Relationship(
        back_populates="team", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    user_links: List["UserTeamLink"] = Relationship(
        back_populates="team", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
