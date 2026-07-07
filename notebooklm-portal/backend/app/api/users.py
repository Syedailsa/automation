from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    LLMKeyRequest,
    NotebookLMStatusResponse,
    UserProfileResponse,
    UserProfileUpdate,
    UserSettingsResponse,
    UserSettingsUpdate,
)
from app.services import user_service

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    body: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await user_service.update_user_profile(
        db, current_user, name=body.name, avatar_url=body.avatar_url
    )


@router.get("/settings", response_model=UserSettingsResponse)
async def get_settings(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/settings", response_model=UserSettingsResponse)
async def update_settings(
    body: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await user_service.update_user_settings(
        db, current_user, preferred_llm=body.preferred_llm
    )


@router.post("/llm-key")
async def store_llm_key(
    body: LLMKeyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await user_service.store_llm_key(db, current_user, body.llm_api_key)
    return {"message": "LLM API key stored successfully"}


@router.get("/notebooklm-status", response_model=NotebookLMStatusResponse)
async def get_notebooklm_status(current_user: User = Depends(get_current_user)):
    return NotebookLMStatusResponse(
        notebooklm_connected=current_user.notebooklm_connected,
        last_login=current_user.last_login,
    )
