from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class TailoredResumeCreate(BaseModel):
    job_description_id: int
    selected_experience_bullet_ids: list[int] = []
    selected_project_ids: list[int] = []
    selected_skill_ids: list[int] = []
    selected_education_ids: list[int] = []
    scoring_metadata: dict[str, Any] = {}


class TailoredResumeUpdate(BaseModel):
    selected_experience_bullet_ids: list[int] | None = None
    selected_project_ids: list[int] | None = None
    selected_skill_ids: list[int] | None = None
    selected_education_ids: list[int] | None = None
    scoring_metadata: dict[str, Any] | None = None


class EnhancedBulletOut(BaseModel):
    bullet_id: int
    original: str
    suggested: str
    flagged: bool


class EnhanceResponse(BaseModel):
    bullets: list[EnhancedBulletOut]


class AcceptEnhancedBulletsRequest(BaseModel):
    accepted: dict[int, str]


class TailoredResumeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_description_id: int
    selected_experience_bullet_ids: list[int]
    selected_project_ids: list[int]
    selected_skill_ids: list[int]
    selected_education_ids: list[int]
    scoring_metadata: dict[str, Any]
    llm_enhanced: bool
    llm_enhanced_bullets: dict[str, Any] | None
    resolved_content: dict[str, Any] | None
    rendered_pdf_path: str | None
    rendered_filename: str | None
    status: str
    created_at: datetime
    finalized_at: datetime | None
