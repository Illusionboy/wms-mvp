from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.inventory_record import InventoryRecord


class Warehouse(TimestampMixin, Base):
    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    allow_negative_stock: Mapped[bool] = mapped_column(default=False, server_default="false", nullable=False)
    # 秦丝仓库(depot/storehouse)ID。按 ID 关联而不是按名字——两边任意一边改名都不会断。
    # 秦丝曾把「大阪一号店」改名为「大阪一号店备货仓」，当时按名字映射的三处全部失效。
    qinsi_depot_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, unique=True, index=True)

    inventory_records: Mapped[list[InventoryRecord]] = relationship(
        back_populates="warehouse",
    )
