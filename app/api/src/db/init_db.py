import yaml
from rich import print
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src import crud, schemas
from src.core.config import settings
from src.db import models
from src.db.session import async_session, staging_session
from src.core.config import Settings


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
        #Create roles
        for role in default_settings:
            role_obj = await db.execute(select(models.Role).filter(models.Role.name == role))
            role_obj = role_obj.scalars().first()
            if not role_obj:
                print(f"INFO: The role {role} does not exist in database. It will be created.")
                await crud.role.create(db, obj_in=models.Role(name=role))
        
        #Create default organization
        organization_obj = await crud.organization.create(db, obj_in=models.Organization(name=settings_env.FIRST_ORGANIZATION))

        #Create first user
        await crud.user.create(db, obj_in=schemas.UserCreate(
                name=settings_env.FIRST_SUPERUSER_NAME,
                surname=settings_env.FIRST_SUPERUSER_SURNAME,
                email=settings_env.FIRST_SUPERUSER_EMAIL,
                password=settings_env.FIRST_SUPERUSER_PASSWORD,
                role=list(default_settings.keys()), 
                organization_id=organization_obj.id, 
                storage=settings_env.FIRST_SUPERUSER_STORAGE,
                is_active=True
            )
        )

    #Create customization
    if customization_exists == False:
        print("INFO: There is no default customization. The default customization will be loaded.")

        for role in default_settings:
            for setting in default_settings[role]:
                role_obj = await db.execute(select(models.Role).filter(models.Role.name == role))
                role_obj = role_obj.scalars().first()
                customization_create = models.Customization(
                    role_id=role_obj.id,
                    type=setting,
                    default_setting={setting: default_settings[role][setting]},
                )
                await crud.customization.create(
                    db, obj_in=customization_create
                )
                print(
                    "INFO: Default setting of parameter [bold magenta]%s[/bold magenta] for [bold magenta]%s[/bold magenta] added."
                    % (setting, role)
                )
    else:
        print("INFO: There is default customization in the Database. The default customization will not be loaded.")
