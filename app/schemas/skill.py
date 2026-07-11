from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SkillBase(BaseModel):
    name: str
    category: str
    tags: list[str] = []


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    tags: list[str] | None = None


class SkillRead(SkillBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
