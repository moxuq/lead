import phonenumbers
from pydantic import (
    AnyUrl,
    BaseModel,
    ConfigDict,
    EmailStr,
    TypeAdapter,
    ValidationInfo,
    field_validator,
)

from ..db.models import SourceContacts, TypeContacts


class ContactDTO(BaseModel):
    lead_id: int
    type: TypeContacts
    value: str
    source: SourceContacts

    @field_validator("value", mode="before")
    @classmethod
    def type_valid(cls, value: str, info: ValidationInfo) -> str:
        value = str(value).lower().strip()
        contact_type = info.data.get("type")
        if contact_type == TypeContacts.PHONE:
            for region in ["RU", "US", None]:
                try:
                    parsed = phonenumbers.parse(value, region)
                    if phonenumbers.is_valid_number(parsed): return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                except Exception:  # noqa: BLE001
                    raise ValueError("The phone number is not valid")
        if contact_type == TypeContacts.EMAIL:
            email_adapter = TypeAdapter(EmailStr)
            try:
                email_adapter.validate_python(value)
            except Exception:  # noqa: BLE001
                raise ValueError("Incorrect email")
            return value
        if contact_type == TypeContacts.WEBSITE:
            try:
                AnyUrl(url=value)
            except Exception:  # noqa: BLE001
                raise ValueError("Incorrect url")
            return value
        return value

    model_config = ConfigDict(extra='forbid')
