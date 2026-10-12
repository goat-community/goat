from datetime import datetime
from enum import Enum
from typing import Any, Literal
from uuid import UUID

from pydantic import field_validator
from sqlmodel import SQLModel

from core.db.models.invitation import (
    InvitationStatusEnum,
    InvitationType,
)
from core.db.models.organization import OrganizationRolesEnum


class InvitationCreate(SQLModel):
    send_by: UUID
    send_to: UUID | None = None
    team_id: UUID | None = None
    organization_id: UUID | None = None
    type: InvitationType
    payload: dict
    expires: datetime | None = None
    status: InvitationStatusEnum


class OrganizationInvitationRole(str, Enum):
    admin = OrganizationRolesEnum.admin.value
    editor = OrganizationRolesEnum.editor.value
    viewer = OrganizationRolesEnum.viewer.value


class InvitationUpdate(SQLModel):
    status: InvitationStatusEnum


class InvitationOrgCreate(SQLModel):
    user_email: str
    role: OrganizationInvitationRole
    expires: int | None = None

    @field_validator("user_email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        # Keycloak stores emails lowercase; the invitation payload must match
        # the token's email claim, so normalize at the boundary.
        return value.strip().lower()


class InvitationOrgUpdate(SQLModel):
    role: OrganizationInvitationRole | None = None


class InvitationOrgCreateRead(SQLModel):
    """A created organization invitation.

    ``account_setup`` is set when GOAT created the invitee's Keycloak account
    (KEYCLOAK_PROVISION_INVITED_USERS): ``email_sent`` when Keycloak emailed
    the invitee a link to set a password, ``manual`` when that email could not
    be sent and an administrator must set the password in the Keycloak admin
    console. It is ``None`` when the invitee already had an account or GOAT
    does not create accounts.
    """

    id: UUID | None = None
    send_by: UUID
    send_to: UUID | None = None
    team_id: UUID | None = None
    organization_id: UUID | None = None
    type: InvitationType
    payload: dict[str, Any]
    expires: datetime | None = None
    status: InvitationStatusEnum
    created_at: datetime | None = None
    updated_at: datetime | None = None
    account_setup: Literal["email_sent", "manual"] | None = None
