from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ExperienceEntryBase(BaseModel):
    company: str
    title: str
    location: str
    start_date: date
    end_date: date | None = None
    display_order: int = 0


class ExperienceEntryCreate(ExperienceEntryBase):
    pass


class ExperienceEntryUpdate(BaseModel):
    company: str | None = None
    title: str | None = None
    location: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    display_order: int | None = None


class ExperienceEntryRead(ExperienceEntryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
