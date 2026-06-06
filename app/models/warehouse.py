from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.inventory_record import InventoryRecord


class Warehouse(TimestampMixin, Base):
    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    allow_negative_stock: Mapped[bool] = mapped_column(default=False, server_default="false", nullable=False)

    inventory_records: Mapped[list[InventoryRecord]] = relationship(
        back_populates="warehouse",
    )
