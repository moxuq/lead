from pydantic import Field, ConfigDict, BaseModel
from typing import Annotated
from datetime import datetime

from ..db.models import AccountStatuses

class AccountCreate(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=30)]
    password: Annotated[str, Field(min_length=6)]
    proxy_url: Annotated[str | None, Field(default=None, pattern=r"^(http|https|socks5)://.+:\d+$")]
    
    model_config = ConfigDict(extra='forbid')
    
class AccountResponce(BaseModel):
    id: int
    username: str
    proxy_url: str | None
    status: AccountStatuses
    