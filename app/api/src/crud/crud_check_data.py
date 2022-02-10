from typing import Dict
from xmlrpc.client import Boolean
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from rich import print

class CRUDCheckData():
    async def table_is_empty(self, db: AsyncSession, ModelDB) -> Dict:
        try:
            result = await db.execute(select(ModelDB).limit(1))
        except SQLAlchemyError as e:
            print('[red]%s[/red]' % e)
            return {"Result": "Error: Problem in finding or accessing table."}        
        
        if result.scalars().first() is None:
            return {"Result": True}  
        else:
            return {"Result": False}
  
check_data = CRUDCheckData()