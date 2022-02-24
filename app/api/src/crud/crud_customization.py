import asyncio

from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import and_

from src import crud, schemas
from src.crud.base import CRUDBase
from src.db import models
from src.db.models import user
from src.db.models.config_validation import *
from sqlalchemy.orm import Bundle, join 

from src.db.models.customization import Customization

class CRUDCustomization(
    CRUDBase[models.Customization, models.Customization, models.Customization]
):
    pass


class CRUDDynamicCustomization:

    def arr_dict_to_nested_dict(self, arr_dict):
        result = {}
        for group in arr_dict:
            group_key = list(group.keys())[0]
            categories = {}
            for category in group[group_key]['children']:
                categories.update(category)

            group[group_key]['children'] = categories
            result.update(group)
        return result

    def nested_dict_to_arr_dict(self, nested_dict):
        result = []
        for group_key in nested_dict:
            group = nested_dict[group_key]
            categories = []
            for category in group['children']:
                categories.append({category:group['children'][category]})
            
            group['children'] = categories
            result.append({group_key:group})
        return result

    def update_settings(self, old_setting, new_settings):
        new_groups = self.arr_dict_to_nested_dict(new_settings)

        for new_group in new_groups:
            if new_group  in old_setting:   
                for category in new_groups[new_group]['children']:
                    old_setting[new_group]['children'][category] = new_groups[new_group]['children'][category]
            else:
                old_setting[new_group] = new_groups[new_group]
        return old_setting

    async def build_main_setting_json(
        self, *, db: AsyncSession, current_user: models.User
    ):
        combined_settings = {}

        # Get default customization
        default_settings = {}
        default_customizations = await db.execute(select(models.Customization))
        default_customizations = default_customizations.all()

        if default_customizations is not None:
            [default_settings.update(i[0].default_setting) for i in default_customizations]

        # Get user customization
        user_settings = {}
        user_customizations = await db.execute(
            select(models.UserCustomization
        ).where(and_(models.UserCustomization.user_id == current_user.id, models.UserCustomization.study_area_id == current_user.active_study_area_id)))
        user_customizations = user_customizations.all()

        if user_customizations != []:
            [user_settings.update(i[0].setting) for i in user_customizations]

        # Get study area customization
        study_area_settings = {}
        study_area_customizations = await db.execute(select(models.StudyArea).where(models.StudyArea.id == current_user.active_study_area_id))
        study_area_customizations = study_area_customizations.all()

        if study_area_customizations != []:
            [study_area_settings.update(i[0].default_setting) for i in study_area_customizations]
                
        # Combine settings for pois and layers
        combined_groups = self.arr_dict_to_nested_dict(default_settings['poi_groups'])
        print('Combined POI groups:')
        if 'poi_groups' in study_area_settings:
            combined_groups = self.update_settings(combined_groups, study_area_settings['poi_groups'])

        if 'poi_groups' in user_settings:
            combined_groups = self.update_settings(combined_groups, user_settings['poi_groups'])

        combined_layer_groups = self.arr_dict_to_nested_dict(default_settings['layer_groups'])
        if 'layer_groups' in study_area_settings:
            combined_layer_groups = self.update_settings(combined_layer_groups, study_area_settings['layer_groups'])

        if 'layer_groups' in user_settings:
            combined_layer_groups = self.update_settings(combined_layer_groups, user_settings['layer_groups'])

        combined_settings['poi_groups'] = self.nested_dict_to_arr_dict(combined_groups)
        combined_settings['layer_groups'] = self.nested_dict_to_arr_dict(combined_layer_groups)

        # Add remaining settings 
        # Delete poi_groups and layer_groups from default_settings
        del default_settings['poi_groups']
        del default_settings['layer_groups']
        # Loop through default_settings and merge settings
        for setting_key in default_settings:
            combined_settings.update({setting_key: default_settings[setting_key]})
            if setting_key in user_settings:
                combined_settings.update({setting_key: user_settings[setting_key]})
            
            if setting_key in study_area_settings:
                combined_settings.update({setting_key: study_area_settings[setting_key]})

        return combined_settings


    async def update_settings(
        self, *, db: AsyncSession, current_user: models.User, new_settings, setting_type
    ):
        # Get user customization
        current_settings = {}

        # Get relevant user customization
        stmt = select(models.UserCustomization).join(Customization).where(and_(
            models.UserCustomization.user_id == current_user.id, 
            models.UserCustomization.study_area_id == current_user.active_study_area_id, 
            models.UserCustomization.customization_id == Customization.id,
            Customization.type == setting_type
            )
        )

        print(stmt)


        user_customizations = await db.execute(stmt)

        user_customizations = user_customizations.all()

        if user_customizations != []:
            [current_settings.update(i[0].setting) for i in user_customizations]






# from src.db.session import async_session


# test_user = models.User(
#     id=4,
#     active_study_area_id=1
# )

# poi_category = {"gym": {"icon": "fa-solid fa-dumbbell", "color": ["#985F03"]}}

# asyncio.run(CRUDDynamicCustomization().build_main_setting_json(db=async_session(), current_user=test_user))


#asyncio.run(CRUDDynamicCustomization().update_poi_settings(db=async_session(), current_user=test_user, poi_settings=poi_category))



customization = CRUDCustomization(models.Customization)
dynamic_customization = CRUDDynamicCustomization()



