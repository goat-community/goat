from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from geoalchemy2.shape import from_shape, to_shape
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import and_, delete, func, select

from src import crud
from src.crud.base import CRUDBase
from src.db import models
from src.db.models.config_validation import *
from src.db.models.customization import Customization
from src.utils import web_mercator_to_wgs84, wgs84_to_web_mercator


class CRUDCustomization(
    CRUDBase[models.Customization, models.Customization, models.Customization]
):
    pass


class CRUDUserCustomization(
    CRUDBase[models.UserCustomization, models.UserCustomization, models.UserCustomization]
):
    pass


customization = CRUDCustomization(models.Customization)
user_customization = CRUDUserCustomization(models.UserCustomization)


class CRUDDynamicCustomization:
    def layer_arr_to_dict(self, arr_dict):
        result = {}
        for elem in arr_dict:
            result.update(elem)
        return result

    async def build_layer_category_obj(self, db: AsyncSession, layer_name: str):
        """ "This function will build the layer category obj for a specific layer name"""
        layer = await crud.layer_library.get_by_multi_keys(
            db=db, keys={"name": layer_name}, extra_fields=[models.LayerLibrary.style_library]
        )
        if layer == []:
            HTTPException(status_code=400, detail="The layer %s does not exist." % layer_name)

        layer = layer[0]
        layer_attributes = {}
        for key in [
            "url",
            "legend_urls",
            "type",
            "map_attribution",
            "access_token",
            "max_resolution",
            "max_resolution",
            "doc_url"
        ]:
            if getattr(layer, key) is not None:
                layer_attributes[key] = getattr(layer, key)

        if layer.style_library is not None:
            if layer.style_library.style is not None:
                layer_attributes["style"] = layer.style_library.style
                if layer.style_library.translation is not None:
                    layer_attributes["translation"] = layer.style_library.translation

        if layer.date is not None and layer.source is not None:
            source_obj = {}
            source_obj["date"] = layer.date
            source_obj["source"] = layer.source

            if layer.date_1 is not None and layer.source_1 is not None:
                source_obj["date"] = source_obj["date"] + "," + layer.date_1
                source_obj["source"] = source_obj["source"] + "," + layer.source_1

            layer_attributes["attributes"] = source_obj

        if layer.type == "BING" and layer.special_attribute is not None:
            layer_attributes["imagery_set"] = layer.special_attribute["imagery_set"]

        layer_obj = {layer_name: layer_attributes}
        if check_dict_schema(LayerCategory, layer_obj) is False:
            HTTPException(
                status_code=400, detail="For %s the layer object is not valid." % layer_name
            )

        return layer_obj

    async def build_layer_group_obj(self, db: AsyncSession, list_groups, layer_group):
        """This function will build the layer group obj for a specific group"""
        layers = []
        group_name = list(layer_group.keys())[0]
        for category in layer_group[group_name]:
            category_obj = await self.build_layer_category_obj(db, category)
            layers.append(category_obj)

        group_obj = {group_name: {"icon": list_groups[group_name], "children": layers}}
        if check_dict_schema(LayerGroup, group_obj) is False:
            HTTPException(
                status_code=400, detail="For %s the group object is not valid." % group_name
            )
        return group_obj

    async def merge_layer_groups(
        self, db: AsyncSession, list_groups, default_groups, study_area_groups
    ):
        """This function will merge the default layer groups with the study area layer groups"""
        default_groups = self.layer_arr_to_dict(default_groups)
        study_area_groups = self.layer_arr_to_dict(study_area_groups)
        combined_group_objs = []

        for group in list_groups.keys():

            if group in default_groups.keys() and group in study_area_groups.keys():
                merge_groups = default_groups[group] + list(
                    set(study_area_groups[group]) - set(default_groups[group])
                )
            elif group in default_groups.keys():
                merge_groups = default_groups[group]
            elif group in study_area_groups.keys():
                merge_groups = study_area_groups[group]
            else:
                continue

            if merge_groups != []:
                group_obj = await self.build_layer_group_obj(
                    db, list_groups, {group: merge_groups}
                )
                combined_group_objs.append(group_obj)
            else:
                continue

        if check_dict_schema(LayerGroups, {"layer_groups": combined_group_objs}) is False:
            HTTPException(status_code=400, detail="The layer group object is not valid.")

        return combined_group_objs

    async def prepare_settings_dict(self, db: AsyncSession, sql_query):
        settings = await db.execute(sql_query)
        settings = settings.all()
        settings_dict = {}

        if settings is not None:
            for setting in settings:
                settings_dict.update(setting[0].setting)

        return settings_dict

    async def get_all_default_poi_categories(self, db: AsyncSession):
        """This will get a list of all default POI categories"""

        stmt = (
            select(models.OpportunityDefaultConfig.category)
            .join(models.OpportunityGroup)
            .where(
                and_(
                    models.OpportunityGroup.type == "poi",
                    models.OpportunityDefaultConfig.opportunity_group_id
                    == models.OpportunityGroup.id,
                )
            )
        )
        poi_categories = await db.execute(stmt)
        poi_categories = poi_categories.all()
        poi_categories = [category[0] for category in poi_categories]
        return poi_categories

    async def build_main_setting_json(self, *, db: AsyncSession, current_user: models.User):
        """This function builds the main setting json for one specific user."""
        combined_settings = {}

        # Get default customization
        default_settings = await self.prepare_settings_dict(db, select(models.Customization))

        # Get user customization
        sql_query = select(models.UserCustomization).where(
            and_(
                models.UserCustomization.user_id == current_user.id,
                models.UserCustomization.study_area_id == current_user.active_study_area_id,
            )
        )
        user_settings = await self.prepare_settings_dict(db, sql_query)

        # Get study area customization
        study_area_settings = await self.prepare_settings_dict(
            db,
            select(models.StudyArea).where(
                models.StudyArea.id == current_user.active_study_area_id
            ),
        )
        # Get active POI settings
        combined_poi_settings = await db.execute(
            func.basic.active_opportunities_json(
                "poi", current_user.id, current_user.active_study_area_id
            )
        )
        combined_poi_settings = combined_poi_settings.first()

        if check_dict_schema(PoiGroups, {"poi_groups": combined_poi_settings[0]}) is False:
            HTTPException(status_code=400, detail="Build POI groups are invalid.")

        combined_aoi_settings = await db.execute(
            func.basic.active_opportunities_json(
                "aoi", current_user.id, current_user.active_study_area_id
            )
        )
        combined_aoi_settings = combined_aoi_settings.first()

        if check_dict_schema(PoiGroups, {"aoi_groups": combined_aoi_settings[0]}) is False:
            HTTPException(status_code=400, detail="Build POI groups are invalid.")


        # Combine settings for layers
        combined_layer_groups = await self.merge_layer_groups(
            db,
            default_settings["app_ui"]["layer_tree"]["group_icons"],
            default_settings["layer_groups"],
            study_area_settings["layer_groups"],
        )


        # TODO: Manage other settings then layers and POIs
        # Loop through default_settings and merge settings
        for setting_key in default_settings:
            combined_settings.update({setting_key: default_settings[setting_key]})
            if setting_key in user_settings:
                combined_settings.update({setting_key: user_settings[setting_key]})

            if setting_key in study_area_settings:
                combined_settings.update({setting_key: study_area_settings[setting_key]})

        combined_settings["layer_groups"] = combined_layer_groups
        combined_settings["aoi_groups"] = combined_aoi_settings[0]
        combined_settings["poi_groups"] = combined_poi_settings[0]

        # Added geostores to settings
        study_area_obj = await crud.study_area.get(db, id=current_user.active_study_area_id, extra_fields=[models.StudyArea.geostores])
        combined_settings["geostores"] = jsonable_encoder(study_area_obj.geostores)

        # Remove transit modes that are not operating in study area from settings
        transit = {}
        for index_mode, mode in enumerate(combined_settings["routing"]):
            if mode["type"] == 'transit':
                transit = mode
                index_transit = index_mode
                break

        if transit != {}:
            filtered_transit_modes = []
            for transit_type in transit["transit_modes"]:
                # Check if station type is in study area buffer
                study_area_geom = to_shape(study_area_obj.geom)
                study_area_geom = wgs84_to_web_mercator(study_area_geom)
                study_area_geom = study_area_geom.buffer(60000)
                study_area_geom = web_mercator_to_wgs84(study_area_geom)
                study_area_geom = from_shape(study_area_geom, srid=4326)

                statement = select(models.Poi).where(
                    and_(
                        models.Poi.geom.ST_Intersects(study_area_geom),
                        models.Poi.category == transit_type["poi_category"],
                    )
                ).limit(1)
                result = await db.execute(statement)
                result = result.first()

                if result is not None:
                    filtered_transit_modes.append(transit_type)

            combined_settings["routing"][index_transit]["transit_modes"] = filtered_transit_modes

        return combined_settings

    async def insert_opportunity_setting(
        self,
        *,
        db: AsyncSession,
        current_user: models.User,
        insert_settings: dict,
        data_upload_id: int = None
    ):
        # Check if there is a default category
        category = list(insert_settings.keys())[0]
        existing_user_setting = await crud.opportunity_user_config.get_by_multi_keys(
            db=db, keys={"user_id": current_user.id, "category": category, "study_area_id": current_user.active_study_area_id}
        )

        if existing_user_setting == []:
            default_setting = await crud.opportunity_default_config.get_by_key(
                db=db, key="category", value=category
            )
            study_area_setting = await crud.opportunity_study_area_config.get_by_multi_keys(
                db=db, keys={"category": category, "study_area_id": current_user.active_study_area_id}
            )
            if default_setting != []:
                opportunity_group_id = default_setting[0].opportunity_group_id
            elif study_area_setting != []:
                opportunity_group_id = study_area_setting[0].opportunity_group_id
            else:
                opportunity_group_id = await crud.opportunity_group.get_by_key(
                    db=db, key="group", value="other"
                )
                opportunity_group_id = opportunity_group_id[0].id

            new_setting = models.OpportunityUserConfig(
                category=category,
                opportunity_group_id=opportunity_group_id,
                icon=insert_settings[category]["icon"],
                color=insert_settings[category]["color"],
                study_area_id=current_user.active_study_area_id,
                user_id=current_user.id,
                data_upload_id=data_upload_id,
            )
            await crud.opportunity_user_config.create(db=db, obj_in=new_setting)
        else:
            await crud.opportunity_user_config.update(
                db=db,
                db_obj=existing_user_setting[0],
                obj_in={
                    "icon": insert_settings[category]["icon"],
                    "color": insert_settings[category]["color"],
                },
            )

    async def delete_opportunity_setting(
        self, *, db: AsyncSession, current_user: models.User, setting_type: str, category: str
    ):
        await db.execute(
            delete(models.OpportunityUserConfig).where(
                and_(
                    models.OpportunityUserConfig.user_id == current_user.id,
                    models.OpportunityUserConfig.study_area_id == current_user.active_study_area_id,
                    models.OpportunityUserConfig.category == category
                )
            )
        )

        await db.commit()
        return {"msg": "Features deleted successfully"}

    async def get_user_settings(
        self, *, db: AsyncSession, current_user: models.User, setting_type
    ):
        """Get user settings for specific user and its active study area"""
        # Get relevant user customization
        query_user_customization = (
            select(models.UserCustomization)
            .join(Customization)
            .where(
                and_(
                    models.UserCustomization.user_id == current_user.id,
                    models.UserCustomization.study_area_id == current_user.active_study_area_id,
                    models.UserCustomization.customization_id == Customization.id,
                    Customization.type == setting_type,
                )
            )
        )

        user_customizations = await db.execute(query_user_customization)
        return user_customizations.first()

dynamic_customization = CRUDDynamicCustomization()
