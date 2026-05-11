from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.inventory_record import InventoryRecord


class StockTransactionType(StrEnum):
    in_ = "IN"
    out = "OUT"
    adjust = "ADJUST"


class StockTransaction(TimestampMixin, Base):
    __tablename__ = "stock_transactions"
    __table_args__ = (
        Index("ix_stock_transactions_inventory_record_id", "inventory_record_id"),
        Index("ix_stock_transactions_transaction_type", "transaction_type"),
        Index("ix_stock_transactions_source", "source"),
        Index("ix_stock_transactions_reference_id", "reference_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    inventory_record_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_records.id", ondelete="CASCADE"),
        nullable=False,
    )
    transaction_type: Mapped[StockTransactionType] = mapped_column(
        Enum(
            StockTransactionType,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            native_enum=False,
            length=16,
        ),
        nullable=False,
    )
    quantity_change: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    reference_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    inventory_record: Mapped[InventoryRecord] = relationship(back_populates="transactions")
