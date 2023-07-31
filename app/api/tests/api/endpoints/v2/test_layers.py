from typing import Generator
import pytest

from httpx import AsyncClient
from src.main import app

url = "http://localhost:5000/api/v2"


@pytest.fixture(scope="function")
async def test_client():
    async with AsyncClient(app=app, base_url=url) as client:
        yield client


@pytest.mark.asyncio
class TestLayers:
    pagination_query_params = "skip=0&limit=100"
    @pytest.mark.parametrize(
        "method, endpoint, data, expected_status, expected_response",
        [
            ("get", f"/layers?{pagination_query_params}", None, 200, None),
            # ("post", "/layer", {}, 201, None),  # Add expected JSON response for successful login
            ("get", "/layers/get_layer/2adf749a-ba19-4b9e-bd24-bd001022dd45", None, 200, None),
            # ("put", "/layer/1", {}, 200, None),
            # ("delete", "/layer/1", None, 200, None),
            #          
        ],
    )
    async def test(
        self, test_client, method, endpoint, data, expected_status, expected_response
    ):
        if method == "get":
            response = await test_client.get(endpoint)
        elif method == "put":
            response = await test_client.put(endpoint, json=data)
        elif method == "delete":
            response = await test_client.delete(endpoint)
        else:  # Default to POST
            response = await test_client.post(endpoint, json=data)
        assert response.status_code == expected_status
        if expected_response is not None:
            assert response.json() == expected_response


# @pytest.mark.asyncio
# async def test_temporal_token():
#     client = AsyncClient(app=app, base_url=url)

#     response = await client.post("/layers")

#     await client.aclose()

#     assert response.status_code == 210
