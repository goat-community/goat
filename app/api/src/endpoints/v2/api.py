from fastapi import APIRouter
from . import layers

router = APIRouter()
router.include_router(layers.router, prefix="/layers", tags=["layers"])
