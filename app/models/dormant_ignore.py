"""滞销品「忽略」标记：被标记的 JAN 默认不出现在滞销品统计里（可切换显示全部）。"""
from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class DormantIgnore(TimestampMixin, Base):
    __tablename__ = "dormant_ignores"

    jan_code: Mapped[str] = mapped_column(String(32), primary_key=True)
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
