from __future__ import annotations

from datetime import date

from sqlalchemy import Date, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class QinsiScrapeCache(TimestampMixin, Base):
    """Stores the last scraped result per (from_date, to_date) date range.

    One row per unique date window; upserted on every fresh scrape so the
    cache always reflects the latest successful pull for that window.
    """

    __tablename__ = "qinsi_scrape_cache"
    __table_args__ = (
        UniqueConstraint("from_date", "to_date", name="uq_qinsi_scrape_cache_dates"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    from_date: Mapped[date] = mapped_column(Date, nullable=False)
    to_date: Mapped[date] = mapped_column(Date, nullable=False)
    records_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
