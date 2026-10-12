"""KeycloakAuth fetches the realm public key on demand.

Services may start before Keycloak is reachable; the first token after it
comes up must validate without restarting the service.
"""

from unittest import mock

import pytest
import requests
from goatlib.auth import KeycloakAuth
from jose import JOSEError

pytestmark = pytest.mark.unit

RAW = "MIIB...fake"


def _resp(key: str | None) -> mock.Mock:
    r = mock.Mock()
    r.raise_for_status.return_value = None
    r.json.return_value = {"public_key": key} if key else {}
    return r


def test_no_network_call_at_construction() -> None:
    with mock.patch("goatlib.auth.requests.get") as get:
        KeycloakAuth("http://kc", "goat")
    get.assert_not_called()


def test_key_fetched_on_first_decode_after_initial_failure() -> None:
    auth = KeycloakAuth("http://kc", "goat", retry_interval=0)
    with (
        mock.patch(
            "goatlib.auth.requests.get",
            side_effect=[requests.ConnectionError("down"), _resp(RAW)],
        ) as get,
        mock.patch("goatlib.auth.jwt.decode", return_value={"sub": "u"}),
    ):
        with pytest.raises(JOSEError):
            auth.decode_token("t")
        assert auth.decode_token("t") == {"sub": "u"}
    assert get.call_count == 2
    assert auth.public_key and RAW in auth.public_key


def test_key_is_cached_after_success() -> None:
    auth = KeycloakAuth("http://kc", "goat", retry_interval=0)
    with (
        mock.patch("goatlib.auth.requests.get", return_value=_resp(RAW)) as get,
        mock.patch("goatlib.auth.jwt.decode", return_value={"sub": "u"}),
    ):
        for _ in range(3):
            auth.decode_token("t")
    assert get.call_count == 1


def test_response_without_key_is_retried() -> None:
    auth = KeycloakAuth("http://kc", "goat", retry_interval=0)
    with (
        mock.patch(
            "goatlib.auth.requests.get", side_effect=[_resp(None), _resp(RAW)]
        ) as get,
        mock.patch("goatlib.auth.jwt.decode", return_value={"sub": "u"}),
    ):
        with pytest.raises(JOSEError):
            auth.decode_token("t")
        assert auth.decode_token("t") == {"sub": "u"}
    assert get.call_count == 2


def test_retry_is_rate_limited() -> None:
    auth = KeycloakAuth("http://kc", "goat", retry_interval=3600)
    with mock.patch(
        "goatlib.auth.requests.get", side_effect=requests.ConnectionError("down")
    ) as get:
        for _ in range(5):
            with pytest.raises(JOSEError):
                auth.decode_token("t")
    assert get.call_count == 1


def test_verify_signature_false_never_fetches() -> None:
    auth = KeycloakAuth("http://kc", "goat", verify_signature=False)
    with (
        mock.patch("goatlib.auth.requests.get") as get,
        mock.patch("goatlib.auth.jwt.decode", return_value={}),
    ):
        auth.decode_token("t")
    get.assert_not_called()
