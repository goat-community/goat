from typing import Dict

import httpx
import requests

from src.core.config import settings
from src.schemas.isochrone import request_examples
from src.tests.utils.utils import get_superuser_token_headers


async def run_calculate_isochrone_single_default(
    client: httpx.AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    for isochrone_mode in request_examples["isochrone"].keys():
        data = request_examples["isochrone"][isochrone_mode]["value"]
        if isochrone_mode in ["pois_multi_isochrone", "transit_single"]:
            if settings.R5_HOST:
                try:
                    print("check R5 for 3 seconds...")
                    print(settings.R5_API_URL)
                    requests.get(settings.R5_API_URL, verify=False, timeout=3)
                except:
                    print(f"Coudn't reach R5! So skip call {isochrone_mode}.")
                    print()
                    continue
            else:
                print(f"R5 is not set. Skip call {isochrone_mode}")
                continue

        print(f'running: {request_examples["isochrone"][isochrone_mode].get("summary")}')
        r = await client.post(
            f"{settings.API_V1_STR}/isochrones",
            headers=superuser_token_headers,
            json=data,
        )
        print(r.status_code)
        assert 200 <= r.status_code < 300


async def call_isochrones_startup(app):
    print("First run of isochrones....")
    print("To prevent this calling, set DISABLE_NUMBA_STARTUP_CALL environment variable to True.")
    async with httpx.AsyncClient(app=app, base_url="http://localhost:5000") as client:
        superuser_token_headers = await get_superuser_token_headers(client)
        await run_calculate_isochrone_single_default(client, superuser_token_headers)

    print("Running isochrones first call complete!")
