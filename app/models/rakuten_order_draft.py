from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class RakutenOrderDraft(TimestampMixin, Base):
    """乐天采购/出货需求分析草稿。

    document 存储 RakutenOrderDraftDocument（items + unresolved）。
    apply 时对 status="ok" 的行执行乐天仓库出库扣减；不足/无记录/未知JAN的行
    保留在结果中供"调货"参考，不产生库存变动。
    """

    __tablename__ = "rakuten_order_drafts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="parsed")
    document: Mapped[dict] = mapped_column(JSON, nullable=False)
