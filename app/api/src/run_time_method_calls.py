from typing import Dict

import httpx

from src.core.config import settings
from src.tests.api.api_v1 import test_isochrones as isochrones
from src.tests.utils.utils import get_superuser_token_headers

isochrone_request_examples = {
    "cycling": {
        "mode": "cycling",
        "settings": {"travel_time": 20, "speed": 15, "cycling_profile": "standard"},
        "starting_point": {"input": [{"lat": 48.17723361894386, "lon": 11.479921697097279}]},
        "scenario": {"id": 0, "modus": "default"},
        "output": {"type": "grid", "resolution": 12},
    },
    "walking": {
        "mode": "walking",
        "settings": {"travel_time": "10", "speed": "5", "walking_profile": "standard"},
        "starting_point": {"input": [{"lat": 48.1502132, "lon": 11.5696284}]},
        "scenario": {"id": 0, "modus": "default"},
        "output": {"type": "grid", "steps": "12"},
    },
}


async def run_calculate_isochrone_single_default(
    client: httpx.AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    # data["routing_profile"] = "single_walking_default"
    for mode in ["walking", "cycling"]:
        data = isochrone_request_examples[mode]
        print(mode)
        r = await client.post(
            f"{settings.API_V1_STR}/isochrones",
            headers=superuser_token_headers,
            json=data,
        )
        # response = r.json()
        assert 200 <= r.status_code < 300


async def call_isochrones_startup(app):
    print("First run of isochrones....")
    async with httpx.AsyncClient(app=app, base_url="http://localhost:5000") as client:
        superuser_token_headers = await get_superuser_token_headers(client)
        await run_calculate_isochrone_single_default(client, superuser_token_headers)

    print("Running isochrones first call complete!")
