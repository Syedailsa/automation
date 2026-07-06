from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.services import output_service

router = APIRouter(prefix="/api/outputs", tags=["outputs"])


@router.delete("/{output_id}")
async def delete_output(
    output_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    output = await output_service.get_output_by_id(db, output_id)
    await output_service.delete_output(db, output)
    return {"message": "Output deleted successfully"}
