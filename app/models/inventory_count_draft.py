from __future__ import annotations

from datetime import date

from sqlalchemy import Date, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class InventoryCountDraft(TimestampMixin, Base):
    __tablename__ = "inventory_count_drafts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    original_filename: Mapped[str] = mapped_column(String(255))
    count_date: Mapped[date] = mapped_column(Date, nullable=False)
    warehouse_name: Mapped[str] = mapped_column(String(100))
    customer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="parsed")
    document: Mapped[dict] = mapped_column(JSONB, nullable=False)
