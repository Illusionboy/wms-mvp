from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, false
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
    outer_jan: Mapped[str | None] = mapped_column(String(14), nullable=True)  # ITF-14 外箱箱码为 14 位
    low_stock_alert_sent: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=false(),
    )
    # 报损（破损品）：破损品是一条独立的商品行，jan_code = "D-" + 正常JAN。
    # 用布尔列而不是靠 jan_code LIKE 'D-%' 判断——前缀 LIKE 走不了索引，且前缀解析逻辑
    # 一旦散落到各处，任何一处漏判都是静默错误。有了这列，"默认排除破损"就是一个可复用条件。
    is_damaged: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=false(),
        index=True,
    )
    # 破损品指向其正常品JAN；正常品此列为 NULL
    damaged_of_jan: Mapped[str | None] = mapped_column(
        String(32),
        ForeignKey("products.jan_code", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    inventory_records: Mapped[list[InventoryRecord]] = relationship(
        back_populates="product",
    )
