from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Pallet(TimestampMixin, Base):
    """物理托盘，永久存在（贸易集装箱模块）。

    `code` 是贴在托盘实物上的身份码（条码/NFC 值），终身不变、全局唯一。
    托盘上的货物在 `PalletItem` 里（可变，每个装柜周期都变）；
    `customer_name` / `planned_outbound_date` 是托盘当前绑定的客户与计划出库日期
    （与 `CustomerAllocation` 同值同格式，用于对账）。

    status:
      empty    → 空托盘（可回收复用；仅保留身份码）
      staging  → 备货中（已绑定客户+日期，正在加货）
      loaded   → 已装柜（内容已写入 ContainerLoadItem 快照，等待一键出库后清空）
    """

    __tablename__ = "pallets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    # 库位：沿用项目现有 区-排-层 规范（如 A-12-03）。与托盘身份码是两个独立的码。
    shelf_location: Mapped[str | None] = mapped_column(String(32), nullable=True)
    customer_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    planned_outbound_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="empty")
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    items: Mapped[list["PalletItem"]] = relationship(
        back_populates="pallet",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class PalletItem(TimestampMixin, Base):
    """托盘当前内容（可变）。一个 (pallet, jan) 一条，quantity 为个数（非箱数）。

    这是"此刻托盘上有什么"的可变状态；不可变的装柜历史另见 ContainerLoadItem（P2）。
    """

    __tablename__ = "pallet_items"
    __table_args__ = (
        UniqueConstraint("pallet_id", "jan_code", name="uq_pallet_item_pallet_jan"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pallet_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("pallets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    jan_code: Mapped[str] = mapped_column(String(13), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    pallet: Mapped["Pallet"] = relationship(back_populates="items")
