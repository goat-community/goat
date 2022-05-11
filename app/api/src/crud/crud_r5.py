from typing import List

from motor.motor_asyncio import AsyncIOMotorClient

from src.schemas.r5 import R5RegionInDB

database_name = "analysis"


class CRUDR5:
    async def get_all_regions(self, db: AsyncIOMotorClient) -> List[R5RegionInDB]:
        """
        Get all regions.
        """
        regions = []
        rows = db[database_name].regions.find()
        async for row in rows:
            regions.append(R5RegionInDB(**row))
        return regions


r5 = CRUDR5()
