from typing import Dict
from xmlrpc.client import Boolean
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sentry_sdk import capture_exception
from rich import print

class CRUDCheckData():
    async def table_is_empty(self, db, ModelDB) -> Dict:
        try:
            result = await db.execute(select(ModelDB).limit(1))
        except Exception as e:
            capture_exception(e)

        if result.scalars().first() is not None:
            return True  
        else:
            return False
  
check_data = CRUDCheckData()