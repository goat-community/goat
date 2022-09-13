from typing import Dict

import httpx
import requests

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
    "transit": {
        "mode": "transit",
        "settings": {
            "travel_time": "60",
            "transit_modes": ["bus", "tram", "subway", "rail"],
            "weekday": "0",
            "access_mode": "walk",
            "egress_mode": "walk",
            "bike_traffic_stress": 4,
            "from_time": 25200,
            "to_time": 39600,
            "max_rides": 4,
            "max_bike_time": 20,
            "max_walk_time": 20,
            "percentiles": [5, 25, 50, 75, 95],
            "monte_carlo_draws": 200,
            "decay_function": {
                "type": "logistic",
                "standard_deviation_minutes": 12,
                "width_minutes": 10,
            },
        },
        "starting_point": {"input": [{"lat": 48.1502132, "lon": 11.5696284}]},
        "scenario": {"id": 0, "modus": "default"},
        "output": {"type": "grid", "resolution": "9"},
    },
}


async def run_calculate_isochrone_single_default(
    client: httpx.AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    # data["routing_profile"] = "single_walking_default"
    for mode in ["transit", "walking"]:
        if mode == "transit":
            if settings.R5_API_URL:
                try:
                    print("check R5 for 3 seconds...")
                    requests.get(settings.R5_API_URL, verify=False, timeout=3)
                except:
                    print("Coudn't reach R5! So skip call transit.")
                    print()
                    continue
            else:
                continue

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
