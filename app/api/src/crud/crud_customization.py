from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import and_, func

from src import crud
from src.crud.base import CRUDBase
from src.db import models
from src.db.models.config_validation import *
from src.db.models.customization import Customization
from sqlalchemy.future import select

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
    def arr_dict_to_nested_dict(self, arr_dict):
        result = {}
        for group in arr_dict:
            group_key = list(group.keys())[0]
            categories = {}
            for category in group[group_key]["children"]:
                categories.update(category)

            group[group_key]["children"] = categories
            result.update(group)
        return result

    def nested_dict_to_arr_dict(self, nested_dict):
        result = []
        for group_key in nested_dict:
            group = nested_dict[group_key]
            categories = []
            for category in group["children"]:
                categories.append({category: group["children"][category]})

            group["children"] = categories
            result.append({group_key: group})
        return result

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
        ]:
            if getattr(layer, key) is not None:
                layer_attributes[key] = getattr(layer, key)

        if getattr(layer, "style_library") is not None:
            if getattr(layer.style_library, "style") is not None:
                layer_attributes["style"] = getattr(layer.style_library, "style")
                if getattr(layer.style_library, "translation") is not None:
                    layer_attributes["translation"] = getattr(layer.style_library, "translation")

        if getattr(layer, "date") is not None and getattr(layer, "source") is not None:
            source_obj = {}
            source_obj["date"] = getattr(layer, "date")
            source_obj["source"] = getattr(layer, "source")

            if getattr(layer, "date_1") is not None and getattr(layer, "source_1") is not None:
                source_obj["date"] = source_obj["date"] + "," + getattr(layer, "date_1")
                source_obj["source"] = source_obj["source"] + "," + getattr(layer, "source_1")

            layer_attributes["attributes"] = source_obj

        if getattr(layer, "type") == "BING" and getattr(layer, "special_attribute") is not None:
            layer_attributes["imagery_set"] = getattr(layer, "special_attribute")["imagery_set"]

        layer_obj = {layer_name: layer_attributes}
        if check_dict_schema(LayerCategory, layer_obj) == False:
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
        if check_dict_schema(LayerGroup, group_obj) == False:
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

        if check_dict_schema(LayerGroups, {"layer_groups": combined_group_objs}) == False:
            HTTPException(status_code=400, detail="The layer group object is not valid.")

        return combined_group_objs

    def update_settings(self, old_setting, insert_settings):
        new_groups = self.arr_dict_to_nested_dict(insert_settings)

        for new_group in new_groups:
            if new_group in old_setting:
                for category in new_groups[new_group]["children"]:
                    old_setting[new_group]["children"][category] = new_groups[new_group][
                        "children"
                    ][category]
            else:
                old_setting[new_group] = new_groups[new_group]
        return old_setting

    async def prepare_settings_dict(self, db: AsyncSession, sql_query):
        settings = await db.execute(sql_query)
        settings = settings.all()
        settings_dict = {}

        if settings is not None:
            for setting in settings:
                settings_dict.update(setting[0].setting)

        return settings_dict

    # async def get_all_default_poi_categories(self, db: AsyncSession):
    #     """This will get a list of all default POI categories"""

    #     stmt = (
    #         select(models.OpportunityDefaultConfig.category)
    #         .join(models.OpportunityGroup)
    #         .where(
    #             and_(
    #                 models.OpportunityGroup.type == 'poi',
    #                 models.OpportunityDefaultConfig.group == models.OpportunityGroup.group
    #             )
    #         )
    #     )
    #     print(stmt)
    #     poi_categories = await db.execute(stmt)
    #     poi_categories = poi_categories.all()
    #     return poi_categories

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
            func.basic.active_opportunities_json('poi', current_user.id, current_user.active_study_area_id)
        )
        combined_poi_settings = combined_poi_settings.first()
        

        if check_dict_schema(PoiGroups, {"poi_groups": combined_poi_settings[0]}) == False:
            HTTPException(
                status_code=400, detail="Build POI groups are invalid." 
            )
        combined_settings["poi_groups"] = combined_poi_settings[0]
        
        combined_aoi_settings = await db.execute(
            func.basic.active_opportunities_json('aoi', current_user.id, current_user.active_study_area_id)
        )
        combined_aoi_settings = combined_aoi_settings.first()

        if check_dict_schema(PoiGroups, {"aoi_groups": combined_aoi_settings[0]}) == False:
            HTTPException(
                status_code=400, detail="Build POI groups are invalid." 
            )
        combined_settings["aoi_groups"] = combined_aoi_settings[0]

        # Combine settings for layers
        combined_layer_groups = await self.merge_layer_groups(
            db,
            default_settings["app_ui"]["layer_tree"]["group_icons"],
            default_settings["layer_groups"],
            study_area_settings["layer_groups"],
        )
        combined_settings["layer_groups"] = combined_layer_groups

        # Loop through default_settings and merge settings
        for setting_key in default_settings:
            combined_settings.update({setting_key: default_settings[setting_key]})
            if setting_key in user_settings:
                combined_settings.update({setting_key: user_settings[setting_key]})

            if setting_key in study_area_settings:
                combined_settings.update({setting_key: study_area_settings[setting_key]})

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
        existing_user_setting = await crud.opportunity_user_config.get_by_key(
            db=db, key="category", value=category
        )

        if existing_user_setting == []:
            default_setting = await crud.opportunity_default_config.get_by_key(
                db=db, key="category", value=category
            )

            group = default_setting[0].dict().get("group", "other")
            new_setting = models.OpportunityUserConfig(
                category=category,
                group=group,
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
                obj_in={"icon": insert_settings[category]["icon"], "color": insert_settings[category]["color"]},
            )

    async def delete_opportunity_setting(
        self,
        *,
        db: AsyncSession,
        current_user: models.User,
        category: dict
    ):
        x=1

    async def delete_user_settings(
        self,
        *,
        db: AsyncSession,
        current_user: models.User,
        user_customizations,
        setting_to_delete,
        setting_type
    ):
        """This function deletes the user generated settings for a specific POI category."""
        settings_to_update = self.arr_dict_to_nested_dict(
            user_customizations[0].setting[setting_type]
        )

        for group in settings_to_update:
            for category in settings_to_update[group]["children"]:
                if category == setting_to_delete:
                    settings_to_update[group]["children"].pop(category)
                    break

        if settings_to_update[group]["children"] == {}:
            del settings_to_update[group]

        settings_to_update = {setting_type: self.nested_dict_to_arr_dict(settings_to_update)}

        if (
            check_dict_schema(LayerGroups, settings_to_update) == True
            or check_dict_schema(PoiGroups, settings_to_update) == True
        ):
            await db.execute(
                update(models.UserCustomization)
                .where(models.UserCustomization.id == user_customizations[0].id)
                .values(setting=settings_to_update)
            )
        else:
            raise HTTPException(status_code=400, detail="Failed deleting user settings.")

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

    async def handle_user_setting_modification(
        self,
        *,
        db: AsyncSession,
        current_user: models.User,
        changeset,
        setting_type,
        modification_type
    ):
        # This line needs to be adjdusted
        setting_type = {"poi": "poi_groups"}[setting_type]
        """ "This function handles insert or updates of settings for POIs and Layers."""
        user_customizations = await self.get_user_settings(
            db=db, current_user=current_user, setting_type=setting_type
        )

        default_setting = await customization.get_by_key(db, key="type", value=setting_type)
        default_setting_obj = default_setting[0]

        study_area_setting = await crud.study_area.get_by_key(
            db, key="id", value=current_user.active_study_area_id
        )
        study_area_setting_obj = study_area_setting[0]

        # If user customization exists, update it
        if modification_type == "insert" and user_customizations is not None:
            insert_opportunity_setting

            
        elif modification_type == "delete" and user_customizations is not None:
            await self.delete_user_settings(
                db=db,
                current_user=current_user,
                user_customizations=user_customizations,
                setting_to_delete=changeset,
                setting_type=setting_type,
            )
            await db.commit()
        else:
            raise HTTPException(status_code=400, detail="Invalid modification type.")


# from src.db.session import async_session

# test_user = models.User(id=4, active_study_area_id=1)

# poi_category = {"nursery": {"icon": "fa-solid fa-dumbbell", "color": ["TestTest"]}}

# poi_category = {"This is new": {"icon": "fa-solid fa-dumbbell", "color": ["New Color"]}}


# layer_style = {
#     "accidents_accidents_cyclists": {
#         "name": "accidents_pedestrians",
#         "rules": [
#             {
#                 "name": "sssssssssssssssss",
#                 "symbolizers": [
#                     {"kind": "Mark", "color": "#ff9900", "radius": 3, "wellKnownName": "Square"}
#                 ],
#             }
#         ],
#     }
# }

# layer_style = {
#     "accidents_pedestrians": {
#         "name": "accidents_pedestrians",
#         "rules": [
#             {
#                 "name": "sssssssssssssssss",
#                 "symbolizers": [
#                     {"kind": "Mark", "color": "#ff9900", "radius": 3, "wellKnownName": "Square"}
#                 ],
#             }
#         ],
#     }
# }


# asyncio.run(CRUDDynamicCustomization().build_main_setting_json(db=async_session(), current_user=test_user))

# db = async_session()
# asyncio.run(
#     CRUDDynamicCustomization().handle_user_setting_modification(
#         db=db,
#         current_user=test_user,
#         changeset="accidents_pedestrians",
#         setting_type="layer",
#         modification_type="delete",
#     )
# )
# #asyncio.run(db.close())

# x = asyncio.run(db.execute(select(models.Customization)))
# y = x.all()

dynamic_customization = CRUDDynamicCustomization()
