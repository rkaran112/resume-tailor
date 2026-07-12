from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

ApplicationStatus = Literal["applied", "interview", "offer", "rejected", "withdrawn"]


class ApplicationCreate(BaseModel):
    tailored_resume_id: int | None = None
    cover_letter_id: int | None = None
    job_description_id: int
    company: str
    role_title: str
    date_applied: date
    status: ApplicationStatus = "applied"
    notes: str | None = None


class ApplicationUpdate(BaseModel):
    company: str | None = None
    role_title: str | None = None
    date_applied: date | None = None
    notes: str | None = None
    cover_letter_id: int | None = None


class ApplicationStatusChange(BaseModel):
    status: ApplicationStatus
    note: str | None = None


class ApplicationStatusEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    changed_at: datetime
    note: str | None


class ApplicationRead(BaseModel):
    id: int
    tailored_resume_id: int | None
    cover_letter_id: int | None
    job_description_id: int
    company: str
    role_title: str
    date_applied: date
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime
    status_events: list[ApplicationStatusEventRead] = []
