
async def fun_task1(db,scenarioId):
    #//1- Delete from scenario first
    result = db.perform(f"""SELECT * FROM network_modification({scenarioId});""")
    return result
    
async def fun_task2(db,scenarioId):
    #//2- Rerun upload for ways to reflect the changes.
    result = db.select(f"""SELECT * FROM population_modification({scenarioId});""")
    return result

async def delete_task(db,scenarioId):
    #//1- Delete from scenario first
    await asyncio.sleep(1)
    db.perform(f"""DELETE FROM scenarios WHERE scenario_id={scenarioId};""")
    
async def select_task(db,scenarioId):
    #//2- Rerun upload for ways to reflect the changes.
    await asyncio.sleep(2)
    result = db.select(f"""SELECT * FROM network_modification({scenarioId});""")
    return result