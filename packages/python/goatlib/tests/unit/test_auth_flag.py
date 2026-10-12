"""The AUTH flag every Python service reads.

The spellings mirror the web's ``isAuthDisabled`` (apps/web/lib/utils/
auth-flag.ts): an explicit falsy value turns auth off; unset or empty keeps
it on.
"""

import pytest
from goatlib.auth import AuthFlag, require_keycloak_url
from pydantic import BaseModel, ValidationError

pytestmark = pytest.mark.unit

ON = ["true", "True", "TRUE", "1", "yes", "on", "t", "y", ""]
OFF = ["false", "False", "FALSE", "0", "no", "off", "f", "n"]


class _Model(BaseModel):
    auth: AuthFlag = True


@pytest.mark.parametrize("raw", ON)
def test_on_spellings(raw: str) -> None:
    assert _Model(auth=raw).auth is True


@pytest.mark.parametrize("raw", OFF)
def test_off_spellings(raw: str) -> None:
    assert _Model(auth=raw).auth is False


def test_none_keeps_auth_on() -> None:
    assert _Model(auth=None).auth is True


def test_unknown_value_is_rejected() -> None:
    with pytest.raises(ValidationError):
        _Model(auth="maybe")


def test_require_keycloak_url_raises_when_auth_on_without_url() -> None:
    with pytest.raises(ValueError, match="KEYCLOAK_SERVER_URL"):
        require_keycloak_url(True, "")
    with pytest.raises(ValueError, match="KEYCLOAK_SERVER_URL"):
        require_keycloak_url(True, None)


def test_require_keycloak_url_passes_otherwise() -> None:
    require_keycloak_url(True, "http://kc")
    require_keycloak_url(False, "")
    require_keycloak_url(False, None)
