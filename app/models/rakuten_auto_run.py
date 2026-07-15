from sqlalchemy import JSON, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class RakutenAutoRun(TimestampMixin, Base):
    """乐天自动下载+生成快递单的一次运行记录（P2c）。每店每次一条，供"今日自动生成"面板展示。

    产物（订单 CSV + 三家快递单 + mapping.json 打包 ZIP）存磁盘
    `app/data/rakuten_auto/{store}/`（覆盖为最新），本表只存元数据/状态。
    """

    __tablename__ = "rakuten_auto_runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    store: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False)          # success / failed
    trigger: Mapped[str] = mapped_column(String(16), nullable=False, default="schedule")  # schedule / manual
    order_rows: Mapped[int | None] = mapped_column(Integer, nullable=True)   # 下载到的発送待ち订单行数
    counts: Mapped[dict | None] = mapped_column(JSON, nullable=True)         # {sagawa,yamato,post,err}
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
