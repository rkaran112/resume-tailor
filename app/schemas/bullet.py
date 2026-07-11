from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator


class BulletBase(BaseModel):
    experience_entry_id: int | None = None
    project_id: int | None = None
    text: str
    tags: list[str] = []
    impact_metric: str | None = None
    is_active: bool = True

    @model_validator(mode="after")
    def check_exactly_one_parent(self) -> "BulletBase":
        if (self.experience_entry_id is None) == (self.project_id is None):
            raise ValueError(
                "exactly one of experience_entry_id or project_id must be set"
            )
        return self


class BulletCreate(BulletBase):
    pass


class BulletUpdate(BaseModel):
    experience_entry_id: int | None = None
    project_id: int | None = None
    text: str | None = None
    tags: list[str] | None = None
    impact_metric: str | None = None
    is_active: bool | None = None


class BulletRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    experience_entry_id: int | None
    project_id: int | None
    text: str
    tags: list[str]
    impact_metric: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
