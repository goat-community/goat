"""The assets bucket client and the URLs of uploaded assets."""

from unittest.mock import AsyncMock, MagicMock, patch

import boto3
import pytest
from core.core.config import settings
from core.endpoints.v2 import users
from core.schemas.user import UserProfileUpdate
from core.services.s3 import S3Service

USER_ID = "d78bf1ae-72f5-4104-8f0c-f48c80f3f63b"


@pytest.fixture(autouse=True)
def _assets_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    # boto3 reads a configured endpoint from these; the tests pin the endpoint
    # through settings alone.
    monkeypatch.delenv("AWS_ENDPOINT_URL", raising=False)
    monkeypatch.delenv("AWS_ENDPOINT_URL_S3", raising=False)
    monkeypatch.setattr(settings, "AWS_ACCESS_KEY_ID", "assets-key")
    monkeypatch.setattr(settings, "AWS_SECRET_ACCESS_KEY", "assets-secret")
    monkeypatch.setattr(settings, "AWS_REGION", "eu-central-1")
    monkeypatch.setattr(settings, "ASSETS_S3_ENDPOINT_URL", None)
    monkeypatch.setattr(settings, "ASSETS_S3_FORCE_PATH_STYLE", False)


@pytest.mark.unit
def test_assets_client_uses_the_configured_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "ASSETS_S3_ENDPOINT_URL", "http://garage:3900")
    monkeypatch.setattr(settings, "ASSETS_S3_FORCE_PATH_STYLE", True)
    client = S3Service().assets_client
    assert client.meta.endpoint_url == "http://garage:3900"
    assert client.meta.config.s3["addressing_style"] == "path"
    assert client.meta.config.request_checksum_calculation == "when_required"
    assert client.meta.config.response_checksum_validation == "when_required"


@pytest.mark.unit
def test_assets_client_without_endpoint_is_plain_aws() -> None:
    client = S3Service().assets_client
    plain = boto3.client("s3", region_name="eu-central-1")
    assert client.meta.endpoint_url == "https://s3.eu-central-1.amazonaws.com"
    assert client.meta.region_name == "eu-central-1"
    assert client.meta.config.signature_version == plain.meta.config.signature_version
    assert client.meta.config.s3 == plain.meta.config.s3


@pytest.mark.unit
async def test_avatar_url_is_built_from_assets_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "ASSETS_URL", "http://10.0.0.5:8080/goat-assets")
    upload = MagicMock()
    with (
        patch.object(
            users.crud_user,
            "get",
            AsyncMock(return_value=MagicMock(id=USER_ID, email="a@example.com")),
        ),
        patch.object(users.crud_user, "update", AsyncMock()) as update_mock,
        patch.object(users.s3_service, "upload_asset", upload),
        patch.object(users, "get_image_extension_from_base64", return_value="png"),
        patch.object(users, "decode_base64_file", return_value=b"x"),
    ):
        await users.update_profile(
            db=MagicMock(),
            user=UserProfileUpdate(avatar="data:image/png;base64,aGVsbG8="),
            user_token={"sub": USER_ID},
        )
    key = upload.call_args.args[1]
    avatar = update_mock.call_args.kwargs["obj_in"].avatar
    assert key.startswith(f"img/users/{settings.ENVIRONMENT}/avatar_{USER_ID}_T")
    assert avatar == f"http://10.0.0.5:8080/goat-assets/{key}"
