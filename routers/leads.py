from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import AsyncSession
import pandas ad pd
import os

from ..db.repository import list_leads, get_lead_by_username, list_contacts_by_lead
from ..schemas.common import FilterQuery, LeadsAndContacsDTO, ExportRequest
from ..schemas.leads import LeadDTO
from ..db.models import LeadsNoSiteReason

leads_router = APIRouter(prefix='/leads', tags=['Leads'])

@leads_router.get('/', response_model=list[LeadDTO])
async def get_list_of_leads(has_website: bool | None = None, is_business_account: bool | None = None, no_site_reason: LeadsNoSiteReason | None = None, min_followers: int | None = None, max_followers: int | None = None, db: AsyncSession = Depends(get_db)):
    filters = FilterQuery(
        has_website=has_website,
        is_business_account=is_business_account,
        no_site_reason=no_site_reason,
        min_followers=min_followers,
        max_followers=max_followers
    )
    results = await list_leads(db, filters)
    return results

@leads_router.get('/{username}', response_model=LeadsAndContactsDTO)
async def get_leads_and_contacts_by_username(username: str, db: AsyncSession = Depends(get_db)):
    lead = await get_lead_by_username(db, username)
    contacts = await list_contacts_by_lead(db, lead.id)
    return LeadsAndContactsDTO(lead=LeadDTO.from_orm(lead), contacts=contacts)

@leads_router.post('/export')
async def post_export(export: ExportRequest, db: AsyncSession = Depends(get_db)):
    filters = FilterQuery(min_followers=export.min_followers, max_followers=export.max_followers)
    leads = await list_leads(db, filters)
    os.makedirs(os.path.dirname(export.filepath), exist_ok=True)
    data = []
    for lead in leads:
        contacts = await list_contacts_by_lead(db, lead.id)
        phones = [c.value for c in contacts if c.type == 'phone']
        emails = [c.value for c in contacts if c.type == 'email']
        whaps = [c.value for c in contacts if c.type == 'whatsapp']
        data.append({
            'username': lead.username,
            'bio': lead.bio,
            'followers_count': lead.followers_count,
            'has_website': lead.has_website,
            'phones': ', '.join(phones),
            'emails': ', '.join(emails),
            'whatsapp': ', '.join(whaps)
        })
    df = pd.DataFrame(data)
    if export.format == 'xlsx':
        df.to_excel(export.filepath, index=False)
    else:
        df.to_csv(export.filepath, index=False)
    return {"filepath": export.filepath, "count": len(leads)}
