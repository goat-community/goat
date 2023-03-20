from src.db.session import sync_session
from src import crud
from src.workers.celery_app import celery_app
from src.schemas.isochrone import IsochroneDTO
from src.db import models
import binascii


@celery_app.task()
def task_calculate_isochrone(isochrone_in, current_user, study_area_bounds):
    isochrone_in = IsochroneDTO(**isochrone_in)
    current_user = models.User(**current_user)
    db = sync_session()
    result = crud.isochrone.calculate(db, isochrone_in, current_user, study_area_bounds)
    db.close()
    result = binascii.hexlify(bytes(result)).decode('utf-8')
    return result
