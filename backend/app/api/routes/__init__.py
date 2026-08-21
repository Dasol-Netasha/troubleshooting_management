from fastapi import APIRouter

from app.api.routes.common import router as common_router
from app.api.routes.issues_detail import router as issue_detail_router
from app.api.routes.issues_list import router as issue_list_router

router = APIRouter()
router.include_router(common_router)
router.include_router(issue_list_router)
router.include_router(issue_detail_router)

__all__ = ["router"]
