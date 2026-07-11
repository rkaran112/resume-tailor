from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class EducationEntryBase(BaseModel):
    institution: str
    degree: str
    field: str
    start_date: date
    end_date: date | None = None
    gpa: str | None = None


class EducationEntryCreate(EducationEntryBase):
    pass


class EducationEntryUpdate(BaseModel):
    institution: str | None = None
    degree: str | None = None
    field: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    gpa: str | None = None


class EducationEntryRead(EducationEntryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
