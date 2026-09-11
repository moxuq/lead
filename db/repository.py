from collections.abc import Sequence
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.leads import LeadDTO

from ..db.models import (
    AccountPool,
    AccountStatuses,
    Lead,
    RawProfile,
    SearchTask,
    TasksStatuses,
    Contact
)
from ..schemas.accounts import AccountCreate
from ..schemas.tasks import TaskCreate
from ..schemas.common import FilterQuery, StatsResponse

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

async def list_accounts(db: AsyncSession) -> Sequence[AccountPool]:
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

async def list_tasks(db: AsyncSession) -> Sequence[SearchTask] | None:
    tasks = (await db.execute(select(SearchTask))).scalars().all()
    return tasks

async def profile_exists(db: AsyncSession, username: str) -> bool:
    profile = (await db.execute(select(RawProfile).where(RawProfile.username == username))).scalar_one_or_none()
    return profile is not None

async def create_profile(db: AsyncSession, username: str, url: str, task_id: int) -> RawProfile:
    exists = await profile_exists(db, username)
    if exists == True:
        return profile
    new_profile = RawProfile(username=username, url=url, task_id=task_id)
    db.add(new_profile)
    await db.commit()
    await db.refresh(new_profile)
    return new_profile

async def create_lead(db: AsyncSession, data: LeadDTO, profile_id: int) -> Lead:
    new_lead = Lead(**data.model_dump(), profile_id=profile_id)
    db.add(new_lead)
    await db.commit()
    await db.refresh(new_lead)
    return new_lead

async def get_lead_by_username(db: AsyncSession, username: str) -> Lead | None:
    lead = (await db.execute(select(Lead).join(RawProfile)
    .where(RawProfile.username == username))).scalar_one_or_none()
    return lead

async def list_leads(db: AsyncSession, filter: FilterQuery) -> list[Lead]:
    stmt = select(Lead)
    if filter.has_website is not None:
        stmt = stmt.where(Lead.has_website == filter.has_website)
    if filter.is_business_account is not None:
        stmt = stmt.where(Lead.is_business_account == filter.is_business_account)
    if filter.no_site_reason is not None:
        stmt = stmt.where(Lead.no_site_reason == filter.no_site_reason)
    if filter.min_followers is not None:
        stmt = stmt.where(Lead.followers_count >= filter.min_followers)
    if filter.max_followers is not None:
        stmt = stmt.where(Lead.followers_count <= filter.max_followers)
    result = (await db.execute(stmt)).scalars().all()
    return result

async def get_stats(db: AsyncSession) -> StatsResponse:
    total_accounts = await db.scalar(select(func.count(AccountPool.id)))
    active_accounts = await db.scalar(
        select(func.count(AccountPool.id)).where(AccountPool.status == AccountStatuses.AVAILABLE)
    )
    banned_accounts = await db.scalar(
        select(func.count(AccountPool.id)).where(AccountPool.status == AccountStatuses.BAN)
    )
    total_tasks = await db.scalar(select(func.count(SearchTask.id)))
    total_leads = await db.scalar(select(func.count(Lead.id)))
    leads_with_website = await db.scalar(
        select(func.count(Lead.id)).where(Lead.has_website == True)
    )
    leads_no_website = await db.scalar(
        select(func.count(Lead.id)).where(Lead.has_website == False)
    )
    total_contacts = await db.scalar(select(func.count(Contact.id)))
    return StatsResponse(
        total_accounts=total_accounts or 0,
        active_accounts=active_accounts or 0,
        banned_accounts=banned_accounts or 0,
        total_tasks=total_tasks or 0,
        total_leads=total_leads or 0,
        leads_with_website=leads_with_website or 0,
        leads_no_website=leads_no_website or 0,
        total_contacts=total_contacts or 0,
    )

