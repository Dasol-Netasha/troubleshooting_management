from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud_parts.db_utils import ping_db
from app.database import get_db
from app.schemas import HealthCheck

router = APIRouter()


@router.get("/health", response_model=HealthCheck)
def health_check(db: Session = Depends(get_db)) -> HealthCheck:
    ping_db(db)
    return HealthCheck(status="ok")
