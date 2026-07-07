from enum import Enum

from pydantic import BaseModel, EmailStr


class PreferredLLM(str, Enum):
    openai = "openai"
    anthropic = "anthropic"
    google = "google"


class GoogleRedirectResponse(BaseModel):
    authorization_url: str


class GoogleCallbackRequest(BaseModel):
    code: str
    state: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str


class AuthMeResponse(BaseModel):
    id: str
    email: str
    name: str | None = None
    avatar_url: str | None = None
    notebooklm_connected: bool = False
    preferred_llm: str = "openai"

    class Config:
        from_attributes = True
