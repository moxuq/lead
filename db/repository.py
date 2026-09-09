from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timedelta

from ..schemas.accounts import AccountCreate, AccountResponse
from ..db.models import AccountPool, AccountStatuses

async def add_account(db: AsyncSession, user: AccountCreate) -> AccountPool:
    db_acc = await get_account_by_username(db, user.username)
    if db_acc is not None:
        raise ValueError(f"Account with username: {user.username} is already exists")
    new_user = AccountPool(**user.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return account
    
async def get_account_by_username(db: AsyncSession, username: str) -> AccountPool | None:
    account = (await db.execute(select(AccountPool).where(AccountPool.username == username))).scalar_one_or_none()
    return account

async def get_available_account(db: AsyncSession) -> AccountPool | None:
    cooldown = datetime.now(timezone.utc) - timedelta(minutes=30)
    accounts = (await db.execute(select(AccountPool)
    .where((AccountPool.last_used_at == None) |
    (AccountPool.last_used_at < cooldown)).order_by(AccountPool.last_used_at.asc()).limit(1))).scalar_one_or_none()
    return accounts
    
async def update_account_status(db: AsyncSession, account: AccountPool, status: AccountStatuses) -> AccountResponse:
    await db.execute(update(AccountPool).where(AccountPool.id == account.id).values(status = status))
    await db.commit()
    
async def update_last_used(db: AsyncSession, account_id: int) -> None:
    await db.execute(update(AccountPool).where(AccountPool.id==account_id).values(last_used_at=datetime.now(timezone.utc)))
	await db.commit()

