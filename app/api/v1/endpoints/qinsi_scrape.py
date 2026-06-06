from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_auth
from app.db.session import get_db_session
from app.scrapers.qinsi_scraper import (
    ScrapedRecord,
    ScrapeResult,
    _check_auth,
    _load_cookies,
    scrape_stock_records,
)
from app.services.auth import CurrentUser
from app.services.inventory import (
    InventoryTargetNotFoundError,
    stock_in_item,
    stock_out_item,
)
from app.schemas.inventory import StockInCreate, StockOutCreate
import httpx

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
    warehouse_id: int
    customer_id: int | None = None


class ApplyResult(BaseModel):
    applied: int
    skipped: int
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
    JAN 匹配失败的行记录到 errors 中跳过，不中断整体导入。
    """
    applied = 0
    skipped = 0
    errors: list[str] = []

    for rec in payload.records:
        if not rec.jan_code:
            errors.append(f"{rec.product_name}: 无有效 JAN 条码（原始值: {rec.raw_jan}）")
            skipped += 1
            continue

        try:
            if rec.direction == "IN":
                await stock_in_item(
                    session=session,
                    payload=StockInCreate(
                        sku=rec.jan_code,
                        warehouse_id=payload.warehouse_id,
                        customer_id=payload.customer_id,
                        quantity=rec.quantity,
                        location_code="A-00-00",
                        source="qinsi_scrape",
                        note=f"秦丝记录日期:{rec.record_date}" + (f" 备注:{rec.note}" if rec.note else ""),
                    ),
                    commit=False,
                    user_id=current_user.id,
                )
            else:
                await stock_out_item(
                    session=session,
                    payload=StockOutCreate(
                        sku=rec.jan_code,
                        warehouse_id=payload.warehouse_id,
                        customer_id=payload.customer_id,
                        quantity=rec.quantity,
                        source="qinsi_scrape",
                        note=f"秦丝记录日期:{rec.record_date}" + (f" 备注:{rec.note}" if rec.note else ""),
                    ),
                    commit=False,
                    user_id=current_user.id,
                )
            applied += 1
        except InventoryTargetNotFoundError:
            errors.append(f"{rec.jan_code} ({rec.product_name}): 商品或仓库不存在")
            skipped += 1
        except Exception as exc:
            errors.append(f"{rec.jan_code} ({rec.product_name}): {exc}")
            skipped += 1

    if applied > 0:
        await session.commit()

    return ApplyResult(applied=applied, skipped=skipped, errors=errors)
