import yaml
from rich import print
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src import crud, schemas
from src.core.config import settings
from src.db import models
from src.db.data_import import DataImport
from src.db.models import Base  # noqa: F401
from src.db.session import staging_session
from src.db.session import async_session
import asyncio 
# make sure all SQL Alchemy models are imported (src.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


async def init_db(db: AsyncSession) -> None:
    customization = await crud.check_data.table_is_empty(db, models.Customization)
    
    if customization == True:
        print('INFO: There is no default customization. The default customization will be loaded.')

    if customization == True:
        print("INFO: There is no default customization. The default customization will be loaded.")

        with open("/app/customization.yaml", "r") as stream:
            default_settings = yaml.load(stream, Loader=yaml.FullLoader)

        for role in default_settings:
            role_obj = await crud.user.create_role(db, name=role)
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