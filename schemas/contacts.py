from pydantic import BaseModel, ConfigDict, field_validator, ValidationInfo, EmailStr, HttpUrl
from typing import Annotated
import phonenumbers

from ..db.models import TypeContacts, SourceContacts

class ContactDTO(BaseModel):
    lead_id: int
    type: TypeContacts
    value: str
    source: SourceContacts
    
    @field_validator("value")
    @classmethod
    def type_valid(cls, value: str, info: ValidationInfo) -> str:
        value = value.lower().strip()
        type = info.data.get("type")
        if type == TypeContacts.PHONE:
            parsed = phonenumbers.parse(value, None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError("The phone number is not valid")
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        if type == TypeContacts.EMAIL:
            try:
                email = EmailStr(value)
            except Exception as e:
                raise ValueError("Incorrect email")
            return email
        if type == TypeContacts.WEBSITE:
            try:
                url = HttpUrl(value)
            except Exception as e:
                raise ValueError("Incorrect url")
            return url