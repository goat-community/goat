import pytest

from src.core.isochrone import Isochrone
from src.tests.utils.isochrone import get_sample_network

pytestmark = pytest.mark.asyncio


def test_isochrone():
    edges_network, starting_id, distance_limits = get_sample_network(minutes=5)
    isochrone = Isochrone(edges_network, starting_id, distance_limits)
    isochrone.compute_isochrone()  # TEST syntax

    print()


if __name__ == "__main__":
    test_isochrone()
