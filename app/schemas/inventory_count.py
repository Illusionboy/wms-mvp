from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class QinsiColumnMap(BaseModel):
    """Column indices for a 秦丝生意通 盘点单 HTML table."""
    jan_col: int
    name_col: int
    count_col: int
    source: str = "detected"  # "detected" | "cached" | "llm_repaired" | "hardcoded"


class QinsiSession(BaseModel):
    """One count session found in a 秦丝 HTML file."""
    session_index: int
    table_id: str          # e.g. "list5", "list5_1"
    item_count: int        # number of data rows detected
    date_hint: str | None  # any date string found near the table header
    title_hint: str | None # any title / warehouse hint near the table


class QinsiSessionListResult(BaseModel):
    """Returned by POST /inventory-count/list-sessions."""
    session_count: int
    sessions: list[QinsiSession]
    filename: str


class CountDraftLine(BaseModel):
    jan_code: str
    product_name: str
    count_quantity: int
    delta_after_count: int      # net change in WMS after count_date
    target_quantity: int        # count_quantity + delta_after_count
    current_quantity: int       # current WMS total for this SKU/warehouse/customer
    adjust_delta: int           # target_quantity - current_quantity
    has_wms_record: bool        # whether an InventoryRecord exists in this warehouse
    known_product: bool = True  # whether the JAN exists in the products catalog
    implicit_zero: bool = False # True = not in count sheet, treated as count_qty=0


class InventoryCountDocument(BaseModel):
    count_date: date
    warehouse_name: str
    customer_name: str | None = None
    lines: list[CountDraftLine] = Field(default_factory=list)
    unmatched_jan_codes: list[str] = Field(default_factory=list)


class InventoryCountDraftRead(BaseModel):
    id: int
    status: str
    original_filename: str
    count_date: date
    warehouse_name: str
    customer_name: str | None
    document: InventoryCountDocument
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InventoryCountApplyResult(BaseModel):
    applied: bool
    adjusted_count: int
    no_change_count: int
    created_count: int
    issues: list[str] = Field(default_factory=list)
