from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.source import SourceCreate, SourceResponse
from app.services import notebook_service, source_service

router = APIRouter(prefix="/api/notebooks", tags=["sources"])


@router.post("/{notebook_id}/sources/url", response_model=SourceResponse, status_code=201)
async def add_url_source(
    notebook_id: str,
    body: SourceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await notebook_service.get_notebook_by_id(db, notebook_id, current_user.id)
    return await source_service.create_source(
        db, notebook_id, title=body.title, source_type="url", url=body.url
    )


@router.post("/{notebook_id}/sources/text", response_model=SourceResponse, status_code=201)
async def add_text_source(
    notebook_id: str,
    body: SourceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await notebook_service.get_notebook_by_id(db, notebook_id, current_user.id)
    return await source_service.create_source(
        db, notebook_id, title=body.title, source_type="text", content=body.content
    )


@router.delete("/{notebook_id}/sources/{source_id}")
async def delete_source(
    notebook_id: str,
    source_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await notebook_service.get_notebook_by_id(db, notebook_id, current_user.id)
    source = await source_service.get_source_by_id(db, source_id, notebook_id)
    await source_service.delete_source(db, source)
    return {"message": "Source deleted successfully"}


@router.get("/{notebook_id}/sources/{source_id}/content", response_model=SourceResponse)
async def get_source_content(
    notebook_id: str,
    source_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await notebook_service.get_notebook_by_id(db, notebook_id, current_user.id)
    return await source_service.get_source_by_id(db, source_id, notebook_id)
