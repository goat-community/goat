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
            f"{settings.API_V1_STR}/isochrones/single",
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
        f"{settings.API_V1_STR}/isochrones/single",
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
        f"{settings.API_V1_STR}/isochrones/single",
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
        f"{settings.API_V1_STR}/isochrones/single",
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
        f"{settings.API_V1_STR}/isochrones/single",
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
            f"{settings.API_V1_STR}/isochrones/export/",
            json=geojson_payload,
            params={"return_type": export_type.value},
            headers=superuser_token_headers,
        )
        assert 200 <= r.status_code < 300
        assert r.headers["content-type"] == zip_mime_type


# TODO: Calculate isochrone reached network default geojson
# TODO: Calculate isochrone reached network scenario geojson
# TODO: Calculate isochrone reached network comparision geojson
# TODO: Calculate isochrone reached network comparision geobuf
# TODO: Calculate isochrone multi count pois draw
# TODO: Calculate isochrone multi count pois study area
# TODO: Calculate isochrone multi isochrone calculation with coordinates as start points
# TODO: Calculate isochrone multi isochrone calculation with pois as start points
# TODO: Isochrone export geojson
# TODO: Isochrone export shapefile
# TODO: Isochrone export xlsx
# TODO: User calculates isochrone outside of study area and gets error
