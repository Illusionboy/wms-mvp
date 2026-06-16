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
    allow_negative_stock: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WarehouseStatusRead(BaseModel):
    warehouse_id: int
    warehouse_name: str
    allow_negative_stock: bool
    last_stock_in_at: datetime | None
    last_stock_out_at: datetime | None
    last_csv_apply_at: datetime | None
    last_physical_count_at: datetime | None
    data_gap_days: int | None
    negative_stock_count: int


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


class ProductCatalogImportResult(BaseModel):
    created: int
    updated: int
    skipped: int
    total: int


class ProductRead(BaseModel):
    jan_code: str
    name_jp: str
    name_zh: str | None
    units_per_case: int | None
    outer_jan: str | None = None
    low_stock_alert_sent: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    jan_code: JanQuery
    name_jp: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
    name_zh: Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)] | None = None
    units_per_case: int | None = Field(default=None, gt=0)


class ProductUpdate(BaseModel):
    name_jp: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)] | None = None
    name_zh: Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)] | None = None
    units_per_case: int | None = Field(default=None, gt=0)
    outer_jan: Annotated[str, StringConstraints(strip_whitespace=True, max_length=13)] | None = Field(default=None)


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
    outer_jan_warning: str | None = None  # set when search matched via outer_jan


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
    transaction_date: date | None = None
    supplier: str | None = Field(default=None, max_length=255)


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
    transaction_date: date | None = None
    customer: str | None = Field(default=None, max_length=255)


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
    transaction_date: date | None = None


class StockTransferCreate(BaseModel):
    sku: JanQuery
    from_warehouse_id: int = Field(gt=0)
    to_warehouse_id: int = Field(gt=0)
    quantity: int = Field(gt=0)
    note: str | None = Field(default=None, max_length=1000)
    transaction_date: date | None = None


class StockTransactionRead(BaseModel):
    id: int
    inventory_record_id: int
    transaction_type: StockTransactionType
    quantity_change: int
    source: str
    reference_id: str | None
    note: str | None
    transaction_date: date | None
    supplier: str | None
    customer: str | None
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


class NonJanLine(BaseModel):
    order_number: str | None = None
    product_number: str       # raw 商品番号 value
    quantity: int


class RakutenShipmentIssue(BaseModel):
    line_index: int
    jan_code: str
    issue_type: str
    message: str
    candidates: list[ProductRead] = Field(default_factory=list)
    current_stock: int | None = None   # for insufficient_stock: existing qty
    quantity_needed: int | None = None  # for needs_decision display


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
    names_synced: int = 0
    skipped_duplicates: int = 0   # lines skipped because reference_id already exists
    auto_skipped_count: int = 0   # product_not_found lines silently dropped
    force_negated_count: int = 0  # lines applied as negative stock by user choice


class RakutenDraftPreview(BaseModel):
    draft_id: int
    total_lines: int
    ok_count: int                                   # lines that will apply normally
    auto_skipped_count: int                         # product_not_found → always silent skip
    needs_decision: list[RakutenShipmentIssue]      # no record / insufficient → user decides
    blocking_issues: list[RakutenShipmentIssue]     # ambiguous etc → must fix
    non_jan_lines: list[NonJanLine] = Field(default_factory=list)  # unparseable 商品番号 → manual handling


class RakutenApplyRequest(BaseModel):
    force_negative_jans: list[str] = Field(default_factory=list)


class RakutenShipmentDraftDocument(BaseModel):
    warehouse_name: str
    customer_name: str
    lines: list[RakutenShipmentLine] = Field(default_factory=list)
    non_jan_lines: list[NonJanLine] = Field(default_factory=list)


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


class TradeShipmentLine(BaseModel):
    customer_name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
    jan_code: str
    product_name: str | None = None
    box_count: int = Field(gt=0)
    units_per_box: int = Field(gt=0)
    quantity: int = Field(gt=0)


class TradeShipmentIssue(BaseModel):
    line_index: int
    jan_code: str
    issue_type: str
    message: str
    candidates: list[ProductRead] = Field(default_factory=list)
    current_stock: int | None = None
    quantity_needed: int | None = None


class TradeShipmentMutation(BaseModel):
    jan_code: str
    customer_name: str
    quantity: int
    transaction: StockTransactionRead
    low_stock_alert: LowStockAlertRead | None = None


class TradeShipmentImportResult(BaseModel):
    applied: bool
    total_lines: int
    mutations: list[TradeShipmentMutation] = Field(default_factory=list)
    issues: list[TradeShipmentIssue] = Field(default_factory=list)
    skipped_duplicates: int = 0
    force_negated_count: int = 0


class TradeShipmentDraftDocument(BaseModel):
    warehouse_name: str
    lines: list[TradeShipmentLine] = Field(default_factory=list)


class TradeShipmentDraftPreview(BaseModel):
    draft_id: int
    total_lines: int
    ok_count: int
    needs_decision: list[TradeShipmentIssue] = Field(default_factory=list)
    blocking_issues: list[TradeShipmentIssue] = Field(default_factory=list)
    document: TradeShipmentDraftDocument


class TradeShipmentDraftRead(BaseModel):
    id: int
    status: str
    original_filename: str
    warehouse_name: str
    document: TradeShipmentDraftDocument
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TradeShipmentApplyRequest(BaseModel):
    force_negative_jans: list[str] = Field(default_factory=list)


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


class UnresolvedOrderLine(BaseModel):
    product_number: str
    sku_number: str | None = None
    quantity: int


class RakutenOrderLine(BaseModel):
    jan_code: str
    product_name: str | None
    ordered_qty: int
    current_stock: int | None  # None = product in DB but no 乐天仓库 record
    shortage: int               # max(0, ordered - max(0, stock))
    status: str                 # "ok" | "insufficient" | "no_record" | "unknown"


class RakutenOrderAnalysisResult(BaseModel):
    draft_id: int | None = None
    store1_lines: int           # raw item-lines parsed from file 1
    store2_lines: int           # 0 if only one file uploaded
    unresolved_count: int       # lines whose JAN could not be resolved
    unknown_jan_count: int      # JAN not found in WMS product catalog
    items: list[RakutenOrderLine] = Field(default_factory=list)
    unresolved: list[UnresolvedOrderLine] = Field(default_factory=list)


class RakutenOrderDraftDocument(BaseModel):
    items: list[RakutenOrderLine] = Field(default_factory=list)
    unresolved: list[UnresolvedOrderLine] = Field(default_factory=list)


class RakutenOrderMutation(BaseModel):
    jan_code: str
    quantity: int
    transaction: StockTransactionRead
    low_stock_alert: LowStockAlertRead | None = None


class RakutenOrderApplyResult(BaseModel):
    applied: bool
    mutations: list[RakutenOrderMutation] = Field(default_factory=list)
    shortage_items: list[RakutenOrderLine] = Field(default_factory=list)
    unresolved: list[UnresolvedOrderLine] = Field(default_factory=list)
    skipped_duplicates: int = 0


class CustomerAllocationRead(BaseModel):
    id: int
    planned_outbound_date: date
    customer_name: str
    jan_code: str
    quantity: int
    status: str
    source_filename: str | None
    note: str | None
    product_name: str | None = None   # joined from products table
    current_stock: int | None = None  # joined at query time
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerAllocationUploadResult(BaseModel):
    planned_outbound_date: date
    source_filename: str
    total_rows: int
    reserved: int    # immediately satisfied
    waiting: int     # insufficient stock at upload time
    updated: int     # quantity changed on existing record
    skipped: int     # quantity unchanged duplicate


class CustomerAllocationStatusResult(BaseModel):
    customer_name: str
    planned_outbound_date: date
    ready_count: int
    waiting_count: int
    shipped_count: int
    items: list[CustomerAllocationRead] = Field(default_factory=list)


class SafetyStockRecommendation(BaseModel):
    jan_code: str
    name_jp: str
    name_zh: str | None
    warehouse_id: int
    warehouse_name: str
    supplier: str | None
    lead_time_days: int
    daily_avg: float
    std_dev: float
    safety_stock: float
    reorder_point: float
    current_quantity: int
    sufficient_data: bool
