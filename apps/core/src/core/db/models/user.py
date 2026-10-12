from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import UUID as UUID_PG
from sqlmodel import (
    Boolean,
    Column,
    Field,
    ForeignKey,
    Integer,
    Relationship,
    SQLModel,
    Text,
)

from core.core.config import settings
from core.db.models._base_class import UUIDServerDefaultBase

if TYPE_CHECKING:
    from ._link_model import UserRoleLink, UserTeamLink
    from .bundle import Bundle
    from .folder import Folder
    from .organization import Organization
    from .space import Space
    from .system_setting import SystemSetting


class UserBase(SQLModel):
    email: str = Field(sa_column=Column(Text, nullable=False))
    firstname: str = Field(sa_column=Column(Text, nullable=True))
    lastname: str = Field(sa_column=Column(Text, nullable=True))
    avatar: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    newsletter_subscribe: bool | None = Field(
        default=None, sa_column=Column(Boolean, nullable=True)
    )
    hubspot_id: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    # Odoo contact (res.partner) this user is (see core.odoo). Set by the
    # support module on the first lookup/creation; shared with billing.
    odoo_contact_id: int | None = Field(
        default=None, sa_column=Column(Integer, nullable=True)
    )
    organization_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            UUID_PG(as_uuid=True),
            ForeignKey(f"{settings.SCHEMA}.organization.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )


class User(UUIDServerDefaultBase, UserBase, table=True):
    """A user, member of an organization. Most attributes live in Keycloak."""

    __tablename__ = "user"
    __table_args__ = {"schema": settings.SCHEMA}

    # Relationships
    folders: List["Folder"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    bundles: List["Bundle"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    system_setting: "SystemSetting" = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    team_links: List["UserTeamLink"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    role_links: List["UserRoleLink"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    organization: "Organization" = Relationship(back_populates="users")
    # passive_deletes: on delete, defer to the DB's ON DELETE CASCADE on
    # space.user_id instead of the ORM proactively nulling it out first,
    # which would violate space_exactly_one_owner (a space always has an
    # owner; a deleted user's personal space is deleted with it, not orphaned).
    space: Optional["Space"] = Relationship(
        sa_relationship_kwargs={"uselist": False, "passive_deletes": True},
    )


Index("idx_user_organization_id", User.__table__.c.organization_id)
