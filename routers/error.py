from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.database import get_db
from ..db.models import ErrorLog
from ..db.repository import list_errors

errors_router = APIRouter(prefix='/errors', tags=['Errors'])

@errors_router.get('/', response_model=list[ErrorLog])
async def get_list_of_errors(limit: int = 20, db: AsyncSession = Depends(get_db)):
    results = await list_errors(db, limit)
    return results
