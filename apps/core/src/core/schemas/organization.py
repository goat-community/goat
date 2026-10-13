from datetime import datetime
from enum import Enum
from uuid import UUID
from uuid import UUID as _UUID

from pydantic import BaseModel
from sqlmodel import SQLModel

from core.db.models.invitation import InvitationStatusEnum
from core.db.models.organization import (
    AvailableRegionsEnum,
    OrganizationBase,
    OrganizationIndustryEnum,
    OrganizationRolesEnum,
    OrganizationTypeEnum,
    OrganizationUseCaseEnum,
)
from core.utils.partial import optional


class OrganizationRead(OrganizationBase):
    id: _UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None


class TrialPlanTypeEnum(str, Enum):
    """This enum represents the trial subscription types."""

    starter = "goat_starter"
    profesional = "goat_professional"


class OrganizationCreateUpdateBase(BaseModel):
    name: str
    department: str
    industry: OrganizationIndustryEnum
    location: str
    newsletter_subscribe: bool | None = None
    type: OrganizationTypeEnum
    size: str | None = None
    use_case: OrganizationUseCaseEnum
    avatar: str | None = None
    phone_number: str | None = None


class OrganizationCreate(OrganizationCreateUpdateBase):
    name: str
    region: AvailableRegionsEnum


@optional
class OrganizationUpdate(OrganizationCreateUpdateBase):
    pass


class OrganizationMemberRoleUpdateEnum(str, Enum):
    admin = OrganizationRolesEnum.admin.value
    editor = OrganizationRolesEnum.editor.value
    viewer = OrganizationRolesEnum.viewer.value


class OrganizationUpdateMemberRole(SQLModel):
    role: OrganizationMemberRoleUpdateEnum


class OrganizationCreationRead(BaseModel):
    """Whether the caller may set up an organization
    (`ALLOW_ORGANIZATION_CREATION`, superusers always may)."""

    allowed: bool


class OrganizationPermanentlyDeleted(BaseModel):
    """What `DELETE /organizations/{id}/permanent` removed."""

    id: UUID
    # The former member, whose account stays without an organization; None
    # when the organization had no member left.
    user_id: UUID | None
    # Billing is not touched: with Stripe on, the customer and its trial
    # subscription stay in Stripe under this id.
    stripe_id: str | None


class OrganizationUser(BaseModel):
    id: UUID
    firstname: str | None
    lastname: str | None
    email: str
    roles: list[str]
    invitation_status: InvitationStatusEnum
    avatar: str | None


request_examples = {
    "organization": {
        "create": {
            "name": "test",
            "type": "government",
            "size": "25-50",
            "industry": "architecture",
            "department": "GIS",
            "use_case": "infrastructure_planning_and_design",
            "phone_number": "6479616224",
            "location": "AF",
            "newsletter_subscribe": True,
            "region": "EU",
        },
        "update": {"phone_number": "6479616225"},
        "update_user_role": {"role": "organization-admin"},
        "invite": {
            "user_email": "majkshkurti94@gmail.com",
            "organization_id": "e1c0c0b7-8e9c-4c4a-9a3c-0b5a2c1f6b6b",
            "role": "owner",
        },
        "invite_update": {"role": "admin"},
    }
}
