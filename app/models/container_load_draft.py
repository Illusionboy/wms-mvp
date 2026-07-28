"""装柜出库快照：记录某(客户,计划日期)本次装柜实际扫上柜的托盘 + 散货。

- pallet_codes：扫上柜的托盘 code 列表（JSON）
- loose_items：散货（不上托盘的零散货）[{jan, qty}]（JSON）
装柜完成后 status→applied：写 OUT 出库、标记预留已出、清零上柜托盘并重置标签。
"""
from __future__ import annotations

from datetime import date

from sqlalchemy import Date, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class ContainerLoadDraft(TimestampMixin, Base):
    __tablename__ = "container_load_drafts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    planned_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="loading")  # loading / applied
    pallet_codes: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    loose_items: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
