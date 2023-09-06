from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from src.db.models.user import User
from src.schemas.error import HTTPError
from src.db.session import AsyncSession
from pydantic import UUID4
from src.endpoints.deps import get_user_id, get_db
from src.crud.crud_user import user as crud_user

router = APIRouter()


@router.post(
    "",
    response_model=User,
)
async def create_user(
    *,
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID4 = Depends(get_user_id),
):
    """Create a user. This will read the user ID from the JWT token or use the pre-defined user_id if running without authentication."""

    # Check if user already exists
    user = await crud_user.get(async_session, id=user_id)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    else:
        user = await crud_user.create(async_session, obj_in=User(id=user_id))
        # Create user tables
        await crud_user.create_user_data_tables(async_session, user_id=user_id)
        return user


@router.delete(
    "",
    response_model=None,
    status_code=204,
)
async def delete_user(
    *,
    async_session: AsyncSession = Depends(get_db),
    user_id: UUID4 = Depends(get_user_id),
):
    """Delete a user and all of the related contents. This will read the user ID from the JWT token or use the pre-defined user_id if running without authentication."""
    user = await crud_user.get(async_session, id=user_id)

    if user:
        await crud_user.remove(async_session, id=user_id)
        # Delete user tables
        await crud_user.delete_user_data_tables(async_session, user_id=user.id)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return
