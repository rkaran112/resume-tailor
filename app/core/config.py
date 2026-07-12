from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://resume_tailor:resume_tailor@localhost:5432/resume_tailor"
    cors_origins: list[str] = ["http://localhost:5173"]
    log_level: str = "INFO"
    generated_resumes_dir: str = "generated/resumes"
    enable_llm_enhance: bool = False
    enable_cover_letter: bool = False
    enable_resume_import: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
