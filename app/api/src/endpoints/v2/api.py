from fastapi import APIRouter
from . import folder
from . import layer
from . import project
from . import report
from . import user

router = APIRouter()
# TODO: Uncommenting this to avoid having the endpoints activated in the live demo as they are not yet authenticated
router.include_router(user.router, prefix="/user", tags=["User"])
router.include_router(folder.router, prefix="/folder", tags=["Folder"])
router.include_router(layer.router, prefix="/layer", tags=["Layer"])
router.include_router(project.router, prefix="/project", tags=["Project"])
router.include_router(report.router, prefix="/report", tags=["Report"])
