from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.models import Account
from app.security import hash_password

from app.api.routes import router

app = FastAPI(title="Base Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def bootstrap_auth_account() -> None:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        account = db.execute(select(Account).where(Account.account_id == "enscape")).scalar_one_or_none()
        if account is None:
            db.add(
                Account(
                    account_id="enscape",
                    password_hash=hash_password("enscape123!"),
                    display_name="enscape",
                    is_active=True,
                )
            )
            db.commit()


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Base backend is running"}


app.include_router(router, prefix="/api")