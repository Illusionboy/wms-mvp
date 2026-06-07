from datetime import date, datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select
import httpx

from app.api.deps import require_auth
from app.core.config import settings
from app.db.session import get_db_session
from app.models.stock_transaction import StockTransaction
from app.models.warehouse import Warehouse
from app.scrapers.qinsi_scraper import (
    ScrapedRecord,
    ScrapeResult,
    _check_auth,
    _load_cookies,
    scrape_stock_records,
)
from app.services.auth import CurrentUser
from app.services.inventory import (
    InventoryRecordNotFoundError,
    InventoryTargetNotFoundError,
    stock_in_item,
    stock_out_item,
)
from app.schemas.inventory import StockInCreate, StockOutCreate

router = APIRouter()


class AuthStatus(BaseModel):
    authenticated: bool
    message: str


class UploadSessionRequest(BaseModel):
    cookies: list[dict]   # Playwright format: [{name, value, domain, ...}]


@router.post("/upload-session")
async def upload_qinsi_session(
    payload: UploadSessionRequest,
    current_user: CurrentUser = Depends(require_auth),
) -> dict:
    """
    接收从本地 Mac 上传的秦丝 session cookies，保存到服务器。
    由 tools/refresh_qinsi_session.py 调用，解决 NAS 无法打开浏览器的问题。
    """
    from app.scrapers.qinsi_scraper import SESSION_FILE, _check_auth
    import json

    if not payload.cookies:
        return {"ok": False, "message": "cookies 为空"}

    # 验证 cookies 有效
    flat = {c["name"]: c["value"] for c in payload.cookies if "name" in c}
    try:
        async with httpx.AsyncClient(cookies=flat, follow_redirects=True, timeout=10) as client:
            ok = await _check_auth(client)
    except Exception as exc:
        return {"ok": False, "message": f"验证失败: {exc}"}

    if not ok:
        return {"ok": False, "message": "Cookies 无效，请重新登录"}

    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    SESSION_FILE.write_text(json.dumps(payload.cookies, ensure_ascii=False, indent=2))
    return {"ok": True, "message": f"已保存 {len(payload.cookies)} 个 cookies，秦丝同步已授权"}


@router.get("/auth-status", response_model=AuthStatus)
async def qinsi_auth_status() -> AuthStatus:
    """Check whether saved 秦丝 session cookies are still valid (no auth required)."""
    cookies = _load_cookies()
    if not cookies:
        return AuthStatus(authenticated=False, message="未找到登录凭证，请运行本地授权脚本")
    try:
        async with httpx.AsyncClient(cookies=cookies, follow_redirects=True, timeout=10) as client:
            ok = await _check_auth(client)
        if ok:
            return AuthStatus(authenticated=True, message="已登录（秦丝生意通）")
        return AuthStatus(authenticated=False, message="Session 已过期，请重新运行授权脚本")
    except Exception as exc:
        return AuthStatus(authenticated=False, message=f"连接失败: {exc}")


class ScrapeRequest(BaseModel):
    from_date: date
    to_date: date


class ApplyRequest(BaseModel):
    records: list[ScrapedRecord]
    warehouse_id: int | None = None   # fallback when per-record mapping fails
    customer_id: int | None = None


class ApplyResult(BaseModel):
    applied: int
    skipped: int
    duplicate: int = 0
    errors: list[str]


@router.post("/scrape", response_model=ScrapeResult)
async def trigger_scrape(
    payload: ScrapeRequest,
    current_user: CurrentUser = Depends(require_auth),
) -> ScrapeResult:
    """
    触发秦丝生意通爬虫，返回指定日期范围内的出入库记录供用户审核。
    结果不写数据库，由前端展示后用户勾选再调用 /apply。
    """
    result = await scrape_stock_records(
        from_date=payload.from_date,
        to_date=payload.to_date,
    )
    return result


@router.post("/apply", response_model=ApplyResult)
async def apply_scraped_records(
    payload: ApplyRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_auth),
) -> ApplyResult:
    """
    将用户勾选的爬取记录写入 WMS。
    每条记录写一个 StockTransaction（source="qinsi_scrape"）。
    reference_id = "qinsi:{order_no}:{jan_code}" 保证幂等——重复提交同一订单行自动跳过。
    """
    applied = 0
    skipped = 0
    duplicate = 0
    errors: list[str] = []

    # Build warehouse name → id lookup (WMS names)
    wh_rows = await session.scalars(select(Warehouse))
    wh_by_name: dict[str, int] = {w.name: w.id for w in wh_rows.all()}

    # qinsi_name → wms_name mapping from config
    qinsi_wh_map: dict[str, str] = settings.qinsi_warehouse_map

    # 批量预查已导入的 reference_id，避免 N+1
    ref_ids = [
        f"qinsi:{rec.order_no}:{rec.jan_code}"
        for rec in payload.records
        if rec.jan_code and rec.order_no
    ]
    existing_refs: set[str] = set()
    if ref_ids:
        rows = await session.scalars(
            select(StockTransaction.reference_id).where(
                StockTransaction.source == "qinsi_scrape",
                StockTransaction.reference_id.in_(ref_ids),
            )
        )
        existing_refs = set(rows.all())

    for rec in payload.records:
        if not rec.jan_code:
            errors.append(f"{rec.product_name}: 无有效 JAN 条码（原始值: {rec.raw_jan}）")
            skipped += 1
            continue

        ref_id = f"qinsi:{rec.order_no}:{rec.jan_code}" if rec.order_no else None
        if ref_id and ref_id in existing_refs:
            duplicate += 1
            continue

        # Resolve warehouse: map Qinsi name → WMS name → WMS id
        qinsi_name = rec.warehouse_name or ""
        wms_name = qinsi_wh_map.get(qinsi_name, "")
        resolved_wh_id = wh_by_name.get(wms_name) or payload.warehouse_id
        if not resolved_wh_id:
            errors.append(
                f"{rec.jan_code} ({rec.product_name}): "
                f"无法确定仓库（秦丝仓库名 {qinsi_name!r} 未在映射表中，且未指定默认仓库）"
            )
            skipped += 1
            continue

        txn_date: date | None = None
        try:
            txn_date = date.fromisoformat(rec.record_date) if rec.record_date else None
        except ValueError:
            pass
        note = f" 备注:{rec.note}" if rec.note else ""
        try:
            if rec.direction == "IN":
                await stock_in_item(
                    session=session,
                    payload=StockInCreate(
                        sku=rec.jan_code,
                        warehouse_id=resolved_wh_id,
                        customer_id=payload.customer_id,
                        quantity=rec.quantity,
                        location_code="A-00-00",
                        source="qinsi_scrape",
                        reference_id=ref_id,
                        note=note or None,
                        transaction_date=txn_date,
                    ),
                    commit=False,
                    user_id=current_user.id,
                )
            else:
                await stock_out_item(
                    session=session,
                    payload=StockOutCreate(
                        sku=rec.jan_code,
                        warehouse_id=resolved_wh_id,
                        customer_id=payload.customer_id,
                        quantity=rec.quantity,
                        source="qinsi_scrape",
                        reference_id=ref_id,
                        note=note or None,
                        transaction_date=txn_date,
                    ),
                    commit=False,
                    user_id=current_user.id,
                )
            applied += 1
        except InventoryTargetNotFoundError:
            errors.append(f"{rec.jan_code} ({rec.product_name}): 商品字典中不存在该 JAN")
            skipped += 1
        except InventoryRecordNotFoundError:
            errors.append(f"{rec.jan_code} ({rec.product_name}): 出库失败——该仓库无此商品库存记录")
            skipped += 1
        except Exception as exc:
            errors.append(f"{rec.jan_code} ({rec.product_name}): {exc or type(exc).__name__}")
            skipped += 1

    if applied > 0:
        await session.commit()

    return ApplyResult(applied=applied, skipped=skipped, duplicate=duplicate, errors=errors)
