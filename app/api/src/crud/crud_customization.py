from fastapi import HTTPException
from sqlalchemy import  update
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import and_

from src import crud
from src.crud.base import CRUDBase
from src.db import models
from src.db.models.config_validation import *
from src.db.models.customization import Customization


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

    async def get_all_default_poi_categories(self, db: AsyncSession):
        """This will get a list of all default POI categories"""
        poi_categories = []
        default_setting = await customization.get_by_key(db, key="type", value='poi_groups')
        default_setting_obj = default_setting[0]

        for group in default_setting_obj.setting["poi_groups"]:
            for category in group[list(group.keys())[0]]['children']:
                poi_categories.append(list(category.keys())[0])
        
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

        # Combine settings for pois and layers
        combined_groups = self.arr_dict_to_nested_dict(default_settings["poi_groups"])
        if "poi_groups" in study_area_settings:
            combined_groups = self.update_settings(
                combined_groups, study_area_settings["poi_groups"]
            )

        if "poi_groups" in user_settings and current_user.active_data_upload_ids != []:
            active_categories = []   
            for active_id in current_user.active_data_upload_ids:      
                active_category = await db.execute(
                    select(models.PoiUser).where(models.PoiUser.data_upload_id == active_id).limit(1)
                )
                active_category = active_category.all()
                active_categories.append(active_category[0][0].category)

            for group_id, poi_group in enumerate(user_settings["poi_groups"]):
                group_name = next(iter(poi_group))
                for category_id, poi_category in enumerate(poi_group[group_name]["children"]):
                    category_name = next(iter(poi_category))
                    if category_name not in active_categories:
                        active_categories.append(category_id)
                        user_settings['poi_groups'][group_id][group_name]["children"].pop(category_id)
                        break
            
        if "poi_groups" in user_settings:
            combined_groups = self.update_settings(combined_groups, user_settings["poi_groups"])
         
        combined_layer_groups = self.arr_dict_to_nested_dict(default_settings["layer_groups"])
        if "layer_groups" in study_area_settings:
            combined_layer_groups = self.update_settings(
                combined_layer_groups, study_area_settings["layer_groups"]
            )

        if "layer_groups" in user_settings:
            combined_layer_groups = self.update_settings(
                combined_layer_groups, user_settings["layer_groups"]
            )

        combined_settings["poi_groups"] = self.nested_dict_to_arr_dict(combined_groups)
        combined_settings["layer_groups"] = self.nested_dict_to_arr_dict(combined_layer_groups)

        # Add remaining settings
        # Delete poi_groups and layer_groups from default_settings
        del default_settings["poi_groups"]
        del default_settings["layer_groups"]
        # Loop through default_settings and merge settings
        for setting_key in default_settings:
            combined_settings.update({setting_key: default_settings[setting_key]})
            if setting_key in user_settings:
                combined_settings.update({setting_key: user_settings[setting_key]})

            if setting_key in study_area_settings:
                combined_settings.update({setting_key: study_area_settings[setting_key]})
        
        return combined_settings

    async def insert_user_setting(
        self,
        *,
        db: AsyncSession,
        current_user: models.User,
        default_setting_obj,
        study_area_setting_obj,
        insert_settings,
        setting_type
    ):
        """This function inserts user settings if no user settings exists for the setting type."""
        if setting_type == "poi_groups":
            insert_poi_setting = None
            poi_setting_to_update = self.arr_dict_to_nested_dict(
                default_setting_obj.setting["poi_groups"]
            )
            insert_poi_category = list(insert_settings.keys())[0]

            # Check if POI user customization is for an existing POI category
            for poi_group in poi_setting_to_update:
                if (
                    poi_setting_to_update.get(poi_group).get("children").get(insert_poi_category)
                    != None
                ):

                    insert_poi_setting = {poi_group: poi_setting_to_update[poi_group]}
                    poi_setting_to_update[poi_group]["children"] = insert_settings
                    break

            # If POI category is not found assign "Other" as POI category
            if insert_poi_setting is None:
                insert_poi_setting = OtherPoiGroupDummy
                insert_poi_setting["other"]["children"] = {
                    insert_poi_category: insert_settings[insert_poi_category]
                }

            insert_poi_setting = {"poi_groups": self.nested_dict_to_arr_dict(insert_poi_setting)}

            if check_dict_schema(PoiGroups, insert_poi_setting) == True:
                # Update POI user customization
                new_obj = models.UserCustomization(
                    user_id=current_user.id,
                    study_area_id=current_user.active_study_area_id,
                    customization_id=default_setting_obj.id,
                    setting=insert_poi_setting,
                )
                await user_customization.create(db=db, obj_in=new_obj)
            else:
                raise HTTPException(status_code=400, detail="Failed Inserting poi customization.")

        # Handler layer group settings
        elif setting_type == "layer_groups":
            insert_layer_setting = None
            existing_layer_settings = self.arr_dict_to_nested_dict(
                study_area_setting_obj.setting["layer_groups"]
            )
            insert_layer_category = list(insert_settings.keys())[0]

            for layer_group in existing_layer_settings:
                if (
                    existing_layer_settings.get(layer_group)
                    .get("children")
                    .get(insert_layer_category)
                    != None
                ):
                    insert_layer_setting = {
                        layer_group: {
                            "icon": existing_layer_settings[layer_group]["icon"],
                            "children": {
                                insert_layer_category: existing_layer_settings[layer_group][
                                    "children"
                                ][insert_layer_category]
                            },
                        }
                    }

                    insert_layer_setting[layer_group]["children"][insert_layer_category][
                        "style"
                    ] = insert_settings[insert_layer_category]
                    break

            # Check if an existing layer was found for the style
            if insert_layer_setting is None:
                return HTTPException(
                    status_code=400, detail="You passed a style for an unknown layer."
                )

            insert_layer_setting = {
                "layer_groups": self.nested_dict_to_arr_dict(insert_layer_setting)
            }

            if check_dict_schema(LayerGroups, insert_layer_setting) == True:
                # Insert layer with user generated customization
                new_obj = models.UserCustomization(
                    user_id=current_user.id,
                    study_area_id=current_user.active_study_area_id,
                    customization_id=default_setting_obj.id,
                    setting=insert_layer_setting,
                )
                await user_customization.create(db=db, obj_in=new_obj)
            else:
                raise HTTPException(status_code=400, detail="Failed Inserting layer style.")

    async def update_user_setting(
        self,
        *,
        db: AsyncSession,
        current_user: models.User,
        default_setting_obj,
        study_area_setting_obj,
        insert_settings,
        user_customizations,
        setting_type
    ):
        """This function updates the user customization for a specific setting type if the setting exists in user_customization."""
        setting_obj = user_customizations[0]
        user_settings = setting_obj.setting

        if setting_type == "poi_groups":
            poi_default_setting = self.arr_dict_to_nested_dict(
                default_setting_obj.setting["poi_groups"]
            )
            update_status = False
            poi_setting_to_update = self.arr_dict_to_nested_dict(user_settings["poi_groups"])
            update_poi_category = list(insert_settings.keys())[0]

            # Check if POI user customization is for an existing POI category
            for poi_group in poi_default_setting:
                if (
                    poi_default_setting.get(poi_group).get("children").get(update_poi_category)
                    != None
                ):
                    if poi_group in poi_setting_to_update:
                        poi_setting_to_update[poi_group]["children"][
                            update_poi_category
                        ] = insert_settings[update_poi_category]
                    else:
                        placeholder_setting = poi_default_setting[poi_group]
                        placeholder_setting["children"] = insert_settings
                        poi_setting_to_update[poi_group] = placeholder_setting

                    update_status = True

            # Check if POI user customization is for an existing USER-POI category
            if update_status == False:
                for poi_group in poi_setting_to_update:
                    if (
                        poi_setting_to_update.get(poi_group)
                        .get("children")
                        .get(update_poi_category)
                        != None
                    ):
                        poi_setting_to_update[poi_group]["children"][
                            update_poi_category
                        ] = insert_settings[update_poi_category]
                        update_status = True

            # If POI category is not found assign "Other" as POI category and append to existing POI categories
            if update_status == False:
                # Other category already exists
                if "other" in poi_setting_to_update:
                    poi_setting_to_update["other"]["children"][
                        update_poi_category
                    ] = insert_settings[update_poi_category]
                # Other category does not exist
                else:
                    update_poi_setting = OtherPoiGroupDummy
                    update_poi_setting["other"]["children"] = insert_settings
                    poi_setting_to_update.update(update_poi_setting)

            poi_setting_to_update = {
                "poi_groups": self.nested_dict_to_arr_dict(poi_setting_to_update)
            }

            # Check if schema is valid and update user customization
            if check_dict_schema(PoiGroups, poi_setting_to_update) == True:
                await db.execute(
                    update(models.UserCustomization)
                    .where(models.UserCustomization.id == setting_obj.id)
                    .values(setting=poi_setting_to_update)
                )
            else:
                raise HTTPException(status_code=400, detail="Failed updating POIs settings.")

        elif setting_type == "layer_groups":
            layer_setting_to_update = self.arr_dict_to_nested_dict(user_settings["layer_groups"])
            update_layer_category = list(insert_settings.keys())[0]
            update_status = False

            # Update existing layer 
            for layer_group in layer_setting_to_update:
                if (
                    layer_setting_to_update.get(layer_group)
                    .get("children")
                    .get(update_layer_category)
                    != None
                ):
                    layer_setting_to_update[layer_group]["children"][update_layer_category][
                        "style"
                    ] = insert_settings[update_layer_category]
                    update_status = True
                    break

            # Add new layer to existing layer object
            if update_status == False:
                layer_default_setting = self.arr_dict_to_nested_dict(
                    study_area_setting_obj.setting["layer_groups"]
                )
                for layer_group in layer_default_setting:
                    # If layer group is not yet in user customization
                    if (
                        layer_default_setting.get(layer_group)
                        .get("children")
                        .get(update_layer_category)
                        != None
                        and 
                        layer_group not in layer_setting_to_update
                    ):

                        layer_to_insert = layer_default_setting[layer_group]["children"][update_layer_category]
                        layer_group_to_insert = {layer_group:layer_default_setting[layer_group]}
                        layer_group_to_insert[layer_group]["children"].clear()
                        layer_group_to_insert[layer_group]["children"].update(
                            {update_layer_category: layer_to_insert}
                        )

                        layer_group_to_insert[layer_group]["children"][update_layer_category][
                            "style"
                        ] = insert_settings[update_layer_category]

                        layer_setting_to_update.update(layer_group_to_insert)
                        update_status = True
                        break
                    
                    # If layer group is already in user customization
                    elif(
                        layer_default_setting.get(layer_group)
                        .get("children")
                        .get(update_layer_category)
                        != None
                        and 
                        layer_group in layer_setting_to_update
                    ):
                        layer_to_insert = layer_default_setting[layer_group]["children"][update_layer_category]
                        layer_setting_to_update[layer_group]["children"][update_layer_category] = layer_to_insert
                        layer_setting_to_update[layer_group]["children"][update_layer_category]["style"] = insert_settings[update_layer_category]
                        update_status = True
                        break 

            layer_setting_to_update = {
                "layer_groups": self.nested_dict_to_arr_dict(layer_setting_to_update)
            }

            if check_dict_schema(LayerGroups, layer_setting_to_update) == True:
                await db.execute(
                    update(models.UserCustomization)
                    .where(models.UserCustomization.id == setting_obj.id)
                    .values(setting=layer_setting_to_update)
                )
            else:
                raise HTTPException(status_code=400, detail="Failed updating layer settings.")

    async def delete_user_settings(
        self, *, db: AsyncSession, current_user: models.User, user_customizations, setting_to_delete, setting_type
    ):
        """This function deletes user settings. It can also be used to reset to original settings."""
        

        settings_to_update = self.arr_dict_to_nested_dict(user_customizations[0].setting[setting_type])

        for group in settings_to_update:
            for category in settings_to_update[group]["children"]:
                if category == setting_to_delete:
                    settings_to_update[group]["children"].pop(category)
                    break
        
        if settings_to_update[group]['children'] == {}:
            del settings_to_update[group]

        settings_to_update = {
            setting_type: self.nested_dict_to_arr_dict(settings_to_update)
        }
            
        if check_dict_schema(LayerGroups, settings_to_update) == True or check_dict_schema(PoiGroups, settings_to_update) == True:
            await db.execute(
                    update(models.UserCustomization)
                    .where(models.UserCustomization.id == user_customizations[0].id)
                    .values(setting=settings_to_update)
                )
        else:
            raise HTTPException(status_code=400, detail="Failed deleting user settings.")
    
    async def get_user_settings(self, *, db: AsyncSession, current_user: models.User, setting_type):
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
        self, *, db: AsyncSession, current_user: models.User, changeset, setting_type, modification_type
    ):
        """"This function handles insert or updates of settings for POIs and Layers."""

        setting_type = mapping_setting_type[setting_type]
        user_customizations = await self.get_user_settings(db=db, current_user=current_user, setting_type=setting_type)

        default_setting = await customization.get_by_key(db, key="type", value=setting_type)
        default_setting_obj = default_setting[0]

        study_area_setting = await crud.study_area.get_by_key(db, key="id", value=current_user.active_study_area_id)
        study_area_setting_obj = study_area_setting[0]

        # If user customization exists, update it
        if modification_type == 'insert' and user_customizations is not None:
            await self.update_user_setting(
                db=db,
                current_user=current_user,
                default_setting_obj=default_setting_obj,
                study_area_setting_obj=study_area_setting_obj,  
                insert_settings=changeset,
                user_customizations=user_customizations,
                setting_type=setting_type,
            )
            await db.commit()
        elif modification_type == 'insert' and user_customizations is None:
            await self.insert_user_setting(
                db=db,
                current_user=current_user,
                default_setting_obj=default_setting_obj,
                study_area_setting_obj=study_area_setting_obj,
                insert_settings=changeset,
                setting_type=setting_type,
            )
            await db.commit()
        elif modification_type == 'delete' and user_customizations is not None:
            await self.delete_user_settings(
                db=db,
                current_user=current_user,
                user_customizations=user_customizations,
                setting_to_delete=changeset,
                setting_type=setting_type
            )
            await db.commit()
        else:
            raise HTTPException(status_code=400, detail="Invalid modification type.")

#from src.db.session import async_session

#test_user = models.User(id=4, active_study_area_id=1)

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
