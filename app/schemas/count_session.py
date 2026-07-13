"""批量点数模块（数据通信功能）DTO。

通信数据结构只需 JAN + 数量；其余字段（whole_case/case_size/case_count/name_zh）
为工作台编辑辅助，随草稿一起持久化，避免刷新丢失。
"""
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

JanInput = Annotated[str, StringConstraints(strip_whitespace=True, min_length=5, max_length=32)]


# ── 点数条目 ────────────────────────────────────────────────────────────────
class CountItem(BaseModel):
    jan_code: JanInput
    quantity: Annotated[int, Field(ge=0)]
    whole_case: bool = False
    case_size: int | None = Field(default=None, ge=1)     # 整箱报库的箱入数（默认取 units_per_case，可改）
    case_count: int | None = Field(default=None, ge=0)    # 箱数
    name_zh: str | None = None                            # 展示/微信文本用；新品可手输
    is_new: bool = False                                  # 目录外新品（前端 badge）

    model_config = ConfigDict(from_attributes=True)


# ── 会话 CRUD ───────────────────────────────────────────────────────────────
class CountSessionUpsert(BaseModel):
    name: str | None = None
    note: str | None = None
    items: list[CountItem] = Field(default_factory=list)


class CountSessionRead(BaseModel):
    id: int
    name: str | None
    note: str | None
    status: str
    items: list[CountItem] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Excel 导入 ──────────────────────────────────────────────────────────────
class ImportedItem(BaseModel):
    jan_code: str
    quantity: int
    name_zh: str | None = None
    units_per_case: int | None = None
    is_new: bool = False           # JAN 不在商品目录
    customer_name: str | None = None  # sheet 名（客户/供应商），仅展示、不进通信数据


class ImportResult(BaseModel):
    items: list[ImportedItem] = Field(default_factory=list)
    new_count: int = 0             # 目录外新品条数


# ── 库存模拟 ────────────────────────────────────────────────────────────────
class SimulateLine(BaseModel):
    jan_code: JanInput
    quantity: Annotated[int, Field(ge=0)]


class SimulateRequest(BaseModel):
    items: Annotated[list[SimulateLine], Field(min_length=1)]
    warehouse_id: int
    exclude_reserved: bool = False


class SimulateRow(BaseModel):
    jan_code: str
    name_zh: str | None = None
    need: int
    current_stock: int | None = None   # None = 该仓库无库存记录
    reserved: int = 0
    available: int | None = None
    status: str                        # ok / insufficient / no_record / unknown


class SimulateResult(BaseModel):
    rows: list[SimulateRow] = Field(default_factory=list)


# ── 贸易检查（与托盘 QR 对账）──────────────────────────────────────────────
class PalletCheckRequest(BaseModel):
    items: Annotated[list[SimulateLine], Field(min_length=1)]
    pallet_codes: Annotated[list[str], Field(min_length=1)]


class PalletCheckRow(BaseModel):
    jan_code: str
    name_zh: str | None = None
    counted: int          # 实际点数
    expected: int         # 托盘应有量（被扫托盘 PalletItem 之和）
    diff: int             # counted - expected
    match: bool


class PalletCheckResult(BaseModel):
    rows: list[PalletCheckRow] = Field(default_factory=list)
    unknown_pallet_codes: list[str] = Field(default_factory=list)  # 扫到但库里不存在的托盘码
