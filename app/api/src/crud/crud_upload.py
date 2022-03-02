from typing import Any

from fastapi import APIRouter, Body, Depends, File, UploadFile, HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession

from src import crud
from src.crud.base import CRUDBase
from src.db import models
from src.resources.enums import UploadFileTypes
from src.schemas.upload import request_examples
from geopandas import read_file as gpd_read_file, read_postgis as gpd_read_postgis
from geopandas import GeoDataFrame
from src.db.session import legacy_engine
from geoalchemy2.shape import to_shape
import uuid
import os
import shutil
from src.utils import clean_unpacked_zip

class CRUDDataUpload(
    CRUDBase[models.Customization, models.Customization, models.Customization]
):
    pass

user_upload = CRUDDataUpload(models.DataUpload)

class CRUDUploadFile:
    async def upload_custom_pois(
        self, *, 
        db: AsyncSession, 
        file: UploadFile, 
        poi_category: str, 
        current_user: models.User
    ):

        """Handle uploaded custom pois."""
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
        )
        upload_obj = await user_upload.create(db=db, obj_in=upload_obj)

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
        
upload = CRUDUploadFile()