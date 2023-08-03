from fastapi import APIRouter
from . import content
from . import user 

router = APIRouter()
#TODO: Uncommenting this to avoid having the endpoints activated in the live demo as they are not yet authenticated
# router.include_router(user.router, prefix="/user", tags=["User"])
# router.include_router(content.router, prefix="/content", tags=["Content"])
