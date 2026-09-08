from typing import Literal, Annotated
from pydantic import BaseModel, Field, ConfigDict

from ..db.models import LeadsNoSiteReason

class ExportRequest(BaseModel):
    format: Annotated[Literal['xlsx','csv'], Field(default='xlsx')]
    filepath: Annotated[str, Field(default='./exports/leads.xlsx')]
    include_contacts: Annotated[bool, Field(default=True)]
    min_followers: Annotated[int, Field(default=0, ge=0)]
    max_followers: Annotated[int | None, Field(default=None)]
    
    model_config = ConfigDict(extra='forbid')
    
class FilterQuery(BaseModel):
    has_website: bool | None
    is_business_account: bool | None
    no_site_reason: LeadsNoSiteReason | None
    min_followers: int | None
    max_followers: int | None
    
    model_config = ConfigDict(from_attributes=True)
    
class StatsResponse(BaseModel):
    total_accounts: int
    active_accounts: int
    banned_accounts: int
    total_tasks: int
    total_leads: int
    leads_with_website: int
    leads_no_website: int
    total_contacts: int
    
    model_config = ConfigDict(from_attributes=True)
    