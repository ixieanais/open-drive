from fastapi import APIRouter

from .storage import router as storage_router


router = APIRouter(prefix="/api")

router.include_router(storage_router)
