from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class TradeShipmentDraft(TimestampMixin, Base):
    __tablename__ = "trade_shipment_drafts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="parsed")
    warehouse_name: Mapped[str] = mapped_column(String(100), nullable=False)
    document: Mapped[dict] = mapped_column(JSON, nullable=False)
