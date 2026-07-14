from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class RakutenCredential(TimestampMixin, Base):
    """乐天店铺账号凭据（P2 自动下载用）。每店一条。

    每店需要两组凭据：
      - RMS 登录：`rms_login_id` + `rms_password_enc`（登录 rms.rakuten.co.jp 后台）
      - CSV 下载专用：`csv_user` + `csv_password_enc`（データダウンロード 页下载区单独输入）

    密码字段以对称加密密文存储（见 app/services/crypto.py），**绝不明文入库、绝不返回前端**。
    `store` 与 P1 快递单生成的店铺标识一致（mgmt_no 前缀，如 "1" / "2"）。
    """

    __tablename__ = "rakuten_credentials"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    store: Mapped[str] = mapped_column(String(16), nullable=False, unique=True)
    store_label: Mapped[str | None] = mapped_column(String(64), nullable=True)  # 展示名，如"一号店"
    rms_login_id: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    rms_password_enc: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    csv_user: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    csv_password_enc: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
