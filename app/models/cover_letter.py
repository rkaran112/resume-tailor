from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class CoverLetter(Base, TimestampMixin):
    __tablename__ = "cover_letters"
    __table_args__ = (
        CheckConstraint("status IN ('draft', 'finalized')", name="ck_cover_letters_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    tailored_resume_id: Mapped[int] = mapped_column(
        ForeignKey("tailored_resumes.id"), nullable=False
    )
    job_description_id: Mapped[int] = mapped_column(
        ForeignKey("job_descriptions.id"), nullable=False
    )
    generated_text: Mapped[str] = mapped_column(nullable=False)
    edited_text: Mapped[str | None] = mapped_column(nullable=True)
    llm_generated: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    rendered_pdf_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    rendered_filename: Mapped[str | None] = mapped_column(String(300), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="draft")
    finalized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
