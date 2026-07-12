from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class TailoredResume(Base, TimestampMixin):
    __tablename__ = "tailored_resumes"
    __table_args__ = (
        CheckConstraint("status IN ('draft', 'finalized')", name="ck_tailored_resumes_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    job_description_id: Mapped[int] = mapped_column(
        ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False
    )
    selected_experience_bullet_ids: Mapped[list[int]] = mapped_column(
        ARRAY(Integer), nullable=False, server_default="{}"
    )
    selected_project_ids: Mapped[list[int]] = mapped_column(
        ARRAY(Integer), nullable=False, server_default="{}"
    )
    selected_skill_ids: Mapped[list[int]] = mapped_column(
        ARRAY(Integer), nullable=False, server_default="{}"
    )
    selected_education_ids: Mapped[list[int]] = mapped_column(
        ARRAY(Integer), nullable=False, server_default="{}"
    )
    scoring_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )
    llm_enhanced: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    llm_enhanced_bullets: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    resolved_content: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    rendered_pdf_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    rendered_filename: Mapped[str | None] = mapped_column(String(300), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="draft")
    finalized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
