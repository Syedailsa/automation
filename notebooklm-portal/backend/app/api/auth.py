from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.exceptions import BadRequestException
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    AuthMeResponse,
    GoogleCallbackRequest,
    GoogleRedirectResponse,
    TokenResponse,
)
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/google/redirect", response_model=GoogleRedirectResponse)
async def google_redirect():
    url = auth_service.get_google_redirect_url()
    return GoogleRedirectResponse(authorization_url=url)


@router.post("/google/callback", response_model=TokenResponse)
async def google_callback(body: GoogleCallbackRequest, db: AsyncSession = Depends(get_db)):
    try:
        tokens = await auth_service.exchange_code_for_tokens(body.code)
    except Exception:
        raise BadRequestException("Failed to exchange authorization code")

    try:
        user_info = await auth_service.get_google_user_info(tokens["access_token"])
    except Exception:
        raise BadRequestException("Failed to get user info from Google")

    user = await auth_service.get_or_create_user(db, user_info, tokens)
    token = auth_service.generate_jwt_token(str(user.id))

    return TokenResponse(access_token=token, user_id=str(user.id))


@router.get("/me", response_model=AuthMeResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return AuthMeResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        avatar_url=current_user.avatar_url,
        notebooklm_connected=current_user.notebooklm_connected,
        preferred_llm=current_user.preferred_llm,
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    current_user.access_token = None
    current_user.refresh_token = None
    return {"message": "Logged out successfully"}
