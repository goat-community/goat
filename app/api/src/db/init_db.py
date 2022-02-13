import asyncio

import yaml
from rich import print
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src import crud, schemas
from src.core.config import settings
from src.db import models
from src.db.data_import import DataImport
from src.db.models import Base, organization  # noqa: F401
from src.db.session import async_session, staging_session
from src.crud.base import CRUDBase
from src.crud.crud_user import CRUDUser
from src.crud.crud_organization import CRUDOrganization
from src.crud.crud_role import CRUDRole
from src.core.config import Settings

# make sure all SQL Alchemy models are imported (src.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


async def init_db(db: AsyncSession) -> None:
    #Read settings
    settings_env = Settings() 

    with open("/app/customization.yaml", "r") as stream:
        default_settings = yaml.load(stream, Loader=yaml.FullLoader)
    
    #Check if tables are empty 
    role_exists = await crud.check_data.table_is_empty(db, models.Role)
    organization_exists = await crud.check_data.table_is_empty(db, models.Organization)
    user_exists = await crud.check_data.table_is_empty(db, models.User)
    customization_exists = await crud.check_data.table_is_empty(db, models.Customization)
 
    if role_exists == False and organization_exists == False and user_exists == False:
        for role in default_settings:
            role_obj = await db.execute(select(models.Role).filter(models.Role.name == role))
            role_obj = role_obj.scalars().first()
            if not role_obj:
                print(f"INFO: The role {role} does not exist in database. It will be created.")
                await crud.role.create(db, obj_in=models.Role(name=role))

        crud.organization.create(db, obj_in=models.Organization(name=settings_env.FIRST_ORGANIZATION))

        crud.user.create(db, obj_in=schemas.UserCreate(
            name=settings_env.FIRST_SUPERUSER,
            surname=settings_env.FIRST_SUPERUSER,
            email=settings_env.FIRST_SUPERUSER_EMAIL,
            password=settings_env.FIRST_SUPERUSER_PASSWORD,
            role=["superuser", "user"], #Get all roles
            organization_id=1, #Get Organization id 
            is_active=True
            )
        )

    if customization_exists == True:
        print("INFO: There is no default customization. The default customization will be loaded.")


        for setting in default_settings[role]:
            customization_create = schemas.customization.CustomizationCreate(
                role_id=role_obj.id,
                type=setting,
                default_setting={setting: default_settings[role][setting]},
            )
            await crud.customization.insert_default_customization(
                db, obj_in=customization_create
            )
            print(
                "INFO: Default setting of parameter [bold magenta]%s[/bold magenta] for [bold magenta]%s[/bold magenta] added."
                % (setting, role)
            )

        # imported_table = await DataImport().import_all_tables(db, staging_session())
        # user = await crud.user.create(db, obj_in=user_in)  # noqa: F841


asyncio.run(init_db(async_session()))
