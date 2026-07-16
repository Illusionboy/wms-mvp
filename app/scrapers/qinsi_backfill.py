"""秦丝反向回填（Playwright 填表）——把点数结果(JAN+数量)存成秦丝采购(入库)/批发(出库)草稿。

复用现有秦丝 session cookies（qinsi_session.json，Playwright cookie 列表）；驱动真实 Vue 页面
填表→保存草稿（**只存草稿，不点采购/出售**）。每步截图，像乐天那样监督迭代调选择器。

新品(扫码查无)→ 先记入 not_found（自动建商品放后续迭代）。统一供应商/客户、仓库、日期(当天)。
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

_SESSION_FILE = Path("app/data/qinsi_session.json")
_DEBUG_DIR = Path("app/data/qinsi_backfill_debug")
_URLS = {
    "in": "https://web.syt.qinsilk.com/gis/template/nadmin/inner/orders/purchaseList.html?mid=2&version=6.84.0",
    "out": "https://web.syt.qinsilk.com/gis/template/nadmin/inner/sale/wholesaleOrdersList.html?mid=4&version=6.84.0",
}
_NEW_BTN = {"in": "新增采购单", "out": "新增销售单"}
# 新品自动建（后续迭代用）：商品管理 → 新增商品，只填 名称 + 货号=JAN + 条码=JAN
_ADD_GOODS_URL = "https://web.syt.qinsilk.com/gis/static/view#/setting/goods/goodsList?mid=108&type=addGoods"
_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")


@dataclass
class BackfillResult:
    success: bool = False
    steps: list[dict] = field(default_factory=list)
    shots: list[str] = field(default_factory=list)
    created_new: list[str] = field(default_factory=list)
    not_found: list[str] = field(default_factory=list)
    error: str | None = None


async def backfill_draft(
    items: list[tuple[str, int]],
    *,
    direction: str = "in",
    warehouse_name: str = "普通仓库",
    headless: bool = True,
) -> BackfillResult:
    """items=[(jan, qty)]；direction='in'(采购入库)/'out'(批发出库)。首版：登录→开草稿→逐个扫码→存草稿，全程截图。"""
    from playwright.async_api import TimeoutError as PWTimeout  # noqa: F401
    from playwright.async_api import async_playwright

    res = BackfillResult()
    debug_dir = _DEBUG_DIR / direction
    debug_dir.mkdir(parents=True, exist_ok=True)
    for old in debug_dir.glob("*.png"):
        old.unlink()

    try:
        cookies = json.loads(_SESSION_FILE.read_text())
        assert isinstance(cookies, list) and cookies
    except Exception:
        res.error = "秦丝 session 未就绪——先刷新秦丝会话（本机 refresh_qinsi 上传）"
        return res

    seq = 0

    async def shot(page, name: str, ok: bool = True, note: str = "") -> None:
        nonlocal seq
        seq += 1
        fn = f"{seq:02d}_{name}.png"
        try:
            await page.screenshot(path=str(debug_dir / fn))
            res.shots.append(fn)
        except Exception:
            pass
        try:
            res.steps.append({"step": name, "url": page.url, "ok": ok, "note": note})
        except Exception:
            res.steps.append({"step": name, "ok": ok, "note": note})

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=headless,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(
            locale="zh-CN", timezone_id="Asia/Tokyo", viewport={"width": 1440, "height": 900}, user_agent=_UA,
        )
        await context.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")
        try:
            await context.add_cookies(cookies)
        except Exception as exc:  # noqa: BLE001
            res.error = f"加载 cookies 失败：{exc}"
            await browser.close()
            return res
        page = await context.new_page()
        page.set_default_timeout(30000)

        try:
            # 1. 打开列表页（带 session 应已登录）
            await page.goto(_URLS[direction], wait_until="domcontentloaded")
            await page.wait_for_timeout(3500)
            await shot(page, "list_page")
            if "login" in page.url.lower() or await page.locator("input[type='password']").count():
                await shot(page, "NEED_LOGIN", ok=False, note="被要求登录——秦丝 session 失效，请刷新")
                res.error = "秦丝 session 失效（跳到登录页），请刷新会话"
                return res

            # 2. 新增草稿
            nb = page.locator(f"text={_NEW_BTN[direction]}").first
            if await nb.count():
                await nb.click()
            else:
                await shot(page, "NEW_BTN_NOT_FOUND", ok=False, note=f"没找到「{_NEW_BTN[direction]}」按钮")
                res.error = f"没找到「{_NEW_BTN[direction]}」按钮（见截图）"
                return res
            await page.wait_for_timeout(2500)
            await shot(page, "new_draft_form")

            # 3. 逐个扫码加货（扫码框 placeholder=请扫描商品条形码）
            scan = page.locator("input[placeholder*='扫描商品条形码'], input[placeholder*='请扫描商品条形码']").first
            if not await scan.count():
                await shot(page, "SCAN_INPUT_NOT_FOUND", ok=False, note="没找到扫码输入框（可能要先点『扫码录入』）")
                res.error = "没找到扫码输入框（见截图，待补开扫码的步骤）"
                return res
            for jan, qty in items[:5]:  # 首版最多试 5 个
                await scan.fill(jan)
                await scan.press("Enter")
                await page.wait_for_timeout(1500)
            await shot(page, "after_scan")

            # 4. 保存草稿（待定位确切按钮，先截图看有哪些按钮）
            await shot(page, "before_save")
            res.error = "首版跑到『已扫码』，保存草稿按钮/数量填写/供应商仓库 待按截图补下一步"
        except Exception as exc:  # noqa: BLE001
            try:
                await shot(page, "EXCEPTION", ok=False, note=str(exc)[:200])
            except Exception:
                pass
            res.error = f"{type(exc).__name__}: {exc}"
        finally:
            await context.close()
            await browser.close()

    return res
