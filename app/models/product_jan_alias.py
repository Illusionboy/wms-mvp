from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class ProductJanAlias(TimestampMixin, Base):
    """alias_jan 是另一个JAN，实际指向同一个商品（canonical_jan）。

    1:1 简单映射，不含数量换算——外箱JAN（一箱N件）是另一套独立机制，不在此表里。
    """

    __tablename__ = "product_jan_aliases"

    alias_jan: Mapped[str] = mapped_column(String(32), primary_key=True)
    canonical_jan: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("products.jan_code", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
