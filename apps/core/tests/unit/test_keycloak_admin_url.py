from unittest import mock

import pytest
from core.deps import keycloak as kc


@pytest.mark.parametrize(
    "server_url",
    ["http://keycloak:8080/keycloak", "http://keycloak:8080/keycloak/"],
)
async def test_admin_client_keeps_relative_path(server_url: str) -> None:
    with (
        mock.patch.object(kc, "_admin", None),
        mock.patch.multiple(
            kc.settings,
            KEYCLOAK_SERVER_URL=server_url,
            REALM_NAME="goat",
            KEYCLOAK_CLIENT_ID="goat",
            KEYCLOAK_CLIENT_SECRET="secret",
        ),
    ):
        admin = await kc.keycloak_admin()
        assert admin is not None
        token_url = admin.connection.keycloak_openid.connection.base_url
    assert token_url == "http://keycloak:8080/keycloak/"
