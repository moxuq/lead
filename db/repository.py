from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timedelta, timezone

from ..schemas.accounts import AccountCreate
from ..schemas.tasks import TaskCreate
from ..db.models import AccountPool, AccountStatuses, SearchTask, TasksTypes, TasksStatuses, RawProfile, Lead, ParseStatus

async def add_account(db: AsyncSession, user: AccountCreate) -> AccountPool | None:
    db_acc = await get_account_by_username(db, user.username)
    if db_acc is not None:
        raise ValueError(f"Account with username: {user.username} is already exists")
    new_user = AccountPool(**user.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
    
async def get_account_by_username(db: AsyncSession, username: str) -> AccountPool | None:
    account = (await db.execute(select(AccountPool).where(AccountPool.username == username))).scalar_one_or_none()
    return account

async def get_available_account(db: AsyncSession) -> AccountPool | None:
    cooldown = datetime.now(timezone.utc) - timedelta(minutes=30)
    accounts = (await db.execute(select(AccountPool)
    .where(AccountPool.status == AccountStatuses.AVAILABLE)
    .where((AccountPool.last_used_at == None) |
    (AccountPool.last_used_at < cooldown)).order_by(AccountPool.last_used_at.asc()).limit(1))).scalar_one_or_none()
    return accounts
    
async def update_account_status(db: AsyncSession, account: AccountPool, status: AccountStatuses) -> None:
    await db.execute(update(AccountPool).where(AccountPool.id == account.id).values(status = status))
    await db.commit()
    
async def update_last_used(db: AsyncSession, account_id: int) -> None:
    await db.execute(update(AccountPool).where(AccountPool.id==account_id).values(last_used_at=datetime.now(timezone.utc)))
    await db.commit()

async def increment_parsed_count(db: AsyncSession, account_id: int) -> None:
    await db.execute(update(AccountPool).where(AccountPool.id == account_id).values(profiles_parsed_count=AccountPool.profiles_parsed_count+1))
    await db.commit()
    
async def list_accounts(db: AsyncSession) -> list[AccountPool]:
    accounts = (await db.execute(select(AccountPool))).scalars().all()
    return accounts

async def create_task(db: AsyncSession, task: TaskCreate) -> SearchTask:
    new_task = SearchTask(**task.model_dump())
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task
    
async def get_task(db: AsyncSession, id: int) -> SearchTask | None:
    task = (await db.execute(select(SearchTask).where(SearchTask.id == id))).scalar_one_or_none()
    return task

async def update_task_status(db: AsyncSession, id: int, status: TasksStatuses) -> None:
    await db.execute(update(SearchTask).where(SearchTask.id == id).values(status = status))
    await db.commit()
    
async def list_tasks(db: AsyncSession) -> list[SearchTask] | None:
    tasks = (await db.execute(select(SearchTask))).scalars().all()
    return tasks

async def profile_exists(db: AsyncSession, usernmae: str) -> bool:
    profile = (await db.execute(select(RawProfile).where(RawProfile.username == username))).scalar_one_or_none()
    if profile is not None:
        return True
    return False
    
async def create_profile(db: AsyncSession, username: str, url: str, task_id: int) -> RawProfile:
    exists = await profile_exists(db, username)
    if exists == True:
        profile = (await db.execute(select(RawProfile).where(RawProfile.username = username)))
        return profile





