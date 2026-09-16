from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel

from ..schemas.tasks import TaskCreate, TaskResponse
from ..db.database import get_db
from ..db.repository import create_task, list_tasks, get_task, update_task_status, list_tasks_by_status
from ..db.models import TasksStatuses

tasks_router = APIRouter(prefix='/tasks', tags=['Tasks'])

@tasks_router.post('/', response_model=TaskResponse, status_code=201)
async def post_create_new_task(new_task: TaskCreate, db: AsyncSession = Depends(get_db)):
    result = await create_task(db, new_task)
    return result
    
@tasks_router.get('/', response_model=list[TaskResponse])
async def get_list_of_tasks(status: TasksStatuses | None = None, db: AsyncSession = Depends(get_db)):
   result = await list_tasks_by_status(db, status)
   return result

@tasks_router.get('/{task_id}', response_model=TaskResponse)
async def get_task_by_id(task_id: int, db: AsyncSession = Depends(get_db)):
    result = await get_task(db, task_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f'Task {task_id} not found')
    return result

class UpdateStatusRequest(BaseModel):
   status: TasksStatuses

@tasks_router.put('/{task_id}/status')
async def put_status_by_task_id(task_id: int, data: UpdateStatusRequest, db: AsyncSession = Depends(get_db)):
    task = await get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f'Task {task_id} not found')
    await update_task_status(db, task_id, data.status)
    return {"message": "Status updated"}
