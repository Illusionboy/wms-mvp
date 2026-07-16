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
        page.set_default_timeout(12000)             # 动作超时 12s（失败更快，便于调试）
        page.set_default_navigation_timeout(30000)  # 导航仍留 30s

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

            # 2b. 供应商：选「WMS回填」（点供应商选择器→搜索框输入→点结果）。仓库仍用默认(北津守)。
            #     供应商是第一个 mstxt_（供应商→仓库→结算账户顺序）。
            sup = page.locator("[id='mstxt_']").first
            if await sup.count():
                await sup.click()
                await page.wait_for_timeout(1200)
                await shot(page, "supplier_picker")
                si = page.locator("input[ng-model='searchKey']:visible").first
                if await si.count():
                    await si.fill("WMS回填")
                    await page.wait_for_timeout(1600)
                    await shot(page, "supplier_search")
                    opt = page.locator(
                        ":is(li,tr,a,div,span)[ng-click]:visible"
                    ).filter(has_text="WMS回填").first
                    if not await opt.count():
                        opt = page.get_by_text("WMS回填", exact=False).last
                    if await opt.count():
                        await opt.dispatch_event("click")
                        await page.wait_for_timeout(900)
            await shot(page, "after_supplier")

            # 3. 逐个加货：往订单行 #{rowid}_goodName 输全 JAN → 下拉点第一个 → 填 #{rowid}_unitQuantity
            for i, (jan, qty) in enumerate(items[:10]):
                rowid = str(i + 1)
                # 注意：id 以数字开头，CSS #1_goodName 非法，必须用属性选择器 [id="1_goodName"]
                gn = page.locator(f"[id='{rowid}_goodName']")
                if not await gn.count():
                    # 行未进入编辑态：点该行商品格触发行内编辑
                    cell = page.locator(f"tr[id='{rowid}'] td[aria-describedby$='_goodName']").first
                    if await cell.count():
                        await cell.click()
                        await page.wait_for_timeout(500)
                        gn = page.locator(f"[id='{rowid}_goodName']")
                if not await gn.count():
                    res.not_found.append(jan)
                    continue
                await gn.click()
                await gn.fill(jan)              # oninput=changAutoGoods → 弹出下拉
                await page.wait_for_timeout(1600)
                # 下拉是普通 Angular 表格：结果行 <tr ng-click="selAutoGood(good)">，取含本 JAN 的可见行
                sel = page.locator("tr[ng-click='selAutoGood(good)']:visible").filter(has_text=jan).first
                if not await sel.count():
                    sel = page.locator("tr[ng-click='selAutoGood(good)']:visible").first
                if await sel.count():
                    await sel.dispatch_event("click")   # 触发 Angular selAutoGood(good) 选中
                    await page.wait_for_timeout(900)
                else:
                    res.not_found.append(jan)  # 全 JAN 查无 = 新品（自动建后续迭代）
                    continue
                if i == 0:
                    await shot(page, "item1_after_select")  # 诊断：看第1个商品有没有选上
                q = page.locator(f"[id='{rowid}_unitQuantity']")
                if await q.count():
                    await q.fill(str(qty))
            await shot(page, "after_items")

            # 4. 保存草稿：按钮文案就是「草稿」(ng-click=saveOrder)，禁用条件含 supplierId/depotId/accountId/商品
            btn = page.locator("button.btn-normal:text-is('草稿'), button:text-is('草稿')").first
            if not await btn.count():
                await shot(page, "save_btn_NOT_FOUND", ok=False, note="没找到「草稿」按钮")
                res.error = "没找到「草稿」保存按钮（见截图）"
            elif await btn.is_disabled():
                await shot(page, "save_btn_DISABLED", ok=False,
                           note="「草稿」按钮禁用——供应商/仓库/结算账户/商品 有一项没齐")
                res.error = "「草稿」按钮禁用：供应商/仓库/结算账户/商品 有一项没齐（见截图）"
            else:
                await btn.click()
                await page.wait_for_timeout(3500)
                await shot(page, "after_save")
                res.success = not res.not_found
                res.error = (f"已存草稿，但 {len(res.not_found)} 个 JAN 查无(新品待建)：{', '.join(res.not_found[:5])}"
                             if res.not_found else None)
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
