from src.db.session import sync_session
from src import crud
from src.workers.celery_app import celery_app
from src.schemas.isochrone import IsochroneDTO
from src.db import models
import binascii
from src.core.config import settings


@celery_app.task()
def task_calculate_isochrone(isochrone_in, current_user, study_area_bounds):
    isochrone_in = IsochroneDTO(**isochrone_in)
    current_user = models.User(**current_user)
    db = sync_session()
    result = crud.isochrone.calculate(db, isochrone_in, current_user, study_area_bounds)
    db.close()

    result = {
        "data": result,
        "return_type": isochrone_in.output.type.value,
        "hexlified": False,
        "data_source": "isochrone",
    }
    if settings.CELERY_BROKER_URL:
        # if we are using celery, we need to convert the numpy array to a string
        result["data"]["grid"] = binascii.hexlify(bytes(result["data"]["grid"])).decode("utf-8")
        result["hexlified"] = True

    return result
