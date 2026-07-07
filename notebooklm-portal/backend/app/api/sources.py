import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.exceptions import BadRequestException
from app.database import get_db
from app.models.user import User
from app.schemas.source import SourceCreate, SourceResponse
from app.services import notebook_service, source_service

router = APIRouter(prefix="/api/notebooks", tags=["sources"])


def _parse_uuid(value: str, field_name: str = "ID") -> uuid.UUID:
    try:
        return uuid.UUID(value)
    except ValueError:
        raise BadRequestException(f"Invalid {field_name} format")


@router.post("/{notebook_id}/sources/url", response_model=SourceResponse, status_code=201)
async def add_url_source(
    notebook_id: str,
    body: SourceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    nb_id = _parse_uuid(notebook_id, "notebook_id")
    await notebook_service.get_notebook_by_id(db, nb_id, current_user.id)
    source = await source_service.create_source(
        db, nb_id, title=body.title, source_type="url", url=body.url
    )
    await notebook_service.increment_source_count(db, nb_id)
    return source


@router.post("/{notebook_id}/sources/text", response_model=SourceResponse, status_code=201)
async def add_text_source(
    notebook_id: str,
    body: SourceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    nb_id = _parse_uuid(notebook_id, "notebook_id")
    await notebook_service.get_notebook_by_id(db, nb_id, current_user.id)
    source = await source_service.create_source(
        db, nb_id, title=body.title, source_type="text", content=body.content
    )
    await notebook_service.increment_source_count(db, nb_id)
    return source


@router.delete("/{notebook_id}/sources/{source_id}")
async def delete_source(
    notebook_id: str,
    source_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    nb_id = _parse_uuid(notebook_id, "notebook_id")
    src_id = _parse_uuid(source_id, "source_id")
    await notebook_service.get_notebook_by_id(db, nb_id, current_user.id)
    source = await source_service.get_source_by_id(db, src_id, nb_id)
    await source_service.delete_source(db, source)
    await notebook_service.decrement_source_count(db, nb_id)
    return {"message": "Source deleted successfully"}


@router.get("/{notebook_id}/sources/{source_id}/content", response_model=SourceResponse)
async def get_source_content(
    notebook_id: str,
    source_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    nb_id = _parse_uuid(notebook_id, "notebook_id")
    src_id = _parse_uuid(source_id, "source_id")
    await notebook_service.get_notebook_by_id(db, nb_id, current_user.id)
    return await source_service.get_source_by_id(db, src_id, nb_id)
