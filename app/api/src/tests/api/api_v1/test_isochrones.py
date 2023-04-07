import asyncio
import mimetypes
from collections import defaultdict
from typing import Dict

import pyproj
import pytest
from httpx import AsyncClient
from shapely.geometry import shape
from shapely.ops import transform
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud
from src.crud.crud_scenario import scenario as crud_scenario
from src.core.config import settings
from src.db import models
from src.resources.enums import IsochroneExportType
from src.schemas.isochrone import request_examples
from src.schemas.scenario import (
    ScenarioFeatureCreate,
    ScenarioLayerFeatureEnum,
    ScenarioWaysModifiedCreate,
)
from src.tests.utils.utils import random_lower_string

pytestmark = pytest.mark.asyncio


isochrone_points = [
    {"x": 11.575306697287969, "y": 48.13697276799013},
    {"x": 11.649267515328072, "y": 48.11170160691228},
    {"x": 11.421973933692033, "y": 48.15037785861503},
    {"x": 11.502205510052336, "y": 48.192828373724126},
    {"x": 11.639844580841398, "y": 48.14919321406106},
    {"x": 11.41444174652473, "y": 48.16160500680954},
    {"x": 11.646678404267888, "y": 48.09628548434259},
    {"x": 11.526252711275939, "y": 48.14774225930469},
]

isochrone_scenario_new_bridge = {
    "features": [
        {
            "surface": "asphalt",
            "way_type": "bridge",
            "wheelchair": "yes",
            "way_id": None,
            "class_id": None,
            "edit_type": "n",
            "geom": "LINESTRING(11.602886 48.153347999999994,11.601907 48.153525)",
        }
    ]
}

isochrone_scenario_comparision = {
    "minutes": 10,
    "speed": 5,
    "modus": "comparison",
    "n": 2,
    "routing_profile": "walking_standard",
    "scenario_id": None,  # set after scenario creation
    "x": 11.602886678839361,
    "y": 48.153338885122594,
}


async def test_calculate_isochrone_single_default_bulk(
    client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    data = request_examples["single_isochrone"]["default"]["value"]
    for point in isochrone_points:
        data.update(point)
        r = await client.post(
            f"{settings.API_V1_STR}/indicators/isochrone/single",
            headers=superuser_token_headers,
            json=data,
        )
        response = r.json()
        assert 200 <= r.status_code < 300
        assert len(response["features"]) > 0
        assert len(response["features"][0]["geometry"]["coordinates"][0][0]) > 3


async def test_calculate_isochrone_single_scenario(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    superuser = await crud.user.get_by_key(db, key="email", value=settings.FIRST_SUPERUSER_EMAIL)
    obj_scenario = models.Scenario(
        scenario_name=random_lower_string(),
        user_id=superuser[0].id,
        study_area_id=superuser[0].active_study_area_id,
    )
    scenario = await crud_scenario.create(db=db, obj_in=obj_scenario)

    scenario_ways_modified_features = []
    for feature in isochrone_scenario_new_bridge["features"]:
        scenario_ways_modified_features.append(ScenarioWaysModifiedCreate(**feature))
    await crud_scenario.create_scenario_features(
        db,
        superuser[0],
        scenario.id,
        ScenarioLayerFeatureEnum.way_modified,
        ScenarioFeatureCreate(
            features=scenario_ways_modified_features,
        ),
    )
    isochrone_scenario_comparision["scenario_id"] = scenario.id
    r = await client.post(
        f"{settings.API_V1_STR}/indicators/isochrone/single",
        headers=superuser_token_headers,
        json=isochrone_scenario_comparision,
    )
    response = r.json()
    assert 200 <= r.status_code < 300
    assert len(response["features"]) > 0
    assert len(response["features"][0]["geometry"]["coordinates"][0][0]) > 3
    # Scenario geometry area should be greater than default geometry area when new feature is added
    project = pyproj.Transformer.from_crs(
        pyproj.CRS("EPSG:4326"), pyproj.CRS("EPSG:3857"), always_xy=True
    ).transform
    groups = defaultdict(list)
    for obj in response["features"]:
        obj["properties"]["area"] = transform(project, shape(obj["geometry"])).area
        groups[obj["properties"]["step"]].append(obj)
    for group, features in groups.items():
        default_area = 0
        scenario_area = 0
        for feature in features:
            if feature["properties"]["modus"] == "default":
                default_area = feature["properties"]["area"]
            else:
                scenario_area = feature["properties"]["area"]
        assert scenario_area > default_area


async def test_calculate_isochrone_single_walking_wheelchair(
    client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    data = request_examples["single_isochrone"]["default"]["value"]
    data["routing_profile"] = "walking_wheelchair"
    data.update(isochrone_points[0])
    r = await client.post(
        f"{settings.API_V1_STR}/isochrone/single",
        headers=superuser_token_headers,
        json=data,
    )
    response = r.json()
    assert 200 <= r.status_code < 300
    assert len(response["features"]) > 0
    assert len(response["features"][0]["geometry"]["coordinates"][0][0]) > 3


async def test_calculate_isochrone_single_cycling_standard(
    client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    data = request_examples["single_isochrone"]["default"]["value"]
    data["routing_profile"] = "cycling_standard"
    data.update(isochrone_points[0])
    r = await client.post(
        f"{settings.API_V1_STR}/isochrone/single",
        headers=superuser_token_headers,
        json=data,
    )
    response = r.json()
    assert 200 <= r.status_code < 300
    assert len(response["features"]) > 0
    assert len(response["features"][0]["geometry"]["coordinates"][0][0]) > 3


async def test_calculate_isochrone_single_cycling_pedelec(
    client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    data = request_examples["single_isochrone"]["default"]["value"]
    data["routing_profile"] = "cycling_pedelec"
    data.update(isochrone_points[0])
    r = await client.post(
        f"{settings.API_V1_STR}/isochrone/single",
        headers=superuser_token_headers,
        json=data,
    )
    response = r.json()
    assert 200 <= r.status_code < 300
    assert len(response["features"]) > 0
    assert len(response["features"][0]["geometry"]["coordinates"][0][0]) > 3


async def test_convert_geojson_to_shapefile_and_xlsx(
    client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    export_types = [IsochroneExportType.xlsx, IsochroneExportType.shp]
    geojson_payload = request_examples["geojson_to_export"]
    zip_mime_type = mimetypes.guess_type("x.zip")[0]
    for export_type in export_types:
        r = await client.post(
            f"{settings.API_V1_STR}/isochrone/export/",
            json=geojson_payload,
            params={"return_type": export_type.value},
            headers=superuser_token_headers,
        )
        assert 200 <= r.status_code < 300
        assert r.headers["content-type"] == zip_mime_type

test_payloads = {
    "reached_network_default_geojson": {"mode":"walking","settings":{"travel_time":20,"speed":5,"walking_profile":"standard"},"starting_point":{"input":[{"lat":48.17414317972603,"lon":11.5058719230466}]},"scenario":{"id":0,"modus":"default"},"output":{"type":"grid","resolution":13}},
    "reached_network_scenario_geojson": {"mode":"walking","settings":{"travel_time":20,"speed":5,"walking_profile":"standard"},"starting_point":{"input":[{"lat":48.150184567895735,"lon":11.55799774461109}]},"scenario":{"id":0,"modus":"scenario"},"output":{"type":"grid","resolution":13}},
    "multi_count_pois_study_area": {"mode":"walking","settings":{"travel_time":20,"speed":5,"walking_profile":"standard"},"starting_point":{"input":["nursery"],"region_type":"study_area","region":["95","105"]},"scenario":{"id":0,"modus":"default"},"output":{"type":"grid","resolution":13}},
    "multi_count_pois_draw":{"mode":"walking","settings":{"travel_time":20,"speed":5,"walking_profile":"standard"},"starting_point":{"input":["nursery"],"region_type":"draw","region":["POLYGON((11.497258198370304 48.16147474742104,11.547536667106236 48.163870221958376,11.540354028715388 48.13607583948297,11.497258198370304 48.12936459519315,11.477865074715016 48.14709955093468,11.497258198370304 48.16147474742104))"]},"scenario":{"id":0,"modus":"default"},"output":{"type":"grid","resolution":13}},
    "outside_of_study_area_and_gets_error": {"mode":"walking","settings":{"travel_time":20,"speed":5,"walking_profile":"standard"},"starting_point":{"input":[{"lat":48.13128218306605,"lon":11.336367098415318}]},"scenario":{"id":0,"modus":"default"},"output":{"type":"grid","resolution":13}},

}

async def isochrone_set_request(
    client: AsyncClient, superuser_token_headers: dict[str, str], data: dict
) -> None:
    r = await client.post(
        f"{settings.API_V1_STR}/indicators/isochrone",
        headers=superuser_token_headers,
        json=data,
    )
    return r

async def isochrone_get_results(
    client: AsyncClient, superuser_token_headers: dict[str, str], task_id: str
) -> None:
    r = await client.get(
        f"{settings.API_V1_STR}/indicators/result/{task_id}",
        headers=superuser_token_headers,
        params={"return_type": "geojson"},
    )
    return r

async def isochrone_test_base(
    client: AsyncClient, superuser_token_headers: dict[str, str], data: dict
) -> None:
    task_request = await isochrone_set_request(client, superuser_token_headers, data)
    assert task_request.status_code == 200
    task_id = task_request.json()["task_id"]

    for i in range(40):
        task_results = await isochrone_get_results(client, superuser_token_headers, task_id)
        assert task_results.status_code >= 200 and task_results.status_code < 300
        if task_results.status_code == 200:
            break
        else:
            await asyncio.sleep(1)

    assert task_results.status_code == 200

# Calculate isochrone reached network default geojson
async def test_calculate_isochrone_reached_network_default_geojson(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    data = test_payloads["reached_network_default_geojson"]
    await isochrone_test_base(client, superuser_token_headers, data)
    
# Calculate isochrone reached network scenario geojson
async def test_calculate_isochrone_reached_network_scenario_geojson(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    data = test_payloads["reached_network_scenario_geojson"]
    await isochrone_test_base(client, superuser_token_headers, data)

# Calculate isochrone multi count pois draw
async def test_calculate_isochrone_multi_count_pois_draw(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    data = test_payloads["multi_count_pois_draw"]
    await isochrone_test_base(client, superuser_token_headers, data)
    
# Calculate isochrone multi count pois study area
async def test_calculate_isochrone_multi_count_pois_study_area(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    data = test_payloads["multi_count_pois_study_area"]
    await isochrone_test_base(client, superuser_token_headers, data)

# TODO: Calculate isochrone reached network comparision geojson
# TODO: Calculate isochrone reached network comparision geobuf
# TODO: Calculate isochrone multi isochrone calculation with coordinates as start points
# TODO: Calculate isochrone multi isochrone calculation with pois as start points
#‌ TODO: Calculate isochrone multi isochrone calculation with pois and scenario

# TODO: Isochrone export geojson
# TODO: Isochrone export shapefile
# TODO: Isochrone export xlsx


# User calculates isochrone outside of study area and gets error
async def test_calculate_isochrone_outside_of_study_area_and_gets_error(
    client: AsyncClient, normaluser_token_headers: dict[str, str]
) -> None:
    data = test_payloads["outside_of_study_area_and_gets_error"]
    task_request = await isochrone_set_request(client, normaluser_token_headers, data)
    assert task_request.status_code == 403