from __future__ import annotations

from sqlalchemy import BigInteger, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class TelegramAllowedUser(TimestampMixin, Base):
    """Telegram users authorised to query the WMS bot.

    Source of truth replaces TELEGRAM_QUERY_USER_IDS env var.
    Queried per-message so additions take effect instantly without bot restart.
    """

    __tablename__ = "telegram_allowed_users"
    __table_args__ = (Index("ix_telegram_allowed_users_tg_id", "telegram_user_id", unique=True),)

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    username: Mapped[str | None] = mapped_column(String(64))   # @handle, for display
    note: Mapped[str | None] = mapped_column(String(255))      # admin note
