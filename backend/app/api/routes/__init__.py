from fastapi import APIRouter

from app.api.routes.common import router as common_router
from app.api.routes.issues_list import router as issues_router

router = APIRouter()
router.include_router(common_router)
router.include_router(issues_router)

__all__ = ["router"]
