import datetime
from typing import Any, List

from bson.objectid import ObjectId
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

from src.schemas.r5 import (
    R5ProjectCreateDTO,
    R5ProjectInDB,
    R5ProjectUpdateDTO,
    R5RegionCreateDTO,
    R5RegionInDB,
)

database_name = "analysis"


class CRUDR5:
    # --------------------------REGION CRUD------------------------------
    # -------------------------------------------------------------------
    async def get_all_regions(self, db: AsyncIOMotorClient) -> List[R5RegionInDB]:
        """
        Get all regions.
        """
        regions = []
        rows = db[database_name].regions.find()
        async for row in rows:
            regions.append(R5RegionInDB(**row))
        return regions

    async def get_region(self, db: AsyncIOMotorClient, region_id: str) -> R5RegionInDB:
        """
        Get region.
        """
        region = await db[database_name].regions.find_one({"_id": region_id})

        return region

    async def create_region(
        self, db: AsyncIOMotorClient, region_in: R5RegionCreateDTO
    ) -> R5RegionInDB:
        """
        Create new region.
        """
        region_db_obj = R5RegionInDB(
            **region_in.dict(),
            createdAt=datetime.datetime.now(),
            updatedAt=datetime.datetime.now(),
            nonce=str(ObjectId())
        )
        if hasattr(region_db_obj, "id"):
            delattr(region_db_obj, "id")
        region_db_dict = region_db_obj.dict(by_alias=True)
        region_db_dict["_id"] = str(ObjectId())
        ret = await db[database_name].regions.insert_one(region_db_dict)
        region_db_obj.id = ret.inserted_id
        return region_db_obj

    # delete region
    async def delete_region(self, db: AsyncIOMotorClient, region_id: str) -> Any:
        """
        Delete region.
        """
        await db[database_name].regions.delete_one({"_id": region_id})
        return {"msg": "Region deleted successfully"}

    # -------------------------PROJECT CRUD-----------------------------
    # ------------------------------------------------------------------
    async def get_all_projects(self, db: AsyncIOMotorClient) -> List[R5ProjectInDB]:
        """
        Get all projects.
        """
        projects = []
        rows = db[database_name].projects.find()
        async for row in rows:
            projects.append(R5ProjectInDB(**row))
        return projects

    async def get_projects_for_region(
        self, db: AsyncIOMotorClient, region_id: str
    ) -> List[R5ProjectInDB]:
        """
        Get all projects for a region.
        """
        projects = []
        rows = db[database_name].projects.find({"regionId": region_id})
        async for row in rows:
            projects.append(R5ProjectInDB(**row))
        return projects

    # get project by id
    async def get_project(self, db: AsyncIOMotorClient, project_id: str) -> R5ProjectInDB:
        """
        Get project.
        """
        project = await db[database_name].projects.find_one({"_id": project_id})
        return project

    async def create_project(
        self, db: AsyncIOMotorClient, project_in: R5ProjectCreateDTO
    ) -> R5ProjectInDB:
        """
        Create new project.
        """
        region = await db[database_name].regions.find_one({"_id": project_in.regionId})
        bundle = await db[database_name].bundles.find_one({"_id": project_in.bundleId})
        if region is None:
            raise HTTPException(
                status_code=400,
                detail="Region does not exist",
            )
        if bundle is None:
            raise HTTPException(
                status_code=400,
                detail="Bundle does not exist",
            )

        project_db_obj = R5ProjectInDB(
            **project_in.dict(),
            createdAt=datetime.datetime.now(),
            updatedAt=datetime.datetime.now(),
            nonce=str(ObjectId())
        )
        if hasattr(project_db_obj, "id"):
            delattr(project_db_obj, "id")
        project_db_dict = project_db_obj.dict(by_alias=True)
        project_db_dict["_id"] = str(ObjectId())
        ret = await db[database_name].projects.insert_one(project_db_dict)
        project_db_obj.id = ret.inserted_id
        return project_db_obj

    # update project
    async def update_project(self, db: AsyncIOMotorClient, project_in: R5ProjectUpdateDTO) -> Any:
        """
        Update project.
        """
        await db[database_name].projects.update_one(
            {"_id": project_in.id}, {"$set": project_in.dict()}
        )
        return {"msg": "Project updated successfully"}

    # delete project
    async def delete_project(self, db: AsyncIOMotorClient, project_id: str) -> Any:
        """
        Delete project.
        """
        await db[database_name].projects.delete_one({"_id": project_id})
        return {"msg": "Project deleted successfully"}


r5 = CRUDR5()
