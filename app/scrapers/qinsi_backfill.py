"""秦丝反向回填（Playwright 填表）——把点数结果(JAN+数量)存成秦丝采购(入库)/批发(出库)草稿。

复用现有秦丝 session cookies（qinsi_session.json，Playwright cookie 列表）；驱动真实 Vue 页面
填表→保存草稿（**只存草稿，不点采购/出售**）。每步截图，像乐天那样监督迭代调选择器。

新品(扫码查无)→ 先记入 not_found（自动建商品放后续迭代）。统一供应商/客户、仓库、日期(当天)。
"""
from __future__ import annotations

import asyncio
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
_NEW_BTN = {"in": "新增采购单", "out": "新增"}  # 销售页打开即是新单表单，点「新增」保险起见
# 订单表单的对方选择器（按方向）：采购供应商=第一个 MsModel；销售客户有专属 id。
_CP_SEL = {"in": "input[ng-model='MsModel.text']", "out": "#mstxt_saleClientSelectInput"}
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
        # 出库库存不足会弹原生 confirm（"库存将为负…是否确认"）→ 自动接受（与按钮文案无关，各浏览器通用）
        page.on("dialog", lambda dialog: asyncio.ensure_future(dialog.accept()))

        try:
            # 1. 打开列表页（带 session 应已登录）
            await page.goto(_URLS[direction], wait_until="domcontentloaded")
            await page.wait_for_timeout(3500)
            await shot(page, "list_page")
            if "login" in page.url.lower() or await page.locator("input[type='password']").count():
                await shot(page, "NEED_LOGIN", ok=False, note="被要求登录——秦丝 session 失效，请刷新")
                res.error = "秦丝 session 失效（跳到登录页），请刷新会话"
                return res

            # 2. 打开新单：采购点「新增采购单」；销售页加载即是新单表单。点得到就点(找不到不报错，用已开表单)。
            nb = page.locator(f"text={_NEW_BTN[direction]}").first
            if await nb.count():
                try:
                    await nb.click()
                    await page.wait_for_timeout(2500)
                except Exception:
                    pass
            await shot(page, "new_draft_form")
            # 表单就绪判定：有商品行输入框 或「选择商品」按钮；否则报错
            form_ready = await page.locator("[id='1_goodName']").count() or await page.locator("text=选择商品").count()
            if not form_ready:
                await shot(page, "FORM_NOT_READY", ok=False, note="新单表单未就绪(无商品行/选择商品)")
                res.error = "新单表单未打开（见截图）"
                return res

            # 2b. 供应商：选「WMS回填」（点供应商选择器→搜索框输入→点结果）。仓库仍用默认(北津守)。
            #     供应商是第一个 mstxt_（供应商→仓库→结算账户顺序）。
            # 订单表单的对方选择器（采购供应商=第一个 MsModel；销售客户=专属 id）。
            # dispatch_event 打开，绕过橙色提示条遮挡。
            sup = page.locator(_CP_SEL[direction]).first
            if await sup.count():
                await sup.dispatch_event("click")
                await page.wait_for_timeout(1200)
                await shot(page, "supplier_picker")
                si = page.locator("input[ng-model='searchKey']:visible").first
                if await si.count():
                    await si.fill("WMS回填")
                    await page.wait_for_timeout(1600)
                    await shot(page, "supplier_search")
                    # 结果是带人像图标的可点项，文本正好"WMS回填"。真实点击(下拉项不被遮挡)，兜底 dispatch。
                    opt = page.get_by_text("WMS回填", exact=True).first
                    if await opt.count():
                        try:
                            await opt.click(timeout=5000)
                        except Exception:
                            await opt.dispatch_event("click")
                        await page.wait_for_timeout(1200)
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
                        await cell.dispatch_event("click")   # 派发 click 进入行内编辑（绕过货号遮挡）
                        await page.wait_for_timeout(600)
                        gn = page.locator(f"[id='{rowid}_goodName']")
                if not await gn.count():
                    res.not_found.append(jan)
                    continue
                await gn.click()
                await gn.fill(jan)              # oninput=changAutoGoods → 弹出下拉
                await page.wait_for_timeout(1600)
                # 下拉两种实现：采购=Angular tr[ng-click=selAutoGood]；销售=jqGrid td[list4_goodName]「点击选择」
                sel = page.locator("tr[ng-click='selAutoGood(good)']:visible").filter(has_text=jan).first
                if not await sel.count():
                    sel = page.locator("tr[ng-click='selAutoGood(good)']:visible").first
                if not await sel.count():
                    sel = page.locator("td[aria-describedby='list4_goodName']:visible").filter(has_text="点击选择").first
                if await sel.count():
                    await sel.dispatch_event("click")   # 触发选中
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
            # 采购按钮=「草稿」，销售=「草稿 (Ctrl+D)」→ 用包含匹配 + :visible（排除隐藏的"复制草稿")
            btn = page.locator("button:visible:has-text('草稿')").first
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
