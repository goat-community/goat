import asyncio

async def fun_task1(db,scenarioId):
    #//1- Delete from scenario first
    await asyncio.sleep(1)
    result = await db.select("""SELECT * FROM network_modification(%(scenarioId)s)""",{"scenarioId":scenarioId})
    #return'hello'
    return result
    
async def fun_task2(db,scenarioId):
    #//2- Rerun upload for ways to reflect the changes.
    await asyncio.sleep(2)
    result = await db.select("""SELECT * FROM population_modification(%(scenarioId)s)""",{"scenarioId":scenarioId})
    #return'hello'
    return result

async def stop_after(loop):
    await asyncio.sleep(3)
    loop.stop()

async def delete_task(db,scenarioId):
    #//1- Delete from scenario first
    await asyncio.sleep(1)
    db.perform("""DELETE FROM scenarios WHERE scenario_id=%(scenarioId)s""",{"scenarioId":scenarioId})
    
async def select_task(db,scenarioId):
    #//2- Rerun upload for ways to reflect the changes.
    await asyncio.sleep(2)
    result = db.select("""SELECT * FROM network_modification(%(scenarioId)s)""",{"scenarioId":scenarioId})
    return result