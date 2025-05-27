from typing import List, TYPE_CHECKING
from sqlmodel import (
    Column,
    Field,
    Relationship,
    Text,
    text,
)
from core.db.models._base_class import DateTimeBase
from enum import Enum
from sqlalchemy.dialects.postgresql import UUID as UUID_PG
from uuid import UUID
from core.core.config import settings


if TYPE_CHECKING:
    from ._link_model import LayerTeamLink, ProjectTeamLink, LayerOrganizationLink, ProjectOrganizationLink


class RessourceTypeEnum(str, Enum):
    organization = "organization"
    team = "team"
    layer = "layer"
    project = "project"


class Role(DateTimeBase, table=True):
    """
    A table representing a role. A role is a collection of permissions.

    Attributes:
        id (str): The unique identifier for the role.
        name (str): The name of the role.
    """

    __tablename__ = "role"
    __table_args__ = {"schema": settings.ACCOUNTS_SCHEMA}

    id: UUID | None = Field(
        sa_column=Column(
            UUID_PG(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=text("uuid_generate_v4()"),
        ),
        description="Organization ID",
    )
    name: str = Field(sa_column=Column(Text, nullable=False), max_length=255)