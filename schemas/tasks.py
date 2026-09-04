from pydantic import Field, ConfigDict, BaseModel, field_validator, ValidationInfo, ValidationError
from typing import Annotated
from datetime import datetime

from ..db.models import TasksTypes, TasksStatuses

class TaskCreate(BaseModel):
    task_type: Annotated[TasksTypes, Field()]
    query: Annotated[str, Field(min_length=1, max_length=100)]
    city: Annotated[str | None, Field(default=None, max_length=50)]
    limit: Annotated[int, Field(default=100, ge=1, le=10000)]
    
    @field_validator("city")
    @classmethod
    def check_city(cls, value: str, info: ValidationInfo) -> str:
        if not value and info.data["task_type"] == TasksTypes.LOCATION:
            raise ValueError("The city for the location-type task has not been set")
        return value
    
    @field_validator("query")
    @classmethod
    def check_hashtag(cls, value: str, info: ValidationInfo) -> str:
        if info.data["task_type"] == TasksTypes.HASHTAG and not value.startswith("#"):
            return f"#{value}"
        return value
    
    model_config = ConfigDict(extra='forbid')
    
class TaskResponce(BaseModel):
    id: int
    task_type: TasksTypes
    query: str
    city: str | None
    status: TasksStatuses
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)