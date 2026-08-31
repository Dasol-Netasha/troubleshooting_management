from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Account
from app.schemas.common import LoginRequest, LoginResponse
from app.security import verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    account_id = str(payload.id or "").strip()
    password = str(payload.pw or "")

    if not account_id or not password:
        raise HTTPException(status_code=400, detail="id and pw are required")

    account = db.execute(select(Account).where(Account.account_id == account_id)).scalar_one_or_none()
    if account is None or account.is_active is False:
        raise HTTPException(status_code=401, detail="invalid credentials")

    if not verify_password(password, account.password_hash):
        raise HTTPException(status_code=401, detail="invalid credentials")

    return LoginResponse(
        authenticated=True,
        account_id=account.account_id,
        display_name=account.display_name,
    )