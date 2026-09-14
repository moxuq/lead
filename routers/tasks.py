from fastapi import Depends, APIRouter, HTTPException

from ..schemas.tasks import TaskCreate, TaskResponse
from ..db.database import get_db

tasks_router = APIRouter(prefix='/tasks', tags=['Tasks'])

@tasks_router.post('/', response_model=TasksResponse, status_code=201)
async def post_create_new_task(new_task: TaskCreate, db: AsyncSession = Depends(get_db)):
    pass