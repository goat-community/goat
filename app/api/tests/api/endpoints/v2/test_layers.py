from typing import Generator
import pytest

from httpx import AsyncClient
from src.db.models.layer import Layer
from src.main import app
from src.schemas.layer import request_examples, request_examples_update, LayerRead

url = "http://localhost:5000/api/v2"


# @pytest.fixture(scope="function")
# async def test_client():
#     async with AsyncClient(app=app, base_url=url) as client:
#         yield client


# @pytest.mark.asyncio
# class TestLayers:
#     pagination_query_params = "skip=0&limit=100"

#     @pytest.mark.parametrize(
#         "method, endpoint, data, expected_status, expected_response",
#         [
#             # ("get", f"/layers?{pagination_query_params}", None, 200, None),
#             # ("get", f"/layers?{pagination_query_params}", None, 200, None),
#             # ("post", "/layer", {}, 201, None),  # Add expected JSON response for successful login
#             # ("get", "/layers/get_layer/2adf749a-ba19-4b9e-bd24-bd001022dd45", None, 200, None),
#             # ("put", "/layer/1", {}, 200, None),
#             # ("delete", "/layer/1", None, 200, None),
#             #
#         ],
#     )
#     async def test(
#         self, test_client, method, endpoint, data, expected_status, expected_response
#     ):
#         if method == "get":
#             response = await test_client.get(endpoint)
#         elif method == "put":
#             response = await test_client.put(endpoint, json=data)
#         elif method == "delete":
#             response = await test_client.delete(endpoint)
#         else:  # Default to POST
#             response = await test_client.post(endpoint, json=data)
#         assert response.status_code == expected_status
#         if expected_response is not None:
#             assert response.json() == expected_response


@pytest.mark.asyncio
async def test_layer_create():
    client = AsyncClient(app=app, base_url=url)
    example_data = request_examples["create"]["table_layer"]["value"]
    response_post = await client.post("/layers/create_layer", json=example_data)
    response_id = response_post.json()["content"]["id"]
    response_get_by_id = await client.get(f"/layers/get_layer/{response_id}")
    example_data_updated = request_examples_update["update"]["table_layer"]["value"]
    response_update = await client.put(
        f"/layers/update_layer/{response_id}", json=example_data_updated
    )
    response_delete = await client.delete(f"/layers/delete_layer/{response_id}")

    await client.aclose()

    # post
    assert response_post.status_code == 200
    # assert isresponse_post.json()
    # assert_is_instance_value = isinstance(response_post.json()["content"], Layer)
    # assert assert_is_instance_value == True
    assert type(response_post.json()) == dict
    # get by id
    assert response_get_by_id.status_code == 200
    assert response_get_by_id.json()["content"]["id"] == response_id
    # update
    assert response_update.status_code == 200
    assert (
        response_update.json()["content"]["description"]
        == "Updated content description"
    )
    # delete
    assert response_delete.status_code == 200
