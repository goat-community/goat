import asyncio
import pyproj
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src import crud
from src.crud.crud_scenario import scenario as crud_scenario
from src.core.config import settings
from src.db import models
from src.schemas.heatmap import request_examples

from src.tests.utils.utils import random_lower_string

pytestmark = pytest.mark.asyncio

async def heatmap_set_request(
    client: AsyncClient, superuser_token_headers: dict[str, str], data: dict
) -> None:
    r = await client.post(
        f"{settings.API_V1_STR}/indicators/heatmap",
        headers=superuser_token_headers,
        json=data,
    )
    return r

async def heatmap_get_results(
    client: AsyncClient, superuser_token_headers: dict[str, str], task_id: str
) -> None:
    r = await client.get(
        f"{settings.API_V1_STR}/indicators/result/{task_id}",
        headers=superuser_token_headers,
        params={"return_type": "geojson"},
    )
    return r

async def heatmap_test_base(
    client: AsyncClient, superuser_token_headers: dict[str, str], data: dict
) -> None:
    task_request = await heatmap_set_request(client, superuser_token_headers, data)
    assert task_request.status_code == 200
    task_id = task_request.json()["task_id"]
    
    for i in range(10):
        task_results = await heatmap_get_results(client, superuser_token_headers, task_id)
        assert task_results.status_code >= 200 and task_results.status_code < 300
        if task_results.status_code == 200:
            break
        else:
            await asyncio.sleep(1)
    
    assert task_results.status_code == 200



async def test_connectivity_heatmap_6_walking(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    data = request_examples["connectivity_heatmap_6_walking"]["value"]
    await heatmap_test_base(client, superuser_token_headers, data)
    
    
async def test_modified_gaussian_hexagon_10(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    data = request_examples["modified_gaussian_hexagon_10"]["value"]
    await heatmap_test_base(client, superuser_token_headers, data)

async def test_connectivity_heatmap_6_transit(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    data = request_examples["connectivity_heatmap_6_transit"]["value"]
    await heatmap_test_base(client, superuser_token_headers, data)

async def test_modified_gaussian_hexagon_9(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    data = request_examples["modified_gaussian_hexagon_9"]["value"]
    await heatmap_test_base(client, superuser_token_headers, data)

async def test_modified_gaussian_hexagon_6(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    data = request_examples["modified_gaussian_hexagon_6"]["value"]
    await heatmap_test_base(client, superuser_token_headers, data)

async def test_combined_modified_gaussian_hexagon_6(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    data = request_examples["combined_modified_gaussian_hexagon_6"]["value"]
    await heatmap_test_base(client, superuser_token_headers, data)

async def test_closest_average_hexagon_10(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    data = request_examples["closest_average_hexagon_10"]["value"]
    await heatmap_test_base(client, superuser_token_headers, data)

async def test_closest_average_hexagon_9(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    data = request_examples["closest_average_hexagon_9"]["value"]
    await heatmap_test_base(client, superuser_token_headers, data)

async def test_closest_average_hexagon_6(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    data = request_examples["closest_average_hexagon_6"]["value"]
    await heatmap_test_base(client, superuser_token_headers, data)

async def test_connectivity_heatmap_10(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    data = request_examples["connectivity_heatmap_10"]["value"]
    await heatmap_test_base(client, superuser_token_headers, data)

async def test_aggregated_data_heatmap_10(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    data = request_examples["aggregated_data_heatmap_10"]["value"]
    await heatmap_test_base(client, superuser_token_headers, data)

async def test_modified_gaussian_population_6(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    data = request_examples["modified_gaussian_population_6"]["value"]
    await heatmap_test_base(client, superuser_token_headers, data)