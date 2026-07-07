import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.exceptions import BadRequestException
from app.database import get_db
from app.models.user import User
from app.schemas.notebook import (
    NotebookCreate,
    NotebookListResponse,
    NotebookResponse,
    NotebookUpdate,
)
from app.schemas.output import OutputListResponse
from app.schemas.source import SourceListResponse
from app.services import notebook_service, output_service, source_service

router = APIRouter(prefix="/api/notebooks", tags=["notebooks"])


def _parse_uuid(value: str, field_name: str = "ID") -> uuid.UUID:
    try:
        return uuid.UUID(value)
    except ValueError:
        raise BadRequestException(f"Invalid {field_name} format")


@router.get("", response_model=NotebookListResponse)
async def list_notebooks(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    notebooks, total = await notebook_service.list_user_notebooks(
        db, current_user.id, skip=skip, limit=limit
    )
    return NotebookListResponse(notebooks=notebooks, total=total)


@router.post("", response_model=NotebookResponse, status_code=201)
async def create_notebook(
    body: NotebookCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await notebook_service.create_notebook(
        db, current_user.id, title=body.title, description=body.description
    )


@router.get("/{notebook_id}", response_model=NotebookResponse)
async def get_notebook(
    notebook_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    nb_id = _parse_uuid(notebook_id, "notebook_id")
    return await notebook_service.get_notebook_by_id(db, nb_id, current_user.id)


@router.put("/{notebook_id}", response_model=NotebookResponse)
async def update_notebook(
    notebook_id: str,
    body: NotebookUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    nb_id = _parse_uuid(notebook_id, "notebook_id")
    notebook = await notebook_service.get_notebook_by_id(db, nb_id, current_user.id)
    return await notebook_service.update_notebook(
        db, notebook, title=body.title, description=body.description, status=body.status
    )


@router.delete("/{notebook_id}")
async def delete_notebook(
    notebook_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    nb_id = _parse_uuid(notebook_id, "notebook_id")
    notebook = await notebook_service.get_notebook_by_id(db, nb_id, current_user.id)
    await notebook_service.delete_notebook(db, notebook)
    return {"message": "Notebook deleted successfully"}


@router.get("/{notebook_id}/sources", response_model=SourceListResponse)
async def list_notebook_sources(
    notebook_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    nb_id = _parse_uuid(notebook_id, "notebook_id")
    await notebook_service.get_notebook_by_id(db, nb_id, current_user.id)
    sources, total = await source_service.list_notebook_sources(db, nb_id, skip=skip, limit=limit)
    return SourceListResponse(sources=sources, total=total)


@router.get("/{notebook_id}/outputs", response_model=OutputListResponse)
async def list_notebook_outputs(
    notebook_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    nb_id = _parse_uuid(notebook_id, "notebook_id")
    await notebook_service.get_notebook_by_id(db, nb_id, current_user.id)
    outputs, total = await output_service.list_notebook_outputs(db, nb_id, skip=skip, limit=limit)
    return OutputListResponse(outputs=outputs, total=total)
