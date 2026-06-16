from datetime import date

from sqlalchemy import Date, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class CustomerAllocation(TimestampMixin, Base):
    """普通仓库客户货量软预留记录。

    记录某客户在某计划出库日期需要多少件某 JAN 商品。
    status 状态机：
      waiting   → 库存不足，等待入库后自动/手动调转
      reserved  → 库存充足，已软预留（不扣减 InventoryRecord）
      shipped   → 已通过贸易出库 apply 实际出库
      cancelled → 已取消

    唯一约束 (planned_outbound_date, customer_name, jan_code) 保证 UPSERT 幂等：
    同一客户同一日期同一商品只有一条记录；客户追加需求时更新 quantity 并重新评估 status。
    """

    __tablename__ = "customer_allocations"
    __table_args__ = (
        UniqueConstraint(
            "planned_outbound_date", "customer_name", "jan_code",
            name="uq_customer_alloc_date_customer_jan",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    planned_outbound_date: Mapped[date] = mapped_column(Date, nullable=False)
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    jan_code: Mapped[str] = mapped_column(String(13), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="waiting")
    source_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
