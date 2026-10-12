from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.crud.crud_team import team as crud_team
from core.crud.crud_user import user as crud_user
from core.db.models.organization import OrganizationRolesEnum
from core.db.models.team import Team, TeamRolesEnum
from core.db.models.user import User
from core.deps.auth import auth_z, user_token
from core.endpoints.deps import get_db
from core.schemas.team import (
    TeamCreate,
    TeamMember,
    TeamRead,
    TeamUpdate,
    request_examples,
)

router = APIRouter()


async def _require_team_manager(db: AsyncSession, team_id: str, user_id: str) -> None:
    """Renaming or deleting a team is for its owner and the organization's
    admins and owners (who can clean up a team whose owner has left).
    Organization editors and viewers get 403 for teams they do not own."""
    team_role = await crud_team.get_member_role(db=db, team_id=team_id, user_id=user_id)
    if team_role == TeamRolesEnum.owner:
        return
    user = await crud_user.get_user_with_roles(db_session=db, user_id=user_id)
    org_roles = {link.role.name for link in user.role_links} if user else set()
    if org_roles & {OrganizationRolesEnum.owner, OrganizationRolesEnum.admin}:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Only the team's owner or an organization admin can do this",
    )


@router.get(
    "",
    summary="Get Teams List for a user",
    response_model=List[TeamRead],
    dependencies=[Depends(auth_z)],
)
async def get_team_list(
    *,
    db: AsyncSession = Depends(get_db),
    user_token: dict = Depends(user_token),
) -> Any:
    """
    Get Content List for a user
    """
    user_id = user_token["sub"]
    teams = await crud_team.get_all(db=db, user_id=user_id)
    return teams


@router.get(
    "/{team_id}",
    summary="Get Team by ID",
    response_model=TeamRead | None,
    dependencies=[Depends(auth_z)],
)
async def get_team_by_id(
    *,
    db: AsyncSession = Depends(get_db),
    user_token: dict = Depends(user_token),
    team_id: str,
) -> Any:
    """
    Get Team by ID
    """
    user_id = user_token["sub"]
    team = await crud_team.get_by_id(db=db, team_id=team_id, user_id=user_id)
    return team


@router.get(
    "/{team_id}/members",
    summary="Get Team Members",
    response_model=List[TeamMember],
    dependencies=[Depends(auth_z)],
)
async def get_team_members(
    *,
    db: AsyncSession = Depends(get_db),
    user_token: dict = Depends(user_token),
    team_id: str,
) -> Any:
    """
    Get Team Members
    """
    team_members = await crud_team.get_team_members(db=db, team_id=team_id)

    return team_members


@router.post(
    "",
    summary="Create a new team",
    response_model=Team,
    dependencies=[Depends(auth_z)],
)
async def create_team(
    *,
    db: AsyncSession = Depends(get_db),
    user_token: dict = Depends(user_token),
    team: TeamCreate = Body(..., examples=[request_examples["team"]["create"]]),
) -> Any:
    """
    Create a new team
    """
    user_id = user_token["sub"]
    team = await crud_team.create_team(db=db, team_obj=team, user_id=user_id)
    return team


@router.patch(
    "/{team_id}/profile",
    summary="Update team",
    response_model=Team,
    dependencies=[Depends(auth_z)],
)
async def update_team(
    *,
    db: AsyncSession = Depends(get_db),
    user_token: dict = Depends(user_token),
    team_id: str,
    team: TeamUpdate = Body(..., examples=[request_examples["team"]["update"]]),
) -> Any:
    """
    Update a team
    """
    await _require_team_manager(db, team_id, user_token["sub"])
    db_obj = await crud_team.get(db=db, id=team_id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    updated_team = await crud_team.update_team(db=db, db_obj=db_obj, team_obj=team)
    return updated_team


@router.delete(
    "/{team_id}",
    summary="Delete a team",
    dependencies=[Depends(auth_z)],
)
async def delete_team(
    *,
    db: AsyncSession = Depends(get_db),
    user_token: dict = Depends(user_token),
    team_id: str,
) -> Any:
    """
    Delete a team
    """
    await _require_team_manager(db, team_id, user_token["sub"])
    team = await crud_team.delete_team(db=db, team_id=team_id)
    return team


@router.post(
    "/{team_id}/users/{user_id}",
    summary="Add a user to an team",
    response_model=User,
    dependencies=[Depends(auth_z)],
)
async def add_user_to_team(
    *,
    db: AsyncSession = Depends(get_db),
    user_token: dict = Depends(user_token),
    user_id: str | None = None,
    team_id: str,
) -> Any:
    """
    Add a user to a team. Only the team's owner may, and only users of the
    team's organization can be added.
    """
    caller_role = await crud_team.get_member_role(
        db=db, team_id=team_id, user_id=user_token["sub"]
    )
    if caller_role != TeamRolesEnum.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the team's owner can add members",
        )
    team = await crud_team.get(db=db, id=team_id)
    user = await crud_user.get(db, user_id)
    if not team or not user or user.organization_id != team.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only users of the team's organization can be added",
        )
    member = await crud_team.add_team_member(db=db, team_id=team_id, user_id=user_id)

    return member


@router.delete(
    "/{team_id}/users/{user_id}",
    summary="Remove a user from an team",
    dependencies=[Depends(auth_z)],
)
async def remove_user_from_team(
    *,
    db: AsyncSession = Depends(get_db),
    user_token: dict = Depends(user_token),
    user_id: str | None = None,
    team_id: str,
) -> Any:
    """
    Remove a user from a team. The team's owner may remove anyone but
    themselves (the team would be left without an owner); every other
    member may only remove themselves, which is leaving the team.
    """
    caller_id = user_token["sub"]
    caller_role = await crud_team.get_member_role(
        db=db, team_id=team_id, user_id=caller_id
    )
    removes_self = str(user_id) == str(caller_id)
    if caller_role == TeamRolesEnum.owner and removes_self:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The team's owner cannot leave the team; delete it instead",
        )
    if caller_role != TeamRolesEnum.owner and not (caller_role and removes_self):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the team's owner can remove other members",
        )

    await crud_team.remove_team_member(db=db, team_id=team_id, user_id=user_id)

    return {"message": "User removed from team"}
