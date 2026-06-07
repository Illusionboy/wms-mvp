"""
秦丝生意通 API 客户端（httpx 直接调用，无需浏览器抓表格）

认证流程：
  1. 读取 SESSION_FILE 里的 cookies（登录后保存，gisALogin 有效期7天）
  2. 调 getUserInfo.ac 验证；失败则提示用户通过 Playwright 手动登录
  3. 登录成功后保存新 cookies，后续7天内无需再次操作

数据获取（纯 httpx API 调用）：
  - 出库: GET wholesaleOrdersListJSON.ac + POST wholesaleOrdersGet.ac → orderGoods[].quantity
  - 入库: GET purchaseListJSON.ac + POST purchaseGet.ac → orderGoods[].quantity
"""

from __future__ import annotations

import json
import logging
from datetime import date, datetime
from pathlib import Path

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).parent.parent / "data"
SESSION_FILE = _DATA_DIR / "qinsi_session.json"
DEBUG_DIR = _DATA_DIR / "scraper_debug"

BASE = "https://web.syt.qinsilk.com/gis/admin"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://web.syt.qinsilk.com/gis/admin/main.ac",
    "X-Requested-With": "XMLHttpRequest",
}
_PAGE_SIZE = 50


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

class ScrapedRecord(BaseModel):
    scraped_at: str
    record_date: str          # "YYYY-MM-DD"
    direction: str            # "IN" or "OUT"
    order_no: str             # order SN for grouping (sales/purchase order number)
    jan_code: str             # 8 or 13-digit barcode
    raw_jan: str
    product_name: str
    quantity: int
    warehouse_name: str
    customer_name: str | None
    note: str | None
    source_row: dict[str, str]   # raw JSON fields for debugging


class ScrapeResult(BaseModel):
    success: bool
    records: list[ScrapedRecord]
    error: str | None = None
    debug_screenshots: list[str] = []
    from_date: str
    to_date: str
    total_rows_found: int = 0
    needs_relogin: bool = False  # True → caller should trigger Playwright login


# ---------------------------------------------------------------------------
# Session / cookie management
# ---------------------------------------------------------------------------

def _load_cookies() -> dict[str, str]:
    """Load cookies from SESSION_FILE as a flat name→value dict."""
    try:
        if SESSION_FILE.exists():
            data = json.loads(SESSION_FILE.read_text())
            if isinstance(data, list):
                # Playwright format: list of {name, value, domain, ...}
                return {c["name"]: c["value"] for c in data if "name" in c}
            if isinstance(data, dict):
                return data
    except Exception as exc:
        logger.warning("Failed to load session: %s", exc)
    return {}


def save_cookies_from_playwright(playwright_cookies: list[dict]) -> None:
    """Save Playwright cookie list to SESSION_FILE."""
    try:
        SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
        SESSION_FILE.write_text(json.dumps(playwright_cookies, ensure_ascii=False, indent=2))
        logger.info("Saved %d cookies to %s", len(playwright_cookies), SESSION_FILE)
    except Exception as exc:
        logger.warning("Failed to save session: %s", exc)


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def _clean_jan(raw: str) -> str:
    digits = "".join(ch for ch in str(raw) if ch.isdigit())
    return digits if len(digits) >= 8 else ""


def _epoch_to_date(ms: int | None) -> str:
    if not ms:
        return ""
    return datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%d")


async def _check_auth(client: httpx.AsyncClient) -> bool:
    """Return True if the current cookies are valid."""
    try:
        r = await client.get(f"{BASE}/pubuser/getUserInfo.ac", headers=_HEADERS, timeout=10)
        data = r.json()
        return data.get("statusCode") == 1
    except Exception:
        return False


async def _get_json(client: httpx.AsyncClient, path: str, params: dict) -> dict:
    r = await client.get(f"{BASE}{path}", params=params, headers=_HEADERS, timeout=20)
    r.raise_for_status()
    return r.json()


async def _post_json(client: httpx.AsyncClient, path: str, params: dict | None = None) -> dict:
    url = f"{BASE}{path}"
    r = await client.post(
        url,
        params=params or {},
        json={},
        headers={**_HEADERS, "Content-Type": "application/json"},
        timeout=20,
    )
    r.raise_for_status()
    return r.json()


def _build_record(
    goods: dict,
    direction: str,
    order_date_ms: int,
    warehouse_name: str,
    customer_name: str | None,
    order_no: str,
    scraped_at: str,
) -> ScrapedRecord | None:
    raw_jan = str(goods.get("goodsSn") or goods.get("barCode") or "")
    jan = _clean_jan(raw_jan)
    qty = goods.get("quantity", 0)
    if not jan or not qty:
        return None
    return ScrapedRecord(
        scraped_at=scraped_at,
        record_date=_epoch_to_date(order_date_ms),
        direction=direction,
        order_no=order_no,
        jan_code=jan,
        raw_jan=raw_jan,
        product_name=str(goods.get("goodName", "")),
        quantity=int(qty),
        warehouse_name=warehouse_name,
        customer_name=customer_name,
        note=None,
        source_row={k: str(v) for k, v in goods.items()},
    )


# ---------------------------------------------------------------------------
# Fetch sales orders (出库)
# ---------------------------------------------------------------------------

async def _fetch_sales(
    client: httpx.AsyncClient,
    t_begin: str,
    t_end: str,
    scraped_at: str,
) -> list[ScrapedRecord]:
    records: list[ScrapedRecord] = []
    page = 1
    while True:
        data = await _get_json(client, "/inner/sale/wholesaleOrdersListJSON.ac", {
            "itemType": 1, "state": 12,
            "createTimeBegin": t_begin, "createTimeEnd": t_end,
            "rows": _PAGE_SIZE, "page": page,
            "sidx": "", "sord": "asc",
            "_search": "false", "isShowPrintCounts": 1,
        })
        rows = data.get("rows", [])
        total_pages = data.get("total", 1)
        logger.info("Sales page %d/%d: %d orders", page, total_pages, len(rows))

        for order in rows:
            sn = order.get("ordersSn", "")
            depot_name = order.get("depotName", "秦丝仓库")
            client_name = order.get("clientName")
            date_ms = order.get("businessTime") or order.get("createTime")
            try:
                detail = await _post_json(
                    client, "/inner/sale/wholesaleOrdersGet.ac", {"ordersSn": sn}
                )
                for g in detail.get("orderGoods", []):
                    rec = _build_record(g, "OUT", date_ms, depot_name, client_name, sn, scraped_at)
                    if rec:
                        records.append(rec)
            except Exception as exc:
                logger.warning("Failed to fetch sale detail %s: %s", sn, exc)

        if page >= total_pages:
            break
        page += 1

    return records


# ---------------------------------------------------------------------------
# Fetch purchase orders (入库)
# ---------------------------------------------------------------------------

async def _fetch_purchases(
    client: httpx.AsyncClient,
    t_begin: str,
    t_end: str,
    scraped_at: str,
) -> list[ScrapedRecord]:
    records: list[ScrapedRecord] = []
    page = 1
    while True:
        data = await _get_json(client, "/inner/orders/purchase/purchaseListJSON.ac", {
            "itemType": 1, "state": 12,
            "createTimeBegin": t_begin, "createTimeEnd": t_end,
            "rows": _PAGE_SIZE, "page": page,
            "sidx": "", "sord": "asc", "_search": "false",
        })
        rows = data.get("rows", [])
        total_pages = data.get("total", 1)
        logger.info("Purchase page %d/%d: %d orders", page, total_pages, len(rows))

        for order in rows:
            sn = order.get("purchaseSn", "")
            depot_name = order.get("depotName", "秦丝仓库")
            date_ms = order.get("businessTime") or order.get("createTime")
            try:
                detail = await _post_json(
                    client, "/inner/orders/purchase/purchaseGet.ac", {"purchaseSn": sn}
                )
                for g in detail.get("orderGoods", []):
                    rec = _build_record(g, "IN", date_ms, depot_name, None, sn, scraped_at)
                    if rec:
                        records.append(rec)
            except Exception as exc:
                logger.warning("Failed to fetch purchase detail %s: %s", sn, exc)

        if page >= total_pages:
            break
        page += 1

    return records


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

async def scrape_stock_records(
    from_date: date,
    to_date: date,
) -> ScrapeResult:
    """
    Fetch stock movements from 秦丝生意通 API for the given date range.
    No browser required — uses saved session cookies.
    Returns ScrapeResult; if needs_relogin=True, caller must trigger Playwright login first.
    """
    from_str = from_date.strftime("%Y-%m-%d")
    to_str = to_date.strftime("%Y-%m-%d")
    t_begin = f"{from_str} 00:00:00"
    t_end = f"{to_str} 23:59:59"
    scraped_at = datetime.utcnow().isoformat()

    cookies = _load_cookies()
    if not cookies:
        return ScrapeResult(
            success=False, records=[], from_date=from_str, to_date=to_str,
            error="未找到登录 session。请在本地 Mac 上运行: python -m tools.refresh_qinsi_session，完成滑块验证后 session 会自动上传到服务器",
            needs_relogin=True,
        )

    async with httpx.AsyncClient(cookies=cookies, follow_redirects=True, timeout=30) as client:
        # Verify auth
        if not await _check_auth(client):
            return ScrapeResult(
                success=False, records=[], from_date=from_str, to_date=to_str,
                error="秦丝 session 已过期，请重新授权登录",
                needs_relogin=True,
            )

        try:
            sales = await _fetch_sales(client, t_begin, t_end, scraped_at)
            purchases = await _fetch_purchases(client, t_begin, t_end, scraped_at)
        except Exception as exc:
            logger.exception("Scrape failed: %s", exc)
            return ScrapeResult(
                success=False, records=[], from_date=from_str, to_date=to_str,
                error=f"抓取失败: {exc}",
            )

    all_records = sales + purchases
    return ScrapeResult(
        success=True,
        records=all_records,
        from_date=from_str,
        to_date=to_str,
        total_rows_found=len(all_records),
    )


# ---------------------------------------------------------------------------
# Playwright re-login (called when needs_relogin=True)
# ---------------------------------------------------------------------------

async def do_playwright_login() -> bool:
    """
    Open a visible browser for the user to manually complete CAPTCHA login.
    Saves cookies on success. Returns True if login succeeded.
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        logger.error("Playwright not installed")
        return False

    from app.core.config import settings
    base_url = str(settings.qinsi_base_url).rstrip("/")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=False,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(
            locale="zh-CN",
            timezone_id="Asia/Tokyo",
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        await context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
        )
        page = await context.new_page()

        await page.goto(base_url, wait_until="domcontentloaded", timeout=30_000)
        logger.info("Playwright browser opened — waiting for user to complete login...")

        # Poll until auth succeeds (max 5 minutes)
        for _ in range(150):
            await page.wait_for_timeout(2000)
            cookies_list = await context.cookies()
            flat = {c["name"]: c["value"] for c in cookies_list if "qinsilk.com" in c.get("domain", "")}
            if flat:
                async with httpx.AsyncClient(cookies=flat, follow_redirects=True, timeout=10) as client:
                    if await _check_auth(client):
                        save_cookies_from_playwright(cookies_list)
                        logger.info("Login successful, cookies saved")
                        await browser.close()
                        return True

        await browser.close()
        logger.error("Playwright login timed out (5 min)")
        return False
