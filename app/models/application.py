from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Application(Base, TimestampMixin):
    __tablename__ = "applications"
    __table_args__ = (
        CheckConstraint(
            "status IN ('applied', 'interview', 'offer', 'rejected', 'withdrawn')",
            name="ck_applications_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    tailored_resume_id: Mapped[int | None] = mapped_column(
        ForeignKey("tailored_resumes.id"), nullable=True
    )
    cover_letter_id: Mapped[int | None] = mapped_column(
        ForeignKey("cover_letters.id"), nullable=True
    )
    job_description_id: Mapped[int] = mapped_column(
        ForeignKey("job_descriptions.id"), nullable=False
    )
    company: Mapped[str] = mapped_column(String(200), nullable=False)
    role_title: Mapped[str] = mapped_column(String(200), nullable=False)
    date_applied: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="applied")
    notes: Mapped[str | None] = mapped_column(nullable=True)
