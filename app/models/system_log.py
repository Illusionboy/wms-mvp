from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class SystemLog(TimestampMixin, Base):
    """通用系统异常/事件日志，供「日志查看」页面统一展示排查。

    不局限于客户预留场景：负库存出库（category="negative_stock"）、
    预留冲突（category="allocation_conflict"，与 AllocationConflictLog 同时写入，
    后者保留结构化字段供客户预留页面详情展示，本表只存一条摘要供全局检索）等
    后续异常情况都可复用 `write_system_log` 写入本表。
    """

    __tablename__ = "system_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    level: Mapped[str] = mapped_column(String(16), nullable=False, default="warning")
    message: Mapped[str] = mapped_column(Text, nullable=False)
    jan_code: Mapped[str | None] = mapped_column(String(13), nullable=True, index=True)
    warehouse_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
