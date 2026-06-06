from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.product import Product
    from app.models.stock_transaction import StockTransaction
    from app.models.warehouse import Warehouse


class InventoryRecord(TimestampMixin, Base):
    __tablename__ = "inventory_records"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="ck_inventory_records_quantity_non_negative"),
        UniqueConstraint(
            "product_jan",
            "warehouse_id",
            "customer_id",
            "location_code",
            "expiration_date",
            name="uq_inventory_records_stock_bucket",
            postgresql_nulls_not_distinct=True,
        ),
        Index("ix_inventory_records_product_jan", "product_jan"),
        Index("ix_inventory_records_warehouse_id", "warehouse_id"),
        Index("ix_inventory_records_location_code", "location_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_jan: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("products.jan_code", ondelete="RESTRICT"),
        nullable=False,
    )
    warehouse_id: Mapped[int] = mapped_column(
        ForeignKey("warehouses.id", ondelete="RESTRICT"),
        nullable=False,
    )
    customer_id: Mapped[int | None] = mapped_column(
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=True,
    )
    location_code: Mapped[str] = mapped_column(String(32), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    expiration_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    product: Mapped[Product] = relationship(back_populates="inventory_records")
    warehouse: Mapped[Warehouse] = relationship(back_populates="inventory_records")
    customer: Mapped[Customer | None] = relationship(back_populates="inventory_records")
    transactions: Mapped[list[StockTransaction]] = relationship(
        back_populates="inventory_record",
    )
