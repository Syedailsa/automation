from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.user import User
from app.services.cache_service import cache


async def get_user_by_id(db: AsyncSession, user_id: str) -> User:
    cache_key = f"user:{user_id}"
    cached_user = cache.get(cache_key)
    if cached_user is not None:
        return cached_user

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundException("User not found")
    cache.set(cache_key, user, ttl=60)
    return user


async def update_user_profile(
    db: AsyncSession, user: User, name: str | None = None, avatar_url: str | None = None
) -> User:
    if name is not None:
        user.name = name
    if avatar_url is not None:
        user.avatar_url = avatar_url
    await db.flush()
    return user


async def update_user_settings(
    db: AsyncSession, user: User, preferred_llm: str | None = None
) -> User:
    if preferred_llm is not None:
        user.preferred_llm = preferred_llm
    await db.flush()
    return user


async def store_llm_key(db: AsyncSession, user: User, llm_api_key: str) -> User:
    user.llm_api_key = llm_api_key
    await db.flush()
    return user
