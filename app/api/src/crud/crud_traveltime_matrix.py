from src.crud.base import CRUDBase
from src.db import models


class CRUDTraveltimeMatrixWalking(CRUDBase[models.TravelTimeMatrixWalking, models.TravelTimeMatrixWalking, models.TravelTimeMatrixWalking]):
    pass


traveltime_matrix_walking = CRUDTraveltimeMatrixWalking(models.TravelTimeMatrixWalking)

