from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobDescriptionCreate(BaseModel):
    company: str
    role_title: str
    raw_text: str


class JobDescriptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company: str
    role_title: str
    raw_text: str
    extracted_keywords: list[str]
    created_at: datetime
    updated_at: datetime


class MatchRequest(BaseModel):
    bullets_per_experience_entry: int = 3
    max_skills: int = 6
    max_projects: int = 2


class MatchResponse(BaseModel):
    selected_experience_bullet_ids: list[int]
    selected_project_ids: list[int]
    selected_skill_ids: list[int]
    selected_education_ids: list[int]
    scoring_metadata: dict[str, dict[int, list[str]]]
