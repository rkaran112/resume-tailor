from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CoverLetterCreate(BaseModel):
    tailored_resume_id: int


class CoverLetterUpdate(BaseModel):
    edited_text: str


class CoverLetterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tailored_resume_id: int
    job_description_id: int
    generated_text: str
    edited_text: str | None
    llm_generated: bool
    rendered_pdf_path: str | None
    rendered_filename: str | None
    status: str
    created_at: datetime
    finalized_at: datetime | None
