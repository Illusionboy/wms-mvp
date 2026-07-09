from datetime import date

from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class AllocationConflictLog(TimestampMixin, Base):
    """记录客户预留因库存被外部消耗（出库/调整）而被迫从 reserved 降级为 waiting 的事件。

    `_revalidate_for_jan` 在检测到某条预留从 reserved 降级为 waiting 时写入一条记录，
    `trigger` 标注降级是由哪个动作触发的（stock_out / stock_adjust / excel_upload 等），
    供操作员排查"显示已调转但实际发不出货"的情况。
    """

    __tablename__ = "allocation_conflict_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    jan_code: Mapped[str] = mapped_column(String(13), nullable=False, index=True)
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    planned_outbound_date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    current_stock: Mapped[int] = mapped_column(nullable=False)
    trigger: Mapped[str] = mapped_column(String(64), nullable=False)
