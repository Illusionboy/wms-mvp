from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.inventory_record import InventoryRecord


class InventorySourceMode(StrEnum):
    """谁是这个仓库库存的权威源。

    设计判断（ERP 联邦化）：不要让 WMS 和秦丝 ERP 继续抢同一件事，而是各管各自擅长的部分——
    这是 System of Record（权威记录）与 System of Engagement（业务交互）的标准分工。

    - 常规仓库：秦丝每天自动更新、数据准确，而 WMS 侧靠人工维护已停更 →
      权威交给 ERP，WMS 只做镜像 + 分析层
    - 乐天渠道：WMS 每天在用、数据准确，而 ERP 侧不准 → 权威留在 WMS

    这个改造的价值在于**做减法**：识别出自己的系统不该做什么，主动把权威交出去。
    """

    wms_native = "WMS_NATIVE"   # WMS 自己是权威源（默认，现状）
    erp_mirror = "ERP_MIRROR"   # 镜像秦丝 ERP 库存，WMS 侧只读（手动写入一律拒绝）


class Warehouse(TimestampMixin, Base):
    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    allow_negative_stock: Mapped[bool] = mapped_column(default=False, server_default="false", nullable=False)
    # 秦丝仓库(depot/storehouse)ID。按 ID 关联而不是按名字——两边任意一边改名都不会断。
    # 秦丝曾把「大阪一号店」改名为「大阪一号店备货仓」，当时按名字映射的三处全部失效。
    qinsi_depot_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, unique=True, index=True)
    # 库存权威源。切到 ERP_MIRROR 必须先设置 qinsi_depot_id（服务层强制校验），
    # 否则镜像无从同步。
    inventory_source_mode: Mapped[InventorySourceMode] = mapped_column(
        Enum(InventorySourceMode, native_enum=False, length=16),
        nullable=False,
        default=InventorySourceMode.wms_native,
        server_default="WMS_NATIVE",
    )

    inventory_records: Mapped[list[InventoryRecord]] = relationship(
        back_populates="warehouse",
    )
