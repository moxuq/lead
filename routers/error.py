from fastapi import APIRouter, Depends

from ..db.repository import list_errors
from ..db.models import ErrorLog

errors_router = APIRouter(prefix='/errors', tags=['Errors'])

@errors_router.get('/', response_model=list[ErrorLog])
async def get_list_of_errors(offset: int = 20, 