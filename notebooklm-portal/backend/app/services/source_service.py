import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.source import Source


async def list_notebook_sources(
    db: AsyncSession, notebook_id: uuid.UUID, skip: int = 0, limit: int = 50
) -> tuple[list[Source], int]:
    count_result = await db.execute(
        select(Source).where(Source.notebook_id == notebook_id)
    )
    total = len(count_result.scalars().all())

    result = await db.execute(
        select(Source)
        .where(Source.notebook_id == notebook_id)
        .order_by(Source.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all()), total


async def create_source(
    db: AsyncSession,
    notebook_id: uuid.UUID,
    title: str,
    source_type: str,
    url: str | None = None,
    content: str | None = None,
    file_path: str | None = None,
) -> Source:
    source = Source(
        notebook_id=notebook_id,
        title=title,
        source_type=source_type,
        url=url,
        content=content,
        file_path=file_path,
    )
    db.add(source)
    await db.flush()
    return source


async def get_source_by_id(
    db: AsyncSession, source_id: uuid.UUID, notebook_id: uuid.UUID
) -> Source:
    result = await db.execute(
        select(Source).where(
            Source.id == source_id, Source.notebook_id == notebook_id
        )
    )
    source = result.scalar_one_or_none()
    if not source:
        raise NotFoundException("Source not found")
    return source


async def delete_source(db: AsyncSession, source: Source) -> None:
    await db.delete(source)
    await db.flush()
