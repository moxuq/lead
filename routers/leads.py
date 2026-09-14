from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import AsyncSession

from ..db.repository import list_leads, get_lead_by_username, list_contacts_by_lead
from ..schemas.common import FilterQuery
from ..schemas.leads import LeadDTO
from ..db.models import LeadsNoSiteReason

leads_router = APIRouter(prefix='/leads', tags=['Leads'])

@leads_router.get('/', response_model=list[LeadDTO])
async def get_list_of_leads(has_website: bool | None = None, is_business_account: bool | None = None, no_site_reason: LeadsNoSiterReason | None = None, min_followers: int | None = None, max_followers: int | None = None, db: AsyncSession = Depends(get_db)):
    filters = FilterQuery(has_website=has_website, is_business_account, no_site_reason, min_followers, max_followers)
    results = await list_leads(db, filters)
    return results

