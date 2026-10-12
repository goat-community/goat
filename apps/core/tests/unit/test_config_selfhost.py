"""core's defaults keep the hosted service working and move with the env.

The module-level ``settings`` is built at import, so these tests construct
the ``Settings`` class directly.
"""

from pathlib import Path

import pytest
from core.core.config import HOSTED_ARTWORK_URL, Settings
from core.db.session import DatabaseSessionManager

AWS_ASSETS_BUCKET_URL = "https://goat-assets.s3.eu-central-1.amazonaws.com"

_ENV_UNDER_TEST = [
    "CLIENT_URL",
    "ASSETS_URL",
    "STATIC_ASSETS_URL",
    "DEFAULT_PROJECT_THUMBNAIL",
    "DEFAULT_LAYER_THUMBNAIL",
    "USER_DEFAULT_AVATAR",
    "ORGANIZATION_DEFAULT_AVATAR",
    "EMAILS_FROM_NAME",
    "CUSTOM_DOMAIN_CNAME_TARGET",
    "POSTGRES_POOL_SIZE",
    "POSTGRES_MAX_OVERFLOW",
    "ASSETS_S3_ENDPOINT_URL",
    "ASSETS_S3_FORCE_PATH_STYLE",
    "AWS_S3_ASSETS_BUCKET",
    "AWS_REGION",
]


@pytest.fixture(autouse=True)
def _env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in _ENV_UNDER_TEST:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("AUTH", "false")
    monkeypatch.setenv("POSTGRES_SERVER", "localhost")
    monkeypatch.setenv("POSTGRES_USER", "goat")
    monkeypatch.setenv("POSTGRES_PASSWORD", "goat")
    monkeypatch.setenv("POSTGRES_DB", "goat")


def test_defaults() -> None:
    s = Settings()
    assert s.AWS_S3_ASSETS_BUCKET == "goat-assets"
    assert s.ASSETS_URL == AWS_ASSETS_BUCKET_URL
    assert s.POSTGRES_POOL_SIZE == 5
    assert s.POSTGRES_MAX_OVERFLOW == 10
    assert s.ASSETS_S3_ENDPOINT_URL is None
    assert s.ASSETS_S3_FORCE_PATH_STYLE is False


def test_self_host_defaults() -> None:
    s = Settings()
    assert s.EMAILS_FROM_NAME == "GOAT"
    assert s.CUSTOM_DOMAIN_CNAME_TARGET == ""
    assert s.custom_domains_enabled is False


def test_cname_target_turns_custom_domains_on(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CUSTOM_DOMAIN_CNAME_TARGET", "cname.example.org")
    assert Settings().custom_domains_enabled is True


def test_default_artwork_is_the_web_apps_own() -> None:
    s = Settings()
    assert s.STATIC_ASSETS_URL is None
    assert s.artwork_url == "/assets"
    assert s.DEFAULT_PROJECT_THUMBNAIL == "/assets/img/goat_new_project_artwork.png"
    assert s.DEFAULT_LAYER_THUMBNAIL == "/assets/img/goat_new_dataset_thumbnail.png"
    assert s.USER_DEFAULT_AVATAR == "/assets/img/no-user-thumb.jpg"
    assert s.ORGANIZATION_DEFAULT_AVATAR == "/assets/img/no-org-thumb.jpg"


def test_email_artwork_is_absolute_under_client_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CLIENT_URL", "https://goat.example.org/")
    assert Settings().email_artwork_url == "https://goat.example.org/assets"


def test_empty_static_assets_url_reads_as_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("STATIC_ASSETS_URL", "")
    s = Settings()
    assert s.STATIC_ASSETS_URL is None
    assert s.artwork_url == "/assets"


def test_static_assets_url_moves_the_default_artwork(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("STATIC_ASSETS_URL", "https://cdn.x/")
    monkeypatch.setenv("CLIENT_URL", "https://goat.example.org")
    s = Settings()
    assert s.STATIC_ASSETS_URL == "https://cdn.x"
    assert s.artwork_url == "https://cdn.x"
    assert s.email_artwork_url == "https://cdn.x"
    assert (
        s.DEFAULT_PROJECT_THUMBNAIL == "https://cdn.x/img/goat_new_project_artwork.png"
    )
    assert (
        s.DEFAULT_LAYER_THUMBNAIL == "https://cdn.x/img/goat_new_dataset_thumbnail.png"
    )
    assert s.USER_DEFAULT_AVATAR == "https://cdn.x/img/no-user-thumb.jpg"
    assert s.ORGANIZATION_DEFAULT_AVATAR == "https://cdn.x/img/no-org-thumb.jpg"
    # User uploads are served from their own base URL.
    assert s.ASSETS_URL == AWS_ASSETS_BUCKET_URL


def test_explicit_artwork_url_wins_over_static_assets_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("STATIC_ASSETS_URL", "https://cdn.x")
    monkeypatch.setenv("DEFAULT_PROJECT_THUMBNAIL", "https://other.example/p.png")
    assert Settings().DEFAULT_PROJECT_THUMBNAIL == "https://other.example/p.png"


@pytest.mark.parametrize(
    "stored",
    [
        "/assets/img/goat_new_dataset_thumbnail.png",
        f"{HOSTED_ARTWORK_URL}/img/goat_new_dataset_thumbnail.png",
    ],
)
def test_default_artwork_is_recognised_in_every_stored_form(stored: str) -> None:
    s = Settings()
    assert s.is_same_artwork(stored, s.DEFAULT_LAYER_THUMBNAIL)


def test_default_artwork_is_recognised_under_a_mirror(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("STATIC_ASSETS_URL", "https://cdn.x")
    s = Settings()
    for stored in (
        "https://cdn.x/img/goat_new_dataset_thumbnail.png",
        "/assets/img/goat_new_dataset_thumbnail.png",
        f"{HOSTED_ARTWORK_URL}/img/goat_new_dataset_thumbnail.png",
    ):
        assert s.is_same_artwork(stored, s.DEFAULT_LAYER_THUMBNAIL)


@pytest.mark.parametrize(
    "stored",
    [
        None,
        "",
        "thumbnails/layers/1_abc.png",
        "/assets/img/goat_new_project_artwork.png",
        "https://example.org/img/goat_new_dataset_thumbnail.png",
    ],
)
def test_other_images_are_not_the_default(stored: str | None) -> None:
    s = Settings()
    assert not s.is_same_artwork(stored, s.DEFAULT_LAYER_THUMBNAIL)


def test_an_explicit_default_is_matched_as_it_is(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DEFAULT_LAYER_THUMBNAIL", "https://other.example/l.png")
    s = Settings()
    assert s.is_same_artwork("https://other.example/l.png", s.DEFAULT_LAYER_THUMBNAIL)
    assert not s.is_same_artwork(
        "/assets/img/goat_new_dataset_thumbnail.png", s.DEFAULT_LAYER_THUMBNAIL
    )


def test_absolute_url_resolves_root_relative_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CLIENT_URL", "https://goat.example.org/")
    s = Settings()
    assert s.absolute_url("/assets/x.png") == "https://goat.example.org/assets/x.png"
    assert s.absolute_url("https://cdn.x/x.png") == "https://cdn.x/x.png"
    assert s.absolute_url("//cdn.x/x.png") == "//cdn.x/x.png"


def test_assets_url_drops_a_trailing_slash(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ASSETS_URL", "http://10.0.0.5:8080/goat-assets/")
    assert Settings().ASSETS_URL == "http://10.0.0.5:8080/goat-assets"


def test_pool_settings_reach_the_engine(monkeypatch: pytest.MonkeyPatch) -> None:
    from core.db import session

    monkeypatch.setattr(session.settings, "POSTGRES_POOL_SIZE", 2)
    monkeypatch.setattr(session.settings, "POSTGRES_MAX_OVERFLOW", 3)
    manager = DatabaseSessionManager()
    manager.init("postgresql+psycopg://goat:goat@localhost:5432/goat")
    assert manager._engine is not None
    pool = manager._engine.pool
    assert pool.size() == 2
    assert pool._max_overflow == 3  # type: ignore[attr-defined]


def test_no_hosted_asset_host_outside_the_config_defaults() -> None:
    src = Path(__file__).resolve().parents[2] / "src"
    config = src / "core" / "core" / "config.py"
    offenders = [
        f"{path.relative_to(src)}:{lineno}"
        for path in src.rglob("*")
        if path.is_file() and path != config and path.suffix in {".py", ".html"}
        for lineno, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        )
        if "assets.plan4better.de" in line
    ]
    assert offenders == []


def test_assets_url_follows_the_aws_bucket(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AWS_S3_ASSETS_BUCKET", "my-assets")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    assert Settings().ASSETS_URL == "https://my-assets.s3.us-east-1.amazonaws.com"


def test_assets_url_required_for_a_custom_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ASSETS_S3_ENDPOINT_URL", "http://garage:3900")
    with pytest.raises(ValueError, match="ASSETS_URL must be set"):
        Settings()
    monkeypatch.setenv("ASSETS_URL", "")
    with pytest.raises(ValueError, match="ASSETS_URL must be set"):
        Settings()
    monkeypatch.setenv("ASSETS_URL", "https://goat.example.org/goat-assets")
    assert Settings().ASSETS_URL == "https://goat.example.org/goat-assets"
