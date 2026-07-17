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
# 对方 mulselect 定位靠【容器 .ms_container】(其 ng-click=clickIn 开下拉)。实测 live 页触发框 id 与保存的 HTML 不同
# (#mstxt_saleClientSelectInput 在 live 页不存在)，故用稳定锚点找容器：
#   出库(客户)=下拉搜索框 placeholder 含"客户名称"(全页唯一)；入库(供应商)=第一个 MsModel.text 的容器(实测可用)。
# 容器内触发框统一 input[ng-model='MsModel.text']（读值判定是否选中）。
_CP_CONTAINER = {
    "in":  "div.ms_container:has(input[ng-model='MsModel.text'])",
    "out": "div.ms_container:has(input[ng-model='searchKey'][placeholder*='客户名称'])",
}
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
            # 离线提示弹窗：cookie 注入式自动化下，秦丝 SPA 常弹「您已处于离线状态」——这【不是会话失效】
            # (秦丝同步/httpx 抓取仍可用即证明 cookie 有效)，只是浏览器实时通道没建起。它是【阻断性弹窗】，
            # 点「确定」关掉即可继续；不影响后续填表/存草稿（读写走 HTTP，cookie 仍认）。
            for attempt in range(4):  # 可能连弹多个/反复弹，最多关 4 次
                offline = page.locator("text=离线状态").first
                if not (await offline.count() and await offline.is_visible()):
                    break
                await shot(page, "offline_prompt", note=f"离线弹窗 第{attempt+1}次")
                # 弹窗是动态生成、不在保存的HTML里 → 用JS按文本精准找到"确定"叶子元素直接点，并dump候选结构
                info = await page.evaluate(
                    "() => {"
                    " const vis=e=>!!(e.offsetWidth||e.offsetHeight||e.getClientRects().length);"
                    " const cand=Array.from(document.querySelectorAll('button,a,div,span,input'))"
                    "   .filter(e=>vis(e) && (e.children.length<=1) &&"
                    "     (/^确\\s*定$/.test((e.textContent||'').replace(/\\s/g,'')) ||"
                    "      /^确\\s*定$/.test((e.value||'').replace(/\\s/g,''))));"
                    " const dump=cand.slice(0,8).map(e=>({tag:e.tagName,cls:e.className,ng:e.getAttribute('ng-click'),oc:e.getAttribute('onclick'),html:e.outerHTML.slice(0,160)}));"
                    " if(cand[0]){ cand[0].click(); }"
                    " return {clicked:!!cand[0], count:cand.length, cand:dump}; }"
                )
                if attempt == 0:
                    (debug_dir / "diag_offline.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
                await page.wait_for_timeout(1200)
            await shot(page, "after_offline_check")

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

            # 2b. 对方（供应商/客户）选「WMS回填」。这是 mulselect 自定义指令，三个死穴（全面读页面后确认）：
            #   ① 开下拉靠【容器 .ms_container 的 ng-click="clickIn()"】——触发框 input 是 readonly，点它/dispatch 它都白搭！
            #   ② 下拉里 <input ng-model="searchKey" ng-keydown="searchPress"> 搜、<li ng-click="selected(option)"><div title="…"> 选
            #   ③ 页面有多个 mulselect（销售员筛选/供应商/客户…）都有 searchKey/selected，必须把搜和选【限定在对方这个容器内】
            container = page.locator(_CP_CONTAINER[direction]).first
            trg = container.locator("input[ng-model='MsModel.text']").first   # 容器内触发框(读值判定是否选中)
            cp_open = False
            if await container.count():
                await container.dispatch_event("click")   # 直接触发容器 clickIn() 开下拉（dispatch 绕过橙色提示条遮挡）
                await page.wait_for_timeout(700)
                si = container.locator("input[ng-model='searchKey']").first
                if not (await si.count() and await si.is_visible()):   # 没开 → 真实点击容器兜底
                    try:
                        await container.click(timeout=4000)
                    except Exception:
                        await container.click(force=True)
                    await page.wait_for_timeout(700)
                    si = container.locator("input[ng-model='searchKey']").first
                await shot(page, "cp_picker")
                if await si.count() and await si.is_visible():
                    cp_open = True
                    await si.click()
                    await si.fill("WMS回填")
                    await page.wait_for_timeout(1600)          # 等 clientSelectJSON.ac / supplierSelectJSON.ac 返回
                    await shot(page, "cp_search")
                    # 选中：dispatch 到结果 li 直接触发 selected(option)（之前点不中=被遮挡/层级拦截，dispatch 绕过它）
                    opt = container.locator("li[ng-click='selected(option)']:has([title='WMS回填'])").first
                    if await opt.count():
                        await opt.dispatch_event("click")
                        await page.wait_for_timeout(900)
                    v0 = await trg.get_attribute("value") if await trg.count() else None
                    if not (v0 and "回填" in v0):               # 兜底：键盘 ↓ 高亮 + Enter（走搜索框自带 searchPress）
                        await si.press("ArrowDown")
                        await page.wait_for_timeout(300)
                        await si.press("Enter")
                        await page.wait_for_timeout(900)
            # 诊断 dump（成败都留，彻底告别盲猜）：触发框值、容器有没有、各 searchKey、对方容器内的结果项
            try:
                diag = await page.evaluate(
                    "(csel) => { const q=s=>Array.from(document.querySelectorAll(s));"
                    " const c=document.querySelector(csel);"
                    " const trg=c&&c.querySelector(\"input[ng-model='MsModel.text']\");"
                    " const lis=c?Array.from(c.querySelectorAll(\"li[ng-click='selected(option)']\")):[];"
                    " return { trigger_val: trg?trg.value:null, container_found: !!c,"
                    "  searchKeys: q(\"input[ng-model='searchKey']\").map(e=>({ph:e.placeholder,val:e.value,vis:!!(e.offsetWidth||e.offsetHeight)})),"
                    "  cp_options: lis.map(e=>({txt:(e.textContent||'').trim().slice(0,20),vis:!!(e.offsetWidth||e.offsetHeight)})).slice(0,10),"
                    " }; }", _CP_CONTAINER[direction])
                (debug_dir / "diag_picker.json").write_text(json.dumps(diag, ensure_ascii=False, indent=2), encoding="utf-8")
            except Exception:
                pass
            # 确认选中：触发框值必须含「回填」。没选上 → 【中止】（避免开着的 picker 把后续 JAN 串进搜索框，就是你截图那样）
            cp_val = await trg.get_attribute("value") if await trg.count() else None
            await shot(page, "cp_final", note=f"对方=「{cp_val}」 picker={cp_open}")
            if not (cp_val and "回填" in cp_val):
                res.error = f"「WMS回填」未选中(当前=「{cp_val}」, picker={cp_open})——已中止避免污染。见 diag_picker.json"
                await shot(page, "CP_NOT_SELECTED", ok=False, note=res.error)
                return res

            # 3. 加货：采购(in) 与 销售(out) 的商品网格【完全不同】——
            #    采购=Angular 订单行内联输入 #{row}_goodName + 下拉 selAutoGood；
            #    销售=jqGrid「点击选择」，商品要走【选择商品 modal】(selectGoodsClick → #input-control 搜 → 勾选 → 确认)加进 list4。
            if direction == "in":
                for i, (jan, qty) in enumerate(items[:10]):
                    rowid = str(i + 1)
                    # 注意：id 以数字开头，CSS #1_goodName 非法，必须用属性选择器 [id="1_goodName"]
                    gn = page.locator(f"[id='{rowid}_goodName']")
                    if not await gn.count():
                        cell = page.locator(f"tr[id='{rowid}'] td[aria-describedby$='_goodName']").first
                        if await cell.count():
                            await cell.click()
                            await page.wait_for_timeout(700)
                            gn = page.locator(f"[id='{rowid}_goodName']")
                    if not await gn.count():
                        res.not_found.append(jan)
                        continue
                    await gn.click()
                    await gn.fill(jan)              # oninput=changAutoGoods → 弹出下拉
                    await page.wait_for_timeout(1600)
                    sel = page.locator("tr[ng-click='selAutoGood(good)']:visible").filter(has_text=jan).first
                    if not await sel.count():
                        sel = page.locator("tr[ng-click='selAutoGood(good)']:visible").first
                    if await sel.count():
                        await sel.dispatch_event("click")
                        await page.wait_for_timeout(900)
                    else:
                        res.not_found.append(jan)  # 查无 = 新品（自动建后续迭代）
                        continue
                    if i == 0:
                        await shot(page, "item1_after_select")
                    q = page.locator(f"[id='{rowid}_unitQuantity']")
                    if await q.count():
                        await q.fill(str(qty))
            else:
                # 销售：逐个 JAN → 点「选择商品」开 modal → #input-control 搜 → 勾选首行 → 确认 → 加进 list4
                added: list[tuple[str, int]] = []
                for i, (jan, qty) in enumerate(items[:10]):
                    btn = page.locator("[ng-click='selectGoodsClick()']:visible").first
                    if not await btn.count():
                        btn = page.locator("[ng-click='selectGoodsClick()']").first
                    if not await btn.count():
                        res.not_found.append(jan)
                        continue
                    try:
                        await btn.click()
                    except Exception:
                        await btn.dispatch_event("click")
                    await page.wait_for_timeout(1200)
                    search = page.locator("#input-control[ng-model='selectGoodsModalSearchKey']").first
                    if not (await search.count() and await search.is_visible()):
                        res.not_found.append(jan)
                        await page.keyboard.press("Escape")
                        await page.wait_for_timeout(400)
                        continue
                    await search.click()
                    await search.fill(jan)
                    await search.press("Enter")            # ng-keyup=searchGoodsKey → 过滤商品
                    await page.wait_for_timeout(1800)       # 等 searchGoods AJAX
                    if i == 0:
                        await shot(page, "modal_search")    # 诊断：看搜索结果
                    # 有的秦丝 modal 扫到唯一条码会自动加入并关闭 → 已关就算加好
                    if not await search.is_visible():
                        added.append((jan, qty))
                        continue
                    row = page.locator("#selectGoodsModalTable tr.jqgrow").first
                    if not await row.count():
                        res.not_found.append(jan)          # 查无 = 新品
                        close = page.locator("[ng-click='closeSelectGoodsModal($event)']").first
                        if await close.count():
                            await close.dispatch_event("click")
                        await page.wait_for_timeout(500)
                        continue
                    cb = row.locator("input[type='checkbox']").first
                    if await cb.count():
                        try:
                            await cb.check()
                        except Exception:
                            await cb.dispatch_event("click")
                    else:
                        await row.click()
                    await page.wait_for_timeout(500)
                    await page.locator("[ng-click='confirmSelectGoodsDebounce($event)']").first.dispatch_event("click")
                    await page.wait_for_timeout(1600)       # 商品加入 list4
                    added.append((jan, qty))
                await shot(page, "after_add_goods")
                # 填数量：list4 数据行的 数量列(list4_unitQuantity)，按加入顺序对齐
                rows = page.locator("#list4 tr.jqgrow")
                nrows = await rows.count()
                for idx in range(min(nrows, len(added))):
                    row = rows.nth(idx)
                    rid = await row.get_attribute("id")
                    qcell = row.locator("td[aria-describedby='list4_unitQuantity']").first
                    if not await qcell.count():
                        continue
                    try:
                        await qcell.click()
                        await page.wait_for_timeout(400)
                        inp = page.locator(f"[id='{rid}_unitQuantity']").first
                        if not await inp.count():
                            inp = qcell.locator("input").first   # 数量格可能是常驻 input
                        if await inp.count():
                            await inp.fill(str(added[idx][1]))
                            await inp.press("Tab")               # 提交编辑
                            await page.wait_for_timeout(200)
                    except Exception:
                        pass
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
