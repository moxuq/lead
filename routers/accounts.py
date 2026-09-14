from ..db.database import get_db
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, APIRouter
from ..schemas.accounts import AccountResponse, AccountCreate
from ..db.repository import add_account, list_accounts

accounts_router = APIRouter(prefix='/accounts', tags=['Account'])

@accounts_router.post('/', response_model=AccountResponse, status_code=201)
async def post_create_account(new_account: AccountCreate, db: AsyncSession = Depends(get_db)):
    try:
        result = await add_account(db, new_account)
    except ValueError:
        raise HTTPException(status_code=400, detail='Account is already exists')
    return result

@accounts_router.get('/', response_model=list[AccountResponse])
async def get_list_of_accounts(db: AsyncSession = Depends(get_db)):
    results = await list_accounts(db)
    return results
