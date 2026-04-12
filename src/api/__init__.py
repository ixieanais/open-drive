from fastapi import APIRouter

from .files import router as files_router
from .folders import router as folders_router
from .favorites import router as favorites_router


router = APIRouter(prefix="/api")

router.include_router(files_router)
router.include_router(folders_router)
router.include_router(favorites_router)
