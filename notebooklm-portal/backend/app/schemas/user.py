from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class UserProfileResponse(BaseModel):
    id: str
    email: str
    name: str | None = None
    avatar_url: str | None = None
    preferred_llm: str = "openai"
    created_at: datetime
    last_login: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("id", mode="before")
    @classmethod
    def convert_id(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v


class UserProfileUpdate(BaseModel):
    name: str | None = None
    avatar_url: str | None = None


class UserSettingsResponse(BaseModel):
    preferred_llm: str = "openai"

    model_config = ConfigDict(from_attributes=True)


class UserSettingsUpdate(BaseModel):
    preferred_llm: str | None = None


class LLMKeyRequest(BaseModel):
    llm_api_key: str
