"""A network selector set to the default network is no bundle.

The web's network selectors answer "default" for the default network (the
`DEFAULT_NETWORK_BUNDLE` of `BundleInput.tsx`). The toolbox leaves it out of
a request, but a workflow saves it in its node's config, so a tool can be
handed "default" for a field that otherwise names a bundle.
"""

import pytest
from goatlib.tools.schemas import ToolInputBase

pytestmark = pytest.mark.unit


class NetworkParams(ToolInputBase):
    pt_network_bundle_id: str | None = None
    street_network_bundle_id: str | None = None


def test_the_default_network_becomes_no_bundle() -> None:
    params = NetworkParams(
        user_id="u", pt_network_bundle_id="default", street_network_bundle_id="default"
    )
    assert params.pt_network_bundle_id is None
    assert params.street_network_bundle_id is None


def test_a_chosen_bundle_is_kept() -> None:
    bundle = "0f3ac6d0-b178-4f09-a3c9-fd529d7389df"
    assert (
        NetworkParams(user_id="u", pt_network_bundle_id=bundle).pt_network_bundle_id
        == bundle
    )
