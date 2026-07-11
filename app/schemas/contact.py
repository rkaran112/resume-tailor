from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ContactLink(BaseModel):
    label: str
    url: str


class ContactInfoBase(BaseModel):
    name: str
    email: str
    phone: str
    location: str
    links: list[ContactLink] = []


class ContactInfoUpsert(ContactInfoBase):
    pass


class ContactInfoRead(ContactInfoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
