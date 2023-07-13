import enum
import uuid
from typing import Any, List

import pyproj
from fastapi import HTTPException
from geoalchemy2.shape import WKTElement, to_shape
from shapely import Polygon
from shapely.ops import transform
from sqlalchemy import and_, func, or_, text
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql import delete, select
from src import schemas
from src.core.opportunity import opportunity
from src.core.config import settings
from src.crud.base import CRUDBase
from src.core.heatmap.heatmap_compute import ComputeHeatmap
from src.db import models
from src.db.session import legacy_engine
from shapely import wkb
import shutil
import h3

from src.schemas.isochrone import (
    IsochroneDTO,
    IsochroneWalkingProfile,
    request_examples,
)

scenario_layer_models = {
    schemas.ScenarioLayersNoPoisEnum.way.value: models.Edge,
    schemas.ScenarioLayersNoPoisEnum.way_modified.value: models.WayModified,
    schemas.ScenarioLayersNoPoisEnum.building.value: models.Building,
    schemas.ScenarioLayersNoPoisEnum.building_modified.value: models.BuildingModified,
    schemas.ScenarioLayersNoPoisEnum.population.value: models.Population,
    schemas.ScenarioLayersNoPoisEnum.population_modified.value: models.PopulationModified,
    "poi": models.Poi,
    "poi_modified": models.PoiModified,
}

# TODO: Check if geometries are within study area
# TODO: Check geometry CRS


class CRUDScenario(CRUDBase[models.Scenario, schemas.ScenarioCreate, schemas.ScenarioUpdate]):
    async def read_scenario_features(
        self,
        db: AsyncSession,
        current_user: models.User,
        scenario_id: int,
        layer_name: str,
        intersect: str,
    ) -> Any:
        layer = scenario_layer_models[layer_name.value]

        if "_modified" not in layer_name.value and intersect is None:
            raise HTTPException(
                status_code=400, detail="Intersect parameter is required for non-modified layers"
            )

        polygon = None
        if intersect is not None:
            try:
                polygon = WKTElement(intersect, srid=4326)
                # Check if area of polygon is smaller than 10 km2
                project = pyproj.Transformer.from_crs(
                    pyproj.CRS("EPSG:4326"), pyproj.CRS("EPSG:3857"), always_xy=True
                ).transform
                projected_area = transform(project, to_shape(polygon)).area
                if (projected_area / 1000000) > 10:
                    raise HTTPException(
                        status_code=400,
                        detail="The area of the polygon is too large. Please select a smaller area.",
                    )
            except:
                raise HTTPException(status_code=400, detail="Invalid geometry")
        statement = select(layer)

        if layer_name.value == schemas.ScenarioLayersNoPoisEnum.way.value:
            excluded_ids_results = await db.execute(
                func.basic.select_customization("excluded_class_id_walking", current_user.active_study_area_id)
            )
            excluded_ids = excluded_ids_results.fetchall()
            excluded_ids_list = dict(excluded_ids[0])["select_customization_1"]

            excluded_foot_results = await db.execute(
                func.basic.select_customization("categories_no_foot", current_user.active_study_area_id)
            )
            excluded_foot = excluded_foot_results.fetchall()
            excluded_foot_list = dict(excluded_foot[0])["select_customization_1"]

            statement = statement.where(
                and_(
                    layer.class_id.notin_(excluded_ids_list),
                    or_(layer.foot.notin_(excluded_foot_list), layer.foot.is_(None)),
                    layer.geom.ST_Intersects(polygon),
                    layer.scenario_id is None,
                )
            )

        elif "_modified" in layer_name.value and intersect is None:
            statement = statement.where(layer.scenario_id == scenario_id)
        elif "_modified" in layer_name.value:
            statement = statement.where(
                and_(
                    layer.geom.ST_Intersects(polygon),
                    layer.scenario_id == scenario_id,
                )
            )

        else:
            statement = statement.where(layer.geom.ST_Intersects(polygon))

        result = await db.execute(statement)
        result = result.scalars().all()
        return result

    async def delete_scenario_features(
        self, db: AsyncSession, current_user: models.User, scenario_id: int, layer_name: str
    ) -> Any:
        layer = scenario_layer_models[layer_name.value]
        await db.execute(delete(layer).where(layer.scenario_id == scenario_id))
        await db.commit()
        scenario_dir = f"{settings.CACHE_PATH}/user/scenario/{scenario_id}"
        shutil.rmtree(scenario_dir, ignore_errors=True)
        return {"msg": "Features deleted successfully"}

    async def delete_scenario_feature(
        self,
        db: AsyncSession,
        current_user: models.User,
        scenario_id: int,
        layer_name: str,
        feature_ids: List[int],
    ) -> Any:
        layer = scenario_layer_models[layer_name.value]
        # check if feature exists in the table
        await db.execute(
            delete(layer).where(and_(layer.id.in_(feature_ids), layer.scenario_id == scenario_id))
        )
        await db.commit()
        if layer_name.value == schemas.ScenarioLayerFeatureEnum.population_modified.value:
            await db.execute(func.basic.population_modification(scenario_id))
            await db.commit()
        # Recalculate opportunity matrices for poi_modified and population_modified
        features_in_db = await db.execute(
            select(layer).where(and_(layer.scenario_id == scenario_id, layer.id.in_(feature_ids)))
        )
        features_in_db = features_in_db.scalars().fetchall()

        return {"msg": "Features deleted successfully"}

    async def create_scenario_features(
        self,
        db: AsyncSession,
        current_user: models.User,
        scenario_id: int,
        layer_name: str,
        feature_in: schemas.ScenarioFeatureCreate,
    ) -> Any:
        layer = scenario_layer_models[layer_name.value]
        features = feature_in.features
        features_in_db = []
        for feature in features:
            feature_dict = {}

            feature_dict["scenario_id"] = scenario_id

            # Check if population modified intersect with sub study area
            if layer_name.value == schemas.ScenarioLayerFeatureEnum.population_modified.value:
                point = WKTElement(feature.geom, srid=4326)
                statement = select(models.SubStudyArea).where(
                    and_(models.SubStudyArea.geom.ST_Intersects(point))
                )
                sub_study_area_result = await db.execute(statement)
                sub_study_area_result = sub_study_area_result.scalars().all()
                if len(sub_study_area_result) == 0:
                    raise HTTPException(
                        status_code=400,
                        detail="The population feature does not intersect with any sub study area",
                    )
                feature_dict["sub_study_area_id"] = sub_study_area_result[0].id
            try:
                for key, value in feature:
                    if (
                        key == "uid"
                        and layer_name.value == schemas.ScenarioLayerFeatureEnum.poi_modified.value
                    ):
                        if value is None:
                            # new POI
                            feature_dict["uid"] = uuid.uuid4().hex
                        else:
                            # existing POI
                            feature_dict["uid"] = value
                            splited_values = value.split("_")
                            if len(splited_values) >= 5:
                                feature_dict["data_upload_id"] = int(
                                    splited_values[-1].replace("u", "")
                                )

                            # TODO: check if uid is valid (poi / poi_user)
                    elif (
                        layer_name.value == schemas.ScenarioLayerFeatureEnum.way_modified.value
                        and key == "way_id"
                    ):
                        if value is not None:
                            feature_dict["way_id"] = value

                    # TODO: For population check if geometry and building with {building_modified_id} intersect

                    elif isinstance(value, enum.Enum):
                        feature_dict[key] = value.value
                    elif key == "class_id" and value is None:
                        feature_dict[key] = 100
                    elif value is None:
                        continue
                    else:
                        feature_dict[key] = value
                feature_obj = layer.from_orm(layer(**feature_dict))
                features_in_db.append(feature_obj)
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid feature")

        db.add_all(features_in_db)
        await db.commit()
        # Execute population distribution on population modified
        if layer_name.value in (
            schemas.ScenarioLayerFeatureEnum.building_modified.value,
            schemas.ScenarioLayerFeatureEnum.population_modified.value,
        ):
            await db.execute(func.basic.population_modification(scenario_id))
            await db.commit()

        for feature in features_in_db:
            await db.refresh(feature)

        # Recalculate opportunity matrices for poi_modified and population_modified
        if layer_name.value in ("poi_modified"):
            await self.compute_scenario_opportunity_matrices(
                scenario_id, layer_name.value.split("_")[0], features_in_db, current_user
            )

        return features_in_db

    async def update_scenario_features(
        self,
        db: AsyncSession,
        current_user: models.User,
        scenario_id: int,
        layer_name: str,
        feature_in: schemas.ScenarioFeatureUpdate,
    ) -> Any:
        layer = scenario_layer_models[layer_name.value]
        features = feature_in.features
        features_obj = {}
        feature_ids = []
        for feature in features:
            features_obj[feature.id] = {}
            feature_dict = {}
            # Check if population modified intersect with sub study area
            if layer_name.value == schemas.ScenarioLayerFeatureEnum.population_modified.value:
                point = WKTElement(feature.geom, srid=4326)
                statement = select(models.SubStudyArea).where(
                    and_(models.SubStudyArea.geom.ST_Intersects(point))
                )
                sub_study_area_result = await db.execute(statement)
                sub_study_area_result = sub_study_area_result.scalars().all()
                if len(sub_study_area_result) == 0:
                    raise HTTPException(
                        status_code=400,
                        detail="The population feature does not intersect with any sub study area",
                    )
                feature_dict["sub_study_area_id"] = sub_study_area_result[0].id
            try:
                for key, value in feature:
                    if key == "id":
                        feature_ids.append(value)
                        continue
                    elif isinstance(value, enum.Enum):
                        feature_dict[key] = value.value
                    else:
                        feature_dict[key] = value
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid feature")

            features_obj[feature.id] = feature_dict

        features_in_db = await db.execute(
            select(layer).where(and_(layer.scenario_id == scenario_id, layer.id.in_(feature_ids)))
        )
        features_in_db = features_in_db.scalars().fetchall()

        for db_feature in features_in_db:
            feature_id = db_feature.id
            for key, value in features_obj[feature_id].items():
                if value is not None:
                    # TODO: For population check if geometry and building with {building_modified_id} intersect
                    setattr(db_feature, key, value)

        db.add_all(features_in_db)
        await db.commit()

        # Execute population distribution on population modified
        if layer_name.value in (
            schemas.ScenarioLayerFeatureEnum.building_modified.value,
            schemas.ScenarioLayerFeatureEnum.population_modified.value,
        ):
            await db.execute(func.basic.population_modification(scenario_id))
            await db.commit()

        for feature in features_in_db:
            await db.refresh(feature)

        # Recalculate opportunity matrices for poi_modified and population_modified
        if layer_name.value in ("poi_modified"):
            await self.compute_scenario_opportunity_matrices(
                scenario_id, layer_name.value.split("_")[0], features_in_db, current_user
            )

        return features_in_db

    async def remove_multi_by_id_and_userid(
        self, db: AsyncSession, *, ids: List[int], user_id: int
    ) -> Any:
        statement = (
            delete(self.model).where(self.model.id.in_(ids)).where(self.model.user_id == user_id)
        )
        await db.execute(statement)
        await db.commit()
        if statement.is_delete is True:
            # Remove scenario cache
            for id in ids:
                scenario_dir = f"{settings.CACHE_PATH}/user/scenario/{id}"
                shutil.rmtree(scenario_dir, ignore_errors=True)
        else:
            raise HTTPException(status_code=400, detail="Invalid scenario id")

        return ids

    async def is_scenario_broken(self, db: AsyncSession, scenario_id: int) -> bool:
        # Cheking if any of the modified objects has a outdatad column set to true
        query = text(
            """SELECT EXISTS (SELECT 1 FROM customer.poi_modified pm WHERE outdated = true and pm.scenario_id=:scenario_id)
                        OR EXISTS (SELECT 1 FROM customer.way_modified wm WHERE outdated = true and wm.scenario_id=:scenario_id)
                        OR EXISTS (SELECT 1 FROM customer.building_modified bm WHERE outdated = true and bm.scenario_id=:scenario_id)
                        AS broken;"""
        )
        result = await db.execute(query, {"scenario_id": scenario_id})
        result = result.scalars().first()

        return bool(result)

    async def compute_scenario_opportunity_matrices(
        self, scenario_id: int, opportunity_type: str, features, user
    ) -> None:
        # ->
        s3_folder = ""
        crud_compute_heatmap = ComputeHeatmap(current_user=user)
        # todo: the isochrone settings can be dynamic in the future. Currently scenario is only for walking and 20 minutes, 5km/h
        isochrone_dto = IsochroneDTO(
            **request_examples["isochrone"]["single_walking_default"]["value"]
        )
        isochrone_dto.settings.travel_time = 20  # minutes
        isochrone_dto.settings.speed = 5  # km/h
        isochrone_dto.settings.walking_profile = IsochroneWalkingProfile.STANDARD
        isochrone_dto.output.resolution = 12
        # ->
        bulk_id_affected = []
        for feature in features:
            if feature.edit_type == "d":
                continue
            point_shape = wkb.loads(feature.geom.data)
            h3_id = h3.geo_to_h3(point_shape.y, point_shape.x, 6)
            bulk_id_affected.append(h3_id)

        bulk_id_affected = list(set(bulk_id_affected))

        for bulk_id in bulk_id_affected:
            bulk_geom = Polygon(h3.h3_to_geo_boundary(h=bulk_id, geo_json=True))
            opportunities_modified = opportunity.read_modified_data(
                db=legacy_engine,
                layer=opportunity_type,
                bbox_wkt=bulk_geom.wkt,
                scenario_id=scenario_id,
                edit_type=["n", "m"],
            )
            travel_time_matrices = await crud_compute_heatmap.read_travel_time_matrices(
                bulk_id=bulk_id, isochrone_dto=isochrone_dto, s3_folder=s3_folder
            )
            if len(opportunities_modified) == 0:
                return None
            await crud_compute_heatmap.compute_opportunity_matrix(
                bulk_id,
                isochrone_dto,
                opportunity_type,
                opportunities=opportunities_modified,
                travel_time_matrices=travel_time_matrices,
                output_path=f"{settings.CACHE_PATH}/user/scenario/{scenario_id}",
                s3_folder=s3_folder,
            )
        return bulk_id_affected


scenario = CRUDScenario(models.Scenario)
