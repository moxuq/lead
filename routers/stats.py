from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.database import get_db
from ..db.repository import get_stats
from ..schemas.common import StatsResponse

stats_router = APIRouter(prefix='/stats', tags=['Stats'])

@stats_router.get('/', response_model=StatsResponse)
async def get_all_stats(db: AsyncSession = Depends(get_db)):
    stats = await get_stats(db)
    return stats
