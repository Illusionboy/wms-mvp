from datetime import date, datetime
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.models.stock_transaction import StockTransactionType


JanQuery = Annotated[str, StringConstraints(strip_whitespace=True, min_length=5, max_length=32)]
LocationCode = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        pattern=r"^[A-Z]-\d{2}-\d{2}$",
    ),
]


class InventorySearchQuery(BaseModel):
    keyword: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)] = Field(
        description="JAN code, JAN suffix, or product name."
    )


class WarehouseRead(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WarehouseCreate(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]


class CustomerRead(BaseModel):
    id: int
    name: str
    contact_info: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerCreate(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
    contact_info: str | None = Field(default=None, max_length=2000)


class ProductRead(BaseModel):
    jan_code: str
    name_jp: str
    name_zh: str | None
    units_per_case: int | None
    low_stock_alert_sent: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    jan_code: JanQuery
    name_jp: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
    name_zh: Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)] | None = None
    units_per_case: int | None = Field(default=None, gt=0)


class InventoryRecordRead(BaseModel):
    id: int
    product_jan: str
    warehouse_id: int
    customer_id: int | None
    location_code: str
    quantity: int
    expiration_date: date | None
    warehouse: WarehouseRead
    customer: CustomerRead | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductInventoryRead(ProductRead):
    inventory_records: list[InventoryRecordRead] = Field(default_factory=list)


class StockInCreate(BaseModel):
    sku: JanQuery
    warehouse_id: int = Field(gt=0)
    customer_id: int | None = Field(default=None, gt=0)
    quantity: int = Field(gt=0)
    location_code: LocationCode
    expiration_date: date | None = None
    source: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=64)] = "telegram"
    reference_id: str | None = Field(default=None, max_length=64)
    note: str | None = Field(default=None, max_length=1000)


class StockOutCreate(BaseModel):
    sku: JanQuery
    warehouse_id: int = Field(gt=0)
    quantity: int = Field(gt=0)
    source: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=64)]
    customer_id: int | None = Field(default=None, gt=0)
    location_code: LocationCode | None = None
    expiration_date: date | None = None
    reference_id: str | None = Field(default=None, max_length=64)
    note: str | None = Field(default=None, max_length=1000)
    suppress_low_stock_alert: bool = False


class StockAdjustCreate(BaseModel):
    sku: JanQuery
    warehouse_id: int = Field(gt=0)
    actual_quantity: int = Field(ge=0)
    source: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=64)] = "manual_count"
    customer_id: int | None = Field(default=None, gt=0)
    location_code: LocationCode | None = None
    expiration_date: date | None = None
    reference_id: str | None = Field(default=None, max_length=64)
    note: str | None = Field(default=None, max_length=1000)


class StockTransactionRead(BaseModel):
    id: int
    inventory_record_id: int
    transaction_type: StockTransactionType
    quantity_change: int
    source: str
    reference_id: str | None
    note: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LowStockAlertRead(BaseModel):
    jan_code: str
    product_name: str
    total_quantity: int
    units_per_case: int
    threshold_quantity: int

    model_config = ConfigDict(from_attributes=True)


class StockInResult(BaseModel):
    record: InventoryRecordRead
    transaction: StockTransactionRead
    quantity_added: int
    message: str


class StockOutResult(BaseModel):
    record: InventoryRecordRead
    transaction: StockTransactionRead
    quantity_removed: int
    message: str


class StockAdjustResult(BaseModel):
    record: InventoryRecordRead
    transaction: StockTransactionRead
    previous_quantity: int
    actual_quantity: int
    quantity_delta: int
    message: str


class ChatReportDirection(StrEnum):
    stock_in = "IN"
    stock_out = "OUT"


class ChatReportLine(BaseModel):
    direction: ChatReportDirection | None = None
    jan_hint: Annotated[str, StringConstraints(strip_whitespace=True, min_length=5, max_length=32)]
    quantity: int = Field(gt=0)
    product_name_hint: str | None = Field(default=None, max_length=255)
    original_text: str | None = Field(default=None, max_length=1000)
    note: str | None = Field(default=None, max_length=1000)


class ChatReportDocument(BaseModel):
    direction: ChatReportDirection
    report_date: date | None = None
    warehouse_name: str = Field(default="普通仓库", max_length=100)
    customer_name: str = Field(default="店铺", max_length=255)
    source: str = Field(default="chat_ai", max_length=64)
    lines: list[ChatReportLine] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ChatReportParseRequest(BaseModel):
    text: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20000)]
    default_warehouse_name: str = Field(default="普通仓库", max_length=100)
    default_customer_name: str = Field(default="店铺", max_length=255)
    source: str = Field(default="wechat_chat", max_length=64)


class ChatReportApplyIssue(BaseModel):
    line_index: int
    jan_hint: str
    issue_type: str
    message: str
    candidates: list[ProductRead] = Field(default_factory=list)


class ChatReportApplyMutation(BaseModel):
    line_index: int
    direction: ChatReportDirection
    jan_code: str
    quantity: int
    transaction: StockTransactionRead
    low_stock_alert: LowStockAlertRead | None = None


class ChatReportApplyResult(BaseModel):
    applied: bool
    mutations: list[ChatReportApplyMutation] = Field(default_factory=list)
    issues: list[ChatReportApplyIssue] = Field(default_factory=list)


class ChatReportDraftRead(BaseModel):
    id: int
    status: str
    document: ChatReportDocument
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RakutenShipmentLine(BaseModel):
    jan_code: str
    quantity: int = Field(gt=0)
    order_number: str | None = None
    product_name: str | None = None
    raw_product_number: str


class RakutenShipmentIssue(BaseModel):
    line_index: int
    jan_code: str
    issue_type: str
    message: str
    candidates: list[ProductRead] = Field(default_factory=list)


class RakutenShipmentMutation(BaseModel):
    jan_code: str
    quantity: int
    transaction: StockTransactionRead
    low_stock_alert: LowStockAlertRead | None = None


class RakutenShipmentImportResult(BaseModel):
    applied: bool
    total_lines: int
    mutations: list[RakutenShipmentMutation] = Field(default_factory=list)
    issues: list[RakutenShipmentIssue] = Field(default_factory=list)


class RakutenShipmentDraftDocument(BaseModel):
    warehouse_name: str
    customer_name: str
    lines: list[RakutenShipmentLine] = Field(default_factory=list)


class RakutenShipmentDraftRead(BaseModel):
    id: int
    status: str
    original_filename: str
    warehouse_name: str
    customer_name: str
    document: RakutenShipmentDraftDocument
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InventoryImportStatus(StrEnum):
    pending = "pending"
    parsed = "parsed"
    failed = "failed"


class InventoryImportCreate(BaseModel):
    original_filename: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
    content_type: str | None = Field(default=None, max_length=128)
    file_size: int = Field(ge=0)


class InventoryImportRead(BaseModel):
    id: int
    original_filename: str
    content_type: str | None
    file_size: int
    status: InventoryImportStatus
    message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
