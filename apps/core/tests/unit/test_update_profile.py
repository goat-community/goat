from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from core.endpoints.v2 import users
from core.schemas.user import UserProfileUpdate
from fastapi import HTTPException
from keycloak.exceptions import KeycloakPutError

USER_ID = "d78bf1ae-72f5-4104-8f0c-f48c80f3f63b"
TOKEN = {"sub": USER_ID}


def _db_user() -> SimpleNamespace:
    return SimpleNamespace(
        id=USER_ID, email="old@example.com", firstname="A", lastname="B"
    )


def _kc_403() -> MagicMock:
    admin = MagicMock()
    admin.update_user.side_effect = KeycloakPutError(
        error_message=b'{"error":"unknown_error"}', response_code=403
    )
    return admin


def _kc_ok() -> MagicMock:
    admin = MagicMock()
    admin.update_user.return_value = {}
    return admin


async def _call(user_update: UserProfileUpdate, admin: MagicMock):
    with (
        patch.object(users.crud_user, "get", AsyncMock(return_value=_db_user())),
        patch.object(users, "keycloak_admin", AsyncMock(return_value=admin)),
        patch.object(
            users.crud_user, "update", AsyncMock(return_value="DB_UPDATED")
        ) as update_mock,
        patch.object(users.s3_service, "upload_asset", MagicMock()),
    ):
        result = await users.update_profile(
            db=MagicMock(), user=user_update, user_token=TOKEN
        )
    return result, update_mock


@pytest.mark.unit
async def test_avatar_only_skips_keycloak_and_updates_db() -> None:
    admin = _kc_403()  # would raise if called
    user_update = UserProfileUpdate(avatar="data:image/png;base64,aGVsbG8=")
    with (
        patch.object(users, "get_image_extension_from_base64", return_value="png"),
        patch.object(users, "decode_base64_file", return_value=b"x"),
    ):
        result, update_mock = await _call(user_update, admin)
    admin.update_user.assert_not_called()
    update_mock.assert_awaited_once()
    assert result == "DB_UPDATED"


@pytest.mark.unit
async def test_name_change_keycloak_error_raises_502_and_skips_db() -> None:
    admin = _kc_403()
    with pytest.raises(HTTPException) as exc:
        await _call(UserProfileUpdate(firstname="NewName"), admin)
    assert exc.value.status_code == 502
    admin.update_user.assert_called_once()


@pytest.mark.unit
async def test_name_change_keycloak_ok_updates_db() -> None:
    admin = _kc_ok()
    result, update_mock = await _call(UserProfileUpdate(firstname="NewName"), admin)
    admin.update_user.assert_called_once()
    update_mock.assert_awaited_once()
    assert result == "DB_UPDATED"
