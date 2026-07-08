import secrets
from datetime import datetime
from urllib.parse import urlencode

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User

"""Authentication service — supports email/password + Google OAuth for portal login."""


GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


# ---------------------------------------------------------------------------
# Email / Password
# ---------------------------------------------------------------------------

async def register_user(db: AsyncSession, email: str, password: str, name: str) -> User:
    """Register a new user with email and password."""
    existing = await db.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none():
        raise ValueError("Email already registered")

    user = User(
        email=email,
        name=name,
        password_hash=hash_password(password),
    )
    db.add(user)
    await db.flush()
    return user


async def login_with_password(db: AsyncSession, email: str, password: str) -> User:
    """Authenticate with email and password."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not user.password_hash:
        raise ValueError("Invalid email or password")

    if not verify_password(password, user.password_hash):
        raise ValueError("Invalid email or password")

    user.last_login = datetime.utcnow()
    await db.flush()
    return user


# ---------------------------------------------------------------------------
# Google OAuth (portal-only identity — no NotebookLM tokens stored)
# ---------------------------------------------------------------------------

def get_google_redirect_url() -> str:
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
        "state": secrets.token_urlsafe(32),
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"


async def exchange_code_for_tokens(code: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        response.raise_for_status()
        return response.json()


async def get_google_user_info(access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        return response.json()


async def get_or_create_google_user(db: AsyncSession, user_info: dict) -> User:
    """Find or create user from Google OAuth. Does NOT store Google tokens."""
    result = await db.execute(
        select(User).where(User.google_id == user_info["id"])
    )
    user = result.scalar_one_or_none()

    if user:
        user.avatar_url = user_info.get("picture")
        user.name = user_info.get("name")
        user.last_login = datetime.utcnow()
    else:
        # Check if a user with this email already exists (e.g. registered via password)
        email_result = await db.execute(
            select(User).where(User.email == user_info["email"])
        )
        user = email_result.scalar_one_or_none()

        if user:
            # Link Google account to existing email/password user
            user.google_id = user_info["id"]
            user.avatar_url = user_info.get("picture")
            user.last_login = datetime.utcnow()
        else:
            user = User(
                email=user_info["email"],
                name=user_info.get("name"),
                google_id=user_info["id"],
                avatar_url=user_info.get("picture"),
            )
            db.add(user)

    await db.flush()
    return user


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------

def generate_jwt_token(user_id: str) -> str:
    return create_access_token(data={"sub": user_id})
