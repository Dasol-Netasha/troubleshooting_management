from pydantic import BaseModel


class HealthCheck(BaseModel):
    status: str


class LoginRequest(BaseModel):
    id: str
    pw: str


class LoginResponse(BaseModel):
    authenticated: bool
    account_id: str
    display_name: str | None = None
