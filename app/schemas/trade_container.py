"""贸易集装箱模块 DTO（P1：托盘 + 加货 + 库位绑定 + 查询）。

对账、装柜快照、一键出库（Container / ContainerLoadItem）属 P2，届时再补。
"""
from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

# 托盘身份码：贴在托盘上的条码/NFC 值，宽松校验（不同印制来源长度不一）
PalletCode = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=64)]
# 库位码：沿用项目现有 区-排-层 规范（如 A-12-03）——与 schemas/inventory.LocationCode 一致
LocationCode = Annotated[
    str,
    StringConstraints(strip_whitespace=True, pattern=r"^[A-Z]-\d{2}-\d{2}$"),
]
JanInput = Annotated[str, StringConstraints(strip_whitespace=True, min_length=5, max_length=32)]
CustomerName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]


# ── 读 ──────────────────────────────────────────────────────────────────────
class PalletItemRead(BaseModel):
    jan_code: str
    quantity: int
    product_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PalletRead(BaseModel):
    id: int
    code: str
    shelf_location: str | None
    customer_name: str | None
    planned_outbound_date: date | None
    status: str
    note: str | None
    items: list[PalletItemRead] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PalletCandidateRead(BaseModel):
    """加货候选：某托盘绑定的 (客户, 日期) 下的预留行（reserved + waiting 并集）。"""
    jan_code: str
    product_name: str | None = None
    reserved_quantity: int          # 预留需求量
    status: str                     # reserved / waiting
    current_stock: int | None = None  # WMS 在库（中性信息，仅供参考；WMS 滞后实物）
    on_pallet_quantity: int = 0     # 该 JAN 当前已在此托盘上的数量


class DailyCustomerRead(BaseModel):
    """某计划出库日期下、有预留的客户（建空托盘时只能从此列表选）。"""
    customer_name: str
    reserved_count: int
    waiting_count: int


# ── 写 ──────────────────────────────────────────────────────────────────────
class PalletCreate(BaseModel):
    code: PalletCode
    planned_outbound_date: date
    customer_name: CustomerName


class PalletItemInput(BaseModel):
    jan_code: JanInput
    quantity: Annotated[int, Field(gt=0)]


class PalletAddItems(BaseModel):
    items: Annotated[list[PalletItemInput], Field(min_length=1)]


class PalletItemSetQuantity(BaseModel):
    quantity: Annotated[int, Field(ge=0)]  # 0 = 从托盘移除该 JAN


class PalletPlaceLocation(BaseModel):
    pallet_code: PalletCode
    location_code: LocationCode
