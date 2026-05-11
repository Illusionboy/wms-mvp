from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Index, Integer, String, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.inventory_record import InventoryRecord


class Product(TimestampMixin, Base):
    __tablename__ = "products"
    __table_args__ = (
        Index("ix_products_name_jp", "name_jp"),
        Index("ix_products_name_zh", "name_zh"),
    )

    jan_code: Mapped[str] = mapped_column(String(32), primary_key=True)
    name_jp: Mapped[str] = mapped_column(String(255), nullable=False)
    name_zh: Mapped[str | None] = mapped_column(String(255), nullable=True)
    units_per_case: Mapped[int | None] = mapped_column(Integer, nullable=True)
    low_stock_alert_sent: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=false(),
    )

    inventory_records: Mapped[list[InventoryRecord]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )
