import os
import random
import shutil

from fastapi import HTTPException, UploadFile
from geoalchemy2.shape import to_shape
from geopandas import read_file as gpd_read_file
from sqlalchemy import and_, delete, text, update
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm.attributes import flag_modified

from src import crud, schemas
from src.crud.base import CRUDBase
from src.db import models
from src.db.models.config_validation import PoiCategory, check_dict_schema
from src.db.session import legacy_engine
from src.resources.enums import UploadFileTypes
from src.utils import clean_unpacked_zip, delete_file


class CRUDDataUpload(CRUDBase[models.Customization, models.Customization, models.Customization]):
    pass


data_upload = CRUDDataUpload(models.DataUpload)


class CRUDUploadFile:
    async def upload_custom_pois(
        self,
        *,
        db: AsyncSession,
        file: UploadFile,
        file_dir: str,
        file_name: str,
        poi_category: str,
        current_user: models.User,
    ):

        """Handle uploaded custom pois."""
        # Check if poi_category is already uploaded for study area
        try:
            query_poi_features = (
                select(models.PoiUser.category)
                .join(models.DataUpload)
                .where(
                    and_(
                        models.DataUpload.user_id == current_user.id,
                        models.DataUpload.study_area_id == current_user.active_study_area_id,
                        models.PoiUser.data_upload_id == models.DataUpload.id,
                        models.PoiUser.category == poi_category,
                    )
                )
                .limit(1)
            )

            poi_features = await db.execute(query_poi_features)
            poi_features = poi_features.first()
        except:
            delete_file(file_dir)
            raise HTTPException(
                status_code=400,
                detail="Failed reading the file.",
            )

        if poi_features is not None:
            delete_file(file_dir)
            raise HTTPException(
                status_code=400,
                detail="The chosen custom poi category already exists. Please delete the old data-set first in case you want to replace it with the new one",
            )

        required_attributes = ["geometry"]
        optional_attributes = [
            "opening_hours",
            "name",
            "street",
            "housenumber",
            "zipcode",
            "opening_hours",
            "wheelchair",
        ]
        # Get active study area

        study_area_obj = await crud.study_area.get(
            db=db, id=current_user.active_study_area_id, extra_fields=["geom"]
        )
        study_area_geom = to_shape(study_area_obj.geom)

        if UploadFileTypes.geojson.value in file_name:
            try:
                gdf = gpd_read_file(file_dir, driver="GeoJSON")
                delete_file(file_dir)
            except:
                delete_file(file_dir)
                raise HTTPException(
                    status_code=400,
                    detail="Failed reading the file in GeodataFrame",
                )
        elif UploadFileTypes.zip.value in file_name:
            unzipped_file_dir = (
                os.path.splitext(file_dir)[0]
                + "/"
                + file.filename.replace(UploadFileTypes.zip.value, "")
            )

            # Create directory
            try:
                shutil.unpack_archive(file_dir, os.path.splitext(file_dir)[0], "zip")
            except:
                clean_unpacked_zip(
                    zip_path=file_dir, dir_path=file_dir.replace(UploadFileTypes.zip.value, "")
                )
                raise HTTPException(status_code=400, detail="Could not read or process file.")

            # List shapefiles
            try:
                available_shapefiles = [
                    f for f in os.listdir(unzipped_file_dir) if f.endswith(".shp")
                ]
            except:
                clean_unpacked_zip(
                    zip_path=file_dir, dir_path=file_dir.replace(UploadFileTypes.zip.value, "")
                )
                raise HTTPException(status_code=400, detail="No shapefiles inside folder.")

            # Read shapefiles and append to GeoDataFrame
            if len(available_shapefiles) == 1:
                gdf = gpd_read_file(f"{unzipped_file_dir}/{available_shapefiles[0]}")
            elif len(available_shapefiles) > 1:
                clean_unpacked_zip(
                    zip_path=file_dir, dir_path=file_dir.replace(UploadFileTypes.zip.value, "")
                )
                raise HTTPException(
                    status_code=400, detail="More then one shapefiles inside folder."
                )
            else:
                raise HTTPException(status_code=400, detail="No shapefiles inside folder.")
            clean_unpacked_zip(
                zip_path=file_dir, dir_path=file_dir.replace(UploadFileTypes.zip.value, "")
            )
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

        gdf = gdf.drop(columns_to_drop, axis=1)
        if len(gdf) == 0:
            raise HTTPException(
                status_code=400, detail="No valid data in file or data outside the study area."
            )

        # Assign specified category to all points
        gdf["category"] = poi_category

        # Create entry in upload table
        upload_obj = models.DataUpload(
            data_type=file.content_type,
            upload_type=models.PoiUser.__table__.name,
            user_id=current_user.id,
            upload_size=int(file.file.tell() / 1000),
            study_area_id=current_user.active_study_area_id,
        )
        upload_obj = await data_upload.create(db=db, obj_in=upload_obj)

        # Write to database
        try:
            gdf["uid"] = (
                gdf.centroid.map(
                    lambda p: str(format(round(p.x, 4), ".4f")).replace(".", "")
                    + "_"
                    + str(format(round(p.y, 4), ".4f")).replace(".", "")
                )
                + "_"
                + str(poi_category)
            )
            gdf["count_uid"] = gdf.groupby(["uid"]).cumcount() + 1
            gdf["uid"] = (
                gdf["uid"] + "_" + gdf["count_uid"].astype(str) + "_u" + str(upload_obj.id)
            )
            gdf["data_upload_id"] = upload_obj.id

            gdf.rename_geometry("geom", inplace=True)
            gdf.drop(["count_uid"], axis=1, inplace=True)

            gdf.to_postgis(
                name="poi_user",
                schema="customer",
                con=legacy_engine,
                if_exists="append",
                chunksize=1000,
            )

        except:
            await db.execute(
                """DELETE FROM customer.data_upload WHERE id = :data_upload_id""",
                {"data_upload_id": upload_obj.id},
            )
            await db.commit()
            raise HTTPException(
                status_code=400,
                detail="An error happened when writing the data into the database.",
            )

        try:
            default_poi_categories = (
                await crud.dynamic_customization.get_all_default_poi_categories(db)
            )
            if poi_category not in default_poi_categories:
                hex_color = "#%06x" % random.randint(0, 0xFFFFFF)
                new_setting = {poi_category: {"icon": "fas fa-question", "color": [hex_color]}}

                if check_dict_schema(PoiCategory, new_setting) is False:
                    raise HTTPException(status_code=400, detail="Invalid JSON-schema")

                await crud.dynamic_customization.insert_opportunity_setting(
                    db=db, current_user=current_user, insert_settings=new_setting, data_upload_id=upload_obj.id
                )

        except:
            await db.execute(
                """DELETE FROM customer.data_upload WHERE id = :data_upload_id""",
                {"data_upload_id": upload_obj.id},
            )
            await db.commit()
            raise HTTPException(
                status_code=400,
                detail="An error happened when writing new settings to the database.",
            )

        return {"msg": "Upload successful"}

    async def delete_custom_pois(
        self, *, db: AsyncSession, data_upload_id: int, current_user: models.User
    ):
        """Delete uploaded custom pois."""

        category_name = await db.execute(
            select(models.PoiUser.category).where(models.PoiUser.data_upload_id == data_upload_id)
        )
        category_name = category_name.first()[0]

        # Check if poi_category is default
        default_category = await crud.opportunity_default_config.get_by_key(db, key="category", value=category_name)

        try:
            # Delete uploaded data
            await db.execute(
                delete(models.DataUpload).where(models.DataUpload.id == data_upload_id)
            )

            # Delete related scenarios
            sql = text(
                """DELETE FROM customer.scenario WHERE data_upload_ids && :data_upload_id AND user_id = :user_id"""
            )
            await db.execute(sql, {"data_upload_id": [data_upload_id], "user_id": current_user.id})

            # Delete customization for uploaded pois
            if default_category == [] and category_name is not None:
                await crud.dynamic_customization.delete_opportunity_setting(
                    db=db,
                    current_user=current_user,
                    category=category_name,
                    setting_type="poi",
                )

            if (
                current_user.active_data_upload_ids != []
                and data_upload_id in current_user.active_data_upload_ids
            ):
                current_user.active_data_upload_ids.remove(data_upload_id)
                await db.execute(
                    update(models.User)
                    .where(models.User.id == current_user.id)
                    .values(active_data_upload_ids=current_user.active_data_upload_ids)
                )

            await db.commit()
        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=400, detail="Could not delete %s data." % category_name
            )

    async def set_active_state_of_custom_poi(
        self, *, db: AsyncSession, obj_in: schemas.CutomDataUploadState, current_user: models.User
    ):
        """Set active state of custom poi."""
        data_upload_obj = await db.execute(
            select(models.DataUpload).filter(models.DataUpload.id == obj_in.data_upload_id)
        )
        data_upload_obj = data_upload_obj.scalars().first()
        if data_upload_obj.user_id != current_user.id:
            raise HTTPException(status_code=400, detail="User ID does not match")

        data_upload_ids_obj = current_user.active_data_upload_ids

        if obj_in.state is False and data_upload_obj.id in data_upload_ids_obj:
            try:
                data_upload_ids_obj.remove(obj_in.data_upload_id)
            except ValueError:
                print("Data upload doesn't exist")
        elif obj_in.state is True and data_upload_obj.id not in data_upload_ids_obj:
            data_upload_ids_obj.append(obj_in.data_upload_id)
        else:
            return current_user

        current_user.active_data_upload_ids = data_upload_ids_obj
        flag_modified(current_user, "active_data_upload_ids")
        db.add(current_user)
        await db.commit()
        await db.refresh(current_user)
        return current_user


upload = CRUDUploadFile()
