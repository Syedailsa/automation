import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.notebook import Notebook


async def list_user_notebooks(
    db: AsyncSession, user_id: uuid.UUID, skip: int = 0, limit: int = 50
) -> tuple[list[Notebook], int]:
    count_result = await db.execute(
        select(Notebook).where(Notebook.user_id == user_id)
    )
    total = len(count_result.scalars().all())

    result = await db.execute(
        select(Notebook)
        .where(Notebook.user_id == user_id)
        .order_by(Notebook.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all()), total


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
