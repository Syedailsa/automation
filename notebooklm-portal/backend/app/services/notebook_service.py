import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.notebook import Notebook
from app.services.cache_service import cache

"""Notebook CRUD operations."""


async def list_user_notebooks(
    db: AsyncSession, user_id: uuid.UUID, skip: int = 0, limit: int = 50
) -> tuple[list[Notebook], int]:
    cache_key = f"notebooks:list:{user_id}:{skip}:{limit}"
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    count_result = await db.execute(
        select(func.count()).select_from(Notebook).where(Notebook.user_id == user_id)
    )
    total = count_result.scalar()

    result = await db.execute(
        select(Notebook)
        .where(Notebook.user_id == user_id)
        .order_by(Notebook.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    notebooks = list(result.scalars().all())
    result_tuple = (notebooks, total)
    cache.set(cache_key, result_tuple, ttl=120)
    return result_tuple


async def create_notebook(
    db: AsyncSession, user_id: uuid.UUID, title: str, description: str | None = None
) -> Notebook:
    notebook = Notebook(user_id=user_id, title=title, description=description)
    db.add(notebook)
    await db.flush()
    return notebook


async def get_notebook_by_id(
    db: AsyncSession, notebook_id: uuid.UUID, user_id: uuid.UUID
) -> Notebook:
    result = await db.execute(
        select(Notebook).where(
            Notebook.id == notebook_id, Notebook.user_id == user_id
        )
    )
    notebook = result.scalar_one_or_none()
    if not notebook:
        raise NotFoundException("Notebook not found")
    return notebook


async def update_notebook(
    db: AsyncSession,
    notebook: Notebook,
    title: str | None = None,
    description: str | None = None,
    status: str | None = None,
) -> Notebook:
    if title is not None:
        notebook.title = title
    if description is not None:
        notebook.description = description
    if status is not None:
        notebook.status = status
    await db.flush()
    return notebook


async def delete_notebook(db: AsyncSession, notebook: Notebook) -> None:
    await db.delete(notebook)
    await db.flush()


async def increment_source_count(db: AsyncSession, notebook_id: uuid.UUID) -> None:
    result = await db.execute(select(Notebook).where(Notebook.id == notebook_id))
    notebook = result.scalar_one_or_none()
    if notebook:
        notebook.source_count = (notebook.source_count or 0) + 1
        await db.flush()


async def decrement_source_count(db: AsyncSession, notebook_id: uuid.UUID) -> None:
    result = await db.execute(select(Notebook).where(Notebook.id == notebook_id))
    notebook = result.scalar_one_or_none()
    if notebook and (notebook.source_count or 0) > 0:
        notebook.source_count = notebook.source_count - 1
        await db.flush()
