from sqlalchemy import Boolean, CheckConstraint, ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Bullet(Base, TimestampMixin):
    __tablename__ = "bullets"
    __table_args__ = (
        CheckConstraint(
            "(experience_entry_id IS NOT NULL AND project_id IS NULL) OR "
            "(experience_entry_id IS NULL AND project_id IS NOT NULL)",
            name="ck_bullets_exactly_one_parent",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    experience_entry_id: Mapped[int | None] = mapped_column(
        ForeignKey("experience_entries.id", ondelete="CASCADE"), nullable=True
    )
    project_id: Mapped[int | None] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=True
    )
    text: Mapped[str] = mapped_column(nullable=False)
    tags: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, server_default="{}"
    )
    impact_metric: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
