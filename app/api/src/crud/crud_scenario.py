import enum
import uuid
from typing import Any, List

import pyproj
from fastapi import HTTPException
from geoalchemy2.shape import WKTElement, to_shape
from shapely import wkt
from shapely.ops import transform
from sqlalchemy import and_, func
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql import delete, select

from src import schemas
from src.crud.base import CRUDBase
from src.db import models

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
                func.basic.select_customization("excluded_class_id_walking")
            )
            excluded_ids = excluded_ids_results.fetchall()
            excluded_ids_list = dict(excluded_ids[0])["select_customization_1"]
            statement = statement.where(
                and_(
                    layer.class_id.notin_(excluded_ids_list),
                    layer.geom.ST_Intersects(polygon),
                    layer.scenario_id == None,
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
            await db.execute(
                func.basic.population_modification(scenario_id)
            )
            await db.commit()
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
            except Exception as e:
                raise HTTPException(status_code=400, detail="Invalid feature")

        db.add_all(features_in_db)
        await db.commit()
        # Execute population distribution on population modified
        if layer_name.value in (schemas.ScenarioLayerFeatureEnum.building_modified.value, schemas.ScenarioLayerFeatureEnum.population_modified.value):
            await db.execute(
                func.basic.population_modification(scenario_id)
            )
            await db.commit()

        for feature in features_in_db:
            await db.refresh(feature)
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
            except Exception as e:
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
        if layer_name.value in (schemas.ScenarioLayerFeatureEnum.building_modified.value, schemas.ScenarioLayerFeatureEnum.population_modified.value):
            await db.execute(
                func.basic.population_modification(scenario_id)
            )
            await db.commit()

        for feature in features_in_db:
            await db.refresh(feature)
        
        return features_in_db

scenario = CRUDScenario(models.Scenario)
