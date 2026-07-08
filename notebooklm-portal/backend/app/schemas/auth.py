from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PreferredLLM(str, Enum):
    openai = "openai"
    anthropic = "anthropic"
    google = "google"


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)
    name: str = Field(min_length=1, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


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
    preferred_llm: str = "openai"

    model_config = ConfigDict(from_attributes=True)
