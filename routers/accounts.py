from ..db.database import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, APIRouter
from ..schemas.accounts import AccountResponse, AccountCreate
from ..db.repository import add_account, list_accounts

accounts_router = APIRouter(prefix='/accounts', tags=['Account'])

@accounts_router.post('/', response_model=AccountResponse)
async def post_create_account(new_account: AccountCreate, db: AsyncSession = Depends(get_db)):
    result = await add_account(db, new_account)
    return result

@accounts_router.get('/', response_model=list[AccountResponse])
async def get_list_of_accounts(db: AsyncSession = Depends(get_db)):
    results = await list_accounts(db)
    return results
