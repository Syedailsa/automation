from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserProfileResponse(BaseModel):
    id: str
    email: str
    name: str | None = None
    avatar_url: str | None = None
    notebooklm_connected: bool = False
    preferred_llm: str = "openai"
    created_at: datetime
    last_login: datetime

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdate(BaseModel):
    name: str | None = None
    avatar_url: str | None = None


class UserSettingsResponse(BaseModel):
    preferred_llm: str = "openai"
    notebooklm_connected: bool = False

    model_config = ConfigDict(from_attributes=True)


class UserSettingsUpdate(BaseModel):
    preferred_llm: str | None = None


class LLMKeyRequest(BaseModel):
    llm_api_key: str


class NotebookLMStatusResponse(BaseModel):
    notebooklm_connected: bool
    last_login: datetime | None = None
