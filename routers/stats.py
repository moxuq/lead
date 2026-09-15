from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.repository import get_stats
from ..schemas.common import StatsResponse

stats_router = APIRouter(prefix='/stats', tags=['Stats'])

@stats_router.get('/', response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    stats = await get_stats(db)
    return stats
