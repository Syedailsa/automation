import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.output import Output


async def list_notebook_outputs(
    db: AsyncSession, notebook_id: uuid.UUID, skip: int = 0, limit: int = 50
) -> tuple[list[Output], int]:
    count_result = await db.execute(
        select(func.count()).select_from(Output).where(Output.notebook_id == notebook_id)
    )
    total = count_result.scalar()

    result = await db.execute(
        select(Output)
        .where(Output.notebook_id == notebook_id)
        .order_by(Output.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all()), total


async def get_output_by_id(db: AsyncSession, output_id: uuid.UUID) -> Output:
    result = await db.execute(select(Output).where(Output.id == output_id))
    output = result.scalar_one_or_none()
    if not output:
        raise NotFoundException("Output not found")
    return output


async def delete_output(db: AsyncSession, output: Output) -> None:
    await db.delete(output)
    await db.flush()
