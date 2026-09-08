from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from ..schemas.accounts import AccountCreate, AccountResponse
from ..db.models import AccountPool, AccountStatuses

async def add_account(db: AsyncSession, user: AccountCreate) -> AccountPool:
    new_user = AccountPool(**user.model_dump())
    db.add(new_user)
    await db.commit()
    db.refresh(new_user)
    return AccountResponse.model_validate(new_user)
    
async def get_account_by_username(db: AsyncSession, username: str) -> AccountPool | None:
    account = (await db.execute(select(AccountPool).where(AccountPool.username == username))).scalar_one_or_none()
    return AccountResponse.model_validate(account)

async def get_available_account(db: AsyncSession) -> list[AccountPool] | None:
    accounts = (await db.execute(select(AccountPool).where(AccountPool.status == AccountStatuses.AVAILABLE))).scalars().all()
    return accounts
    
async def update_account_status(db: AsyncSession, account: AccountPool, status: AccountStatuses) -> AccountResponse:
    await db.execute(update(AccountPool).where(AccountPool.id == account.id).values(AccountPool.status = status))
    await db.commit()
    
async def update_last_used(db: AsyncSession):
    pass
