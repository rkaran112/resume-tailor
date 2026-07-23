from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://resume_tailor:resume_tailor@localhost:5432/resume_tailor"

    @field_validator("database_url")
    @classmethod
    def _use_psycopg_driver(cls, v: str) -> str:
        # Managed Postgres providers (e.g. Render) hand out a bare
        # ``postgresql://`` URL, which SQLAlchemy maps to psycopg2 — a driver
        # this project doesn't install (it uses psycopg 3). Pin the driver so
        # the same env value works locally and in production.
        if v.startswith("postgresql://"):
            return "postgresql+psycopg://" + v[len("postgresql://") :]
        return v
    cors_origins: list[str] = ["http://localhost:5173"]
    log_level: str = "INFO"
    generated_resumes_dir: str = "generated/resumes"
    enable_llm_enhance: bool = False
    enable_cover_letter: bool = False
    enable_resume_import: bool = False
    anthropic_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
