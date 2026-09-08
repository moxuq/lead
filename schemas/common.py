from typing import Literal, Annotated
from pydantic import BaseModel, Field, ConfigDict, model_validator

from ..db.models import LeadsNoSiteReason

class ExportRequest(BaseModel):
    format: Annotated[Literal['xlsx','csv'], Field(default='xlsx')]
    filepath: Annotated[str, Field(default='./exports/leads.xlsx')]
    include_contacts: Annotated[bool, Field(default=True)]
    min_followers: Annotated[int, Field(default=0, ge=0)]
    max_followers: Annotated[int | None, Field(default=None)]
    
    model_config = ConfigDict(extra='forbid')
    
class FilterQuery(BaseModel):
    has_website: Annotated[bool | None, Field(default=None)]
    is_business_account: Annotated[bool | None, Field(default=None)]
    no_site_reason: Annotated[LeadsNoSiteReason | None, Field(default=None)]
    min_followers: Annotated[int | None, Field(default=None, ge=0)]
    max_followers: Annotated[int | None, Field(default=None, ge=0)]
    
    @model_validator(mode='after')
    def check_followers(self):
        if self.min_followers is not None and self.max_followers is not None:
            if self.min_followers > self.max_followers:
                raise ValueError('Минимальное количество подписчиков не может быть больше максимального')
        return self
    
    model_config = ConfigDict(extra='forbid')
    
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
    