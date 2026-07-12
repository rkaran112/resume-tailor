from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ApplicationStatusEvent(Base):
    """Append-only status timeline for an Application — never updated, only inserted."""

    __tablename__ = "application_status_events"
    __table_args__ = (
        CheckConstraint(
            "status IN ('applied', 'interview', 'offer', 'rejected', 'withdrawn')",
            name="ck_application_status_events_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    note: Mapped[str | None] = mapped_column(nullable=True)
