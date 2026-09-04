from pydantic import Field, ConfigDict, BaseModel, field_validator
from datetime import datetime
from typing import Annotated

from ..db.models import LeadsNoSiteReason

class LeadDTO(BaseModel):
    username: Annotated[str, Field()]
    url: Annotated[str, Field()]
    name: Annotated[str | None, Field()]
    category: Annotated[str | None, Field()]
    bio_text: Annotated[str | None, Field()]
    is_business_account: Annotated[bool, Field(default=False)]
    is_verified: Annotated[bool, Field(default=False)]
    followers_count: Annotated[int, Field(default=0)]
    has_website: Annotated[bool, Field()]
    no_site_reason: Annotated[LeadsNoSiteReason | None, Field()]
    address: Annotated[str | None, Field()]
    
    model_config = ConfigDict(extra='forbid')
    
class LeadExport(BaseModel):
    username: Annotated[str, Field(alias="Username")]
    name: Annotated[str | None, Field(alias="Name")]
    category: Annotated[str | None, Field(alias="Category")]
    bio_text: Annotated[str | None, Field(alias="Bio")]
    followers_count: Annotated[int, Field(alias="Subscribers")]
    is_business_account: Annotated[bool, Field(alias="IsBusiness")]
    is_verified: Annotated[bool, Field(alias="IsVerified")]
    no_site_reason: Annotated[LeadsNoSiteReason, Field(alias="NoSiteReason")]
    address: Annotated[str | None, Field(alias="Address")]
    parsed_at: Annotated[datetime, Field(alias="ParsedAt")]
    
    @field_validator("no_site_reason", mode="before")
    @classmethod
    def convert_enum_to_str(cls, value):
        if isinstance(value, LeadsNoSiteReason):
            return value.value
        return value
    
    model_config = ConfigDict(from_attributes=True)