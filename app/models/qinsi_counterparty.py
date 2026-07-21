"""秦丝供应商/客户缓存 + 简称映射。

用于微信报库/秦丝回填时按名称（简繁/日文发音/简称）匹配到秦丝的供应商/客户，
拿到 qinsi_id 用于回填。数据由 admin 点「同步」从秦丝分页拉取。
"""
from __future__ import annotations

from sqlalchemy import BigInteger, Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class QinsiCounterparty(TimestampMixin, Base):
    __tablename__ = "qinsi_counterparties"
    __table_args__ = (
        UniqueConstraint("kind", "qinsi_id", name="uq_qinsi_counterparty_kind_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    kind: Mapped[str] = mapped_column(String(16), nullable=False, index=True)   # supplier / customer
    qinsi_id: Mapped[int] = mapped_column(BigInteger, nullable=False)           # 秦丝 supplierId / clientId
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    canonical: Mapped[str] = mapped_column(String(255), nullable=False, index=True, default="")  # 归一化名(简繁/去噪)
    reading: Mapped[str] = mapped_column(String(512), nullable=False, default="")                # 发音(日文罗马音+拼音)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")

    aliases: Mapped[list["QinsiCounterpartyAlias"]] = relationship(
        back_populates="counterparty", cascade="all, delete-orphan"
    )


class QinsiCounterpartyAlias(TimestampMixin, Base):
    __tablename__ = "qinsi_counterparty_aliases"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    counterparty_id: Mapped[int] = mapped_column(
        ForeignKey("qinsi_counterparties.id", ondelete="CASCADE"), nullable=False, index=True
    )
    alias: Mapped[str] = mapped_column(String(255), nullable=False)               # 用户输入的简称原文
    canonical: Mapped[str] = mapped_column(String(255), nullable=False, default="")  # 简称归一化

    counterparty: Mapped["QinsiCounterparty"] = relationship(back_populates="aliases")
