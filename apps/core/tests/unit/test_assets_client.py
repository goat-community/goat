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


@pytest.mark.unit
def test_assets_served_by_core_live_in_the_data_bucket(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "ASSETS_SERVED_BY_CORE", True)
    monkeypatch.setattr(settings, "S3_BUCKET_NAME", "goat")
    service = S3Service()
    service.s3_client = MagicMock()
    service.assets_client = MagicMock()
    service.upload_asset(MagicMock(), "img/users/a.png", "image/png")
    service.delete_asset("img/users/a.png")
    service.s3_client.upload_fileobj.assert_called_once()
    assert service.s3_client.upload_fileobj.call_args.kwargs["Bucket"] == "goat"
    assert (
        service.s3_client.upload_fileobj.call_args.kwargs["Key"]
        == "assets/img/users/a.png"
    )
    service.s3_client.delete_object.assert_called_once_with(
        Bucket="goat", Key="assets/img/users/a.png"
    )
    service.assets_client.upload_fileobj.assert_not_called()


@pytest.mark.unit
async def test_asset_route_redirects_to_a_signed_url_under_assets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from core.endpoints.v2 import asset

    monkeypatch.setattr(settings, "ASSETS_SERVED_BY_CORE", True)
    signer = MagicMock(return_value="https://goat.example.org/goat/assets/x?sig")
    monkeypatch.setattr(asset.s3_service, "asset_download_url", signer)

    response = await asset.asset_file("img/users/a.png")
    assert response.status_code == 307
    assert response.headers["location"] == "https://goat.example.org/goat/assets/x?sig"
    assert response.headers["cache-control"].startswith("public, max-age=")
    signer.assert_called_once_with("img/users/a.png")


@pytest.mark.unit
@pytest.mark.parametrize(
    "served, key",
    [
        (False, "img/a.png"),
        (True, "../users/x/upload.zip"),
        (True, "img//a.png"),
        (True, ""),
    ],
)
async def test_asset_route_answers_404(
    monkeypatch: pytest.MonkeyPatch, served: bool, key: str
) -> None:
    from core.endpoints.v2 import asset
    from fastapi import HTTPException

    monkeypatch.setattr(settings, "ASSETS_SERVED_BY_CORE", served)
    with pytest.raises(HTTPException) as err:
        await asset.asset_file(key)
    assert err.value.status_code == 404


@pytest.mark.unit
def test_asset_url_is_signed_for_the_prefixed_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "S3_BUCKET_NAME", "goat")
    service = S3Service()
    service._public_client = MagicMock()
    service._public_client.generate_presigned_url.return_value = "signed"
    assert service.asset_download_url("img/a.png") == "signed"
    service._public_client.generate_presigned_url.assert_called_once_with(
        "get_object",
        Params={"Bucket": "goat", "Key": "assets/img/a.png"},
        ExpiresIn=3600,
    )
