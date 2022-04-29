import asyncio

import yaml
from rich import print
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src import crud, schemas
from src.core.config import Settings, settings
from src.db import models
from src.db.session import async_session


class ConfigSeeding:
    def __init__(self):
        # TODO: Validate settings
        with open("/app/customization.yaml", "r") as stream:
            self.default_settings = yaml.load(stream, Loader=yaml.FullLoader)
        self.settings_env = Settings()

    async def create_first_user(self, db: AsyncSession):
        """Creates the first user in the database."""
        # Check if tables are empty

        organization_obj = await crud.organization.get_by_key(db, key="name", value=self.settings_env.FIRST_ORGANIZATION)
        user_exists = await crud.user.get_n_rows(db, n=1)

        if organization_obj == []:
            # Create default organization
            organization_obj = await crud.organization.create(
                db, obj_in=models.Organization(name=self.settings_env.FIRST_ORGANIZATION)
            )
      
        # Create roles if not exists
        for role in self.default_settings:
            role_obj = await db.execute(select(models.Role).filter(models.Role.name == role))
            role_obj = role_obj.scalars().first()
            if not role_obj:
                print(f"INFO: The role {role} does not exist in database. It will be created.")
                role_obj = await crud.role.create(db, obj_in=models.Role(name=role))

        # Get all available roles
        role_objs = await crud.role.get_all(db)
 
        # Get all availavle study areas
        study_area_objs = await crud.study_area.get_all(db)

        if user_exists == []:
            # Create first user
            new_user = await crud.user.create(
                db,
                obj_in=schemas.UserCreate(
                    name=self.settings_env.FIRST_SUPERUSER_NAME,
                    surname=self.settings_env.FIRST_SUPERUSER_SURNAME,
                    email=self.settings_env.FIRST_SUPERUSER_EMAIL,
                    password=self.settings_env.FIRST_SUPERUSER_PASSWORD,
                    roles=[role.name for role in role_objs],
                    study_areas=[study_area.id for study_area in study_area_objs],
                    organization_id=organization_obj[0].id,
                    storage=self.settings_env.FIRST_SUPERUSER_STORAGE,
                    active_study_area_id=self.settings_env.FIRST_SUPERUSER_ACTIVE_STUDY_AREA_ID,
                    active_data_upload_ids=self.settings_env.FIRST_SUPERUSER_ACTIVE_DATA_UPLOAD_IDS,
                    limit_scenarios=self.settings_env.FIRST_SUPERUSER_LIMIT_SCENARIOS,
                    language_preference=self.settings_env.FIRST_SUPERUSER_LANGUAGE_PREFERENCE,
                    is_active=True
                )
            )
            print(f"INFO: First superuser was successfully created.")
        else:
            print(f"INFO: The first superuser will not be created.")

    async def sync_base_customization(self, db: AsyncSession):
        """Inserts customization settings into database."""
        default_opportunity_settings = self.default_settings["user"]["opportunity"]

        other_settings = self.default_settings
        other_settings["user"].pop("opportunity")

        for role in other_settings:
            role_obj = await db.execute(select(models.Role).filter(models.Role.name == role))
            role_obj = role_obj.scalars().first()
            for setting in other_settings[role]:
                existing_setting = await crud.customization.get_by_key(
                    db, key="type", value=setting
                )
                new_setting = models.Customization(
                    role_id=role_obj.id,
                    type=setting,
                    setting={setting: self.default_settings[role][setting]},
                )
                # Check if setting already exists in database
                if existing_setting == []:
                    await crud.customization.create(db, obj_in=new_setting)
                    print(
                        "INFO: Default setting of parameter [bold magenta]%s[/bold magenta] for [bold magenta]%s[/bold magenta] added."
                        % (setting, role)
                    )
                else:
                    await crud.customization.update(
                        db, db_obj=existing_setting[0], obj_in=new_setting.dict(exclude={"id"})
                    )
                    print(
                        "INFO: Default setting of parameter [bold magenta]%s[/bold magenta] for [bold magenta]%s[/bold magenta] will be updated."
                        % (setting, role)
                    )

        for opportunity in default_opportunity_settings:
            for group in default_opportunity_settings[opportunity]:
                group_dict = default_opportunity_settings[opportunity][group]

                existing_group = await crud.opportunity_group.get_by_key(
                    db, key="group", value=group
                )

                group_obj = models.OpportunityGroup(
                    type=opportunity,
                    group=group,
                    icon=group_dict["icon"],
                    color=group_dict["color"],
                )
                if existing_group == []:
                    new_group = await crud.opportunity_group.create(db=db, obj_in=group_obj)
                    print(
                        "\nINFO: Opportunity group [bold magenta]%s[/bold magenta] added."
                        % (group)
                    )
                else:
                    new_group = await crud.opportunity_group.update(db=db, db_obj=existing_group[0], obj_in=group_obj.dict(exclude={"id"}))
                    print(
                        "\nINFO: Opportunity group [bold magenta]%s[/bold magenta] updated."
                        % (group)
                    )

                group_id = new_group.id
                # If POI group has no children continue
                if group_dict['children'] == None:
                    continue

                for category in group_dict['children']:
                    category_dict = group_dict['children'][category]
                    existing_setting = await crud.opportunity_default_config.get_by_key(
                        db, key="category", value=category
                    )
                    setting_obj = models.OpportunityDefaultConfig(
                        category=category,
                        opportunity_group_id=group_id,
                        icon=category_dict["icon"],
                        color=category_dict["color"],
                        sensitivity=category_dict.get("sensitivity"),
                        multiple_entrance=category_dict.get("multiple_entrance")
                    )
                    if existing_setting == []:
                        await crud.opportunity_default_config.create(db=db, obj_in=setting_obj)
                        print(
                            "INFO: Default setting for the opportunity category [bold magenta]%s[/bold magenta] for the group [bold magenta]%s[/bold magenta] added."
                            % (category, group)
                        )
                    else:
                        await crud.opportunity_default_config.update(
                            db=db,
                            db_obj=existing_setting[0],
                            obj_in=setting_obj.dict(exclude={"id"}),
                        )
                        print(
                            "INFO: Default setting for the opportunity category [bold magenta]%s[/bold magenta] for the group [bold magenta]%s[/bold magenta] updated."
                            % (category, group)
                        )


def main():
    from src.db.session import async_session

    db = async_session()
    config_seeding = ConfigSeeding()

    asyncio.get_event_loop().run_until_complete(config_seeding.create_first_user(db))
    asyncio.get_event_loop().run_until_complete(config_seeding.sync_base_customization(db))
    asyncio.get_event_loop().run_until_complete(db.close())


main()
