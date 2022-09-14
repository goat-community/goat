from typing import Dict

import httpx
import requests
import rich

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
                    rich.print("[blue]check R5 for 3 seconds...[/blue]")
                    requests.get(settings.R5_API_URL, verify=False, timeout=3)
                except:
                    rich.print(
                        f"[orange3]Coudn't reach R5! So skip call:[/orange3] [bold]{isochrone_mode}[/bold]"
                    )
                    print()
                    continue
            else:
                rich.print(
                    f"[orange3]R5 is not set. Skip call:[/orange3] [bold]{isochrone_mode}[/bold]"
                )
                continue

        rich.print(
            f'[bold]running: [light_slate_blue]{request_examples["isochrone"][isochrone_mode].get("summary")}[/light_slate_blue]...[/bold]'
        )
        r = await client.post(
            f"{settings.API_V1_STR}/isochrones",
            headers=superuser_token_headers,
            json=data,
        )
        assert 200 <= r.status_code < 300
        rich.print(
            f'[green1]Finished:[/green1] {request_examples["isochrone"][isochrone_mode].get("summary")}'
        )


async def call_isochrones_startup(app):
    rich.print("[bold]First run of isochrones...[/bold]")
    rich.print(
        "To prevent this calling, set [blue][bold]DISABLE_NUMBA_STARTUP_CALL[/bold][/blue] environment variable to [bold]True[/bold].\n"
    )
    async with httpx.AsyncClient(app=app, base_url="http://localhost:5000") as client:
        superuser_token_headers = await get_superuser_token_headers(client)
        await run_calculate_isochrone_single_default(client, superuser_token_headers)

    rich.print("\n[green4]Running isochrones first call complete![/green4]")
