import ssl
from typing import Any

from fastapi import UploadFile, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, text, update, and_
from src import crud
from src.crud.base import CRUDBase
from src.db import models
from src.resources.enums import UploadFileTypes
from src.schemas.upload import request_examples
from geopandas import read_file as gpd_read_file, read_postgis as gpd_read_postgis
from src.db.session import legacy_engine
from geoalchemy2.shape import to_shape
import uuid
import os
import shutil
from src.utils import clean_unpacked_zip
from sqlalchemy.dialects import postgresql


class CRUDDataUpload(
    CRUDBase[models.Customization, models.Customization, models.Customization]
):
    pass

data_upload = CRUDDataUpload(models.DataUpload)

class CRUDUploadFile:
    async def upload_custom_pois(
        self, *, 
        db: AsyncSession, 
        file: UploadFile, 
        poi_category: str, 
        current_user: models.User
    ):

        """Handle uploaded custom pois."""
        # Check if poi_category is already uploaded for study area
        query_poi_features = select(models.PoiUser.category).join(models.DataUpload).where(
                and_(
                    models.DataUpload.user_id == current_user.id,
                    models.DataUpload.study_area_id == current_user.active_study_area_id,
                    models.PoiUser.data_upload_id == models.DataUpload.id,
                    models.PoiUser.category == poi_category
                )
        ).limit(1)

        poi_features = await db.execute(query_poi_features)
        poi_features = poi_features.first()

        if poi_features is not None:
            raise HTTPException(status_code=400, detail="The chosen custom poi category already exists. Please delete the old data-set first in case you want to replace it with the new one")

        required_attributes = ['geometry']
        optional_attributes = ["opening_hours", "name",	"street", "housenumber", "zipcode",	"opening_hours", "wheelchair"] 
        # Get active study area
        study_area_obj = await crud.study_area.get(db=db, id=current_user.active_study_area_id, extra_fields=["geom"])
        study_area_geom = to_shape(study_area_obj.geom)

        if file.content_type == UploadFileTypes.geojson.value:
            gdf = gpd_read_file(file.file)
        elif file.content_type == UploadFileTypes.zip.value:   
            defined_uuid = uuid.uuid4().hex
            file_dir = f"/tmp/{defined_uuid}"
            unzipped_file_dir = f"/tmp/{defined_uuid}/{os.path.splitext(file.filename)[0]}"
            
            # Create directory
            try: 
                with open(file_dir + '.zip', "wb+") as file_object:
                    file_object.write(file.file.read())
                shutil.unpack_archive(file_dir + '.zip', file_dir, "zip")      
            except:
                clean_unpacked_zip(zip_path=file_dir+'.zip', dir_path=file_dir)
                raise HTTPException(status_code=400, detail="Could not read or process file.")
            
            # List shapefiles
            try:
                available_shapefiles = [f for f in os.listdir(unzipped_file_dir) if f.endswith(".shp")]
            except:
                clean_unpacked_zip(zip_path=file_dir+'.zip', dir_path=file_dir)
                raise HTTPException(status_code=400, detail="No shapefiles inside folder.")

            # Read shapefiles and append to GeoDataFrame
            if len(available_shapefiles) == 1:
                gdf = gpd_read_file(f"{unzipped_file_dir}/{available_shapefiles[0]}")
            elif len(available_shapefiles) > 1:
                clean_unpacked_zip(zip_path=file_dir+'.zip', dir_path=file_dir)
                raise HTTPException(status_code=400, detail="More then one shapefiles inside folder.")
            else:
                raise HTTPException(status_code=400, detail="No shapefiles inside folder.")
                
            clean_unpacked_zip(zip_path=file_dir+'.zip', dir_path=file_dir)
        else:
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        # Convert to EPSG 4326
        gdf_schema = dict(gdf.dtypes)
        if gdf.crs.name == "unknown":
            raise HTTPException(status_code=400, detail="Invalid CRS")
        else:
            gdf.to_crs(epsg=4326, inplace=True)
            gdf.set_crs(epsg=4326)
            gdf = gdf.clip(study_area_geom)

        # Drop not needed columns
        columns_to_drop = []
        for attribute in gdf_schema:
            if attribute not in optional_attributes + required_attributes:
                columns_to_drop.append(attribute)

        gdf = gdf.drop(columns_to_drop, axis = 1)

        # Assign specified category to all points
        gdf["category"] = poi_category

        # Create entry in upload table
        upload_obj = models.DataUpload(
            data_type=file.content_type,
            upload_type=models.PoiUser.__table__.name, 
            user_id=current_user.id,
            upload_size=int(file.file.tell()/1000),
            study_area_id=current_user.active_study_area_id
        )
        upload_obj = await data_upload.create(db=db, obj_in=upload_obj)

        # Write to database
        gdf["uid"] = str(round(gdf.centroid.x, 4)) + '_' + str(round(gdf.centroid.y, 4))
        gdf["uid"] = gdf.centroid.map(lambda p: str(format(round(p.x, 4), '.4f')) + '_' + str(format(round(p.y, 4), '.4f'))) + '_' + str(poi_category)
        gdf["count_uid"] = gdf.groupby(['uid']).cumcount()+1
        gdf["uid"] = gdf["uid"] + '_' + gdf["count_uid"].astype(str) + '_' + str(upload_obj.id)
        gdf["data_upload_id"] = upload_obj.id

        gdf.rename_geometry("geom", inplace=True)
        gdf.drop(["count_uid"], axis=1, inplace=True)

        gdf.to_postgis(name="poi_user", schema="customer", con=legacy_engine, if_exists="append", chunksize=1000)

        return {'msg': 'Upload successful'}

    async def delete_custom_pois(
        self, *, 
        db: AsyncSession, 
        data_upload_id: int, 
        current_user: models.User
    ):
        """Delete uploaded custom pois."""

        category_name = await db.execute(select(models.PoiUser.category).where(models.PoiUser.data_upload_id == data_upload_id))
        category_name = category_name.first()[0]
        default_setting = await crud.customization.get_by_key(db, key="type", value='poi_groups')
        default_setting = default_setting[0].setting
        # Check if poi_category is default
        in_default_setting = False
        for poi_group in default_setting["poi_groups"]:
                group_name = next(iter(poi_group))
                for poi_category in poi_group[group_name]["children"]:
                    default_poi_category = next(iter(poi_category))
                    if category_name == default_poi_category:
                        in_default_setting = True
                        break
    
        try: 
            # Delete uploaded data
            await db.execute(delete(models.DataUpload).where(models.DataUpload.id == data_upload_id))

            # Delete related scenarios
            sql = text("""DELETE FROM customer.scenario WHERE data_upload_ids && :data_upload_id AND user_id = :user_id""")
            await db.execute(sql, {"data_upload_id": [data_upload_id], "user_id": current_user.id})

            # Delete customization for uploaded pois 
            if in_default_setting == False:
                user_setting = await crud.dynamic_customization.get_user_settings(db=db, current_user=current_user, setting_type='poi_groups')
                await crud.dynamic_customization.delete_user_settings(
                    db=db, 
                    current_user=current_user, 
                    user_customizations=user_setting, 
                    setting_to_delete=category_name, 
                    setting_type='poi_groups'
                )

            await db.execute(update(models.User).where(models.User.id == current_user.id).values(active_data_upload_ids=current_user.active_data_upload_ids))
            if current_user.active_data_upload_ids != []:
                current_user.active_data_upload_ids.remove(data_upload_id)
                sql_query = text("""UPDATE customer.user SET active_data_upload_ids = :active_data_upload_ids WHERE id = :id""")
                await db.execute(sql_query, {"active_data_upload_ids": current_user.active_data_upload_ids, "id": current_user.id})
            
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail="Could not delete %s data." % category_name)
        
upload = CRUDUploadFile()

