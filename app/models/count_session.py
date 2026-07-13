from sqlalchemy import JSON, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class CountSession(TimestampMixin, Base):
    """批量点数会话（数据通信功能）草稿。

    一个独立的"点数工作台"：扫码/手输/Excel 收集一堆 (JAN, 数量)，产出通用结构
    （JAN+数量）供各批量模块复用（复制粘贴），并可生成微信报库文本、库存模拟、
    与托盘 QR 对账。**全程只读 WMS 库存、不写任何 StockTransaction**。

    document 存 items 列表，每条：
      {jan_code, quantity, whole_case: bool, case_size: int|null,
       case_count: int|null, name_zh: str|null}
    quantity = 手输总数 或 case_size*case_count（整箱报库）。

    status: "open"（进行中）→ "closed"（归档，可选）。前端每次变更防抖自动保存，
    另有 localStorage 即时镜像兜底，避免刷新丢失已点货。
    """

    __tablename__ = "count_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="open")
    created_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
    document: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
