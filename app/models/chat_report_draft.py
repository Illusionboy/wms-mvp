from sqlalchemy import BigInteger, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class ChatReportDraft(TimestampMixin, Base):
    __tablename__ = "chat_report_drafts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    source_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="parsed")
    document: Mapped[dict] = mapped_column(JSON, nullable=False)
