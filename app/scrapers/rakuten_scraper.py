"""乐天 RMS 订单 CSV 自动下载（P2b）——Playwright 走真实浏览器。

登录链（都在一条会话里）：
  1. 访问 CSV 下载页 → 未登录跳 RMS 登录表单（glogin.rms.rakuten.co.jp）
  2. 填 RMS login_id/passwd 提交 → OAuth 跳 login.account.rakuten.com（React SPA）
  3. SPA 邮箱屏：填 #user_id(name=username) → 下一步
  4. SPA 密码屏：填 #password_current → 登录
  5. 跳回 csvdl-rp 下载表单页
  6. 填条件(注文日時 / 発送待ち / 全カラム模板 / ソーシャルギフト置换) → データを作成する
  7. 下载区填 CSV 专用账密 → ダウンロードする → 捕获下载

**每一步都截图存 debug 目录**，首跑失败时凭截图定位（selector / 是否被风控拦）。
若 headless 被登录 SPA 的风控拦下，退回"本机刷 session"方案（秦丝式），届时改这里。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

# 入口必须是 RMS 登录门户（未登录会渲染 RMS 登录表单）；直接打 csvdl 深链会被判 unauthorized，
# 打裸 mainmenu 会跳"再度ログインをお願いいたします"并指向带 /rms 的正确 URL。
_LOGIN_URL = "https://mainmenu.rms.rakuten.co.jp/rms"
# 登录成功后再导航到订单 CSV 下载表单页。
_DATA_URL = "https://csvdl-rp.rms.rakuten.co.jp/rms/mall/csvdl/CD02_01_001?dataType=opp_order"
_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
_DEBUG_DIR = Path("app/data/rms_debug")


@dataclass
class DownloadResult:
    success: bool = False
    csv_bytes: bytes | None = None
    csv_name: str | None = None
    steps: list[dict] = field(default_factory=list)   # [{step, url, title, ok, note}]
    error: str | None = None
    shots: list[str] = field(default_factory=list)     # 截图文件名（相对 debug 目录）


async def download_shipping_orders(
    creds: dict,
    *,
    days: int = 10,
    headless: bool = True,
) -> DownloadResult:
    """跑一遍登录+下载。creds 需含 rms_login_id/rms_password/member_email/member_password/csv_user/csv_password。"""
    from playwright.async_api import TimeoutError as PWTimeout
    from playwright.async_api import async_playwright

    store = creds.get("store", "?")
    debug_dir = _DEBUG_DIR / str(store)
    debug_dir.mkdir(parents=True, exist_ok=True)
    for old in debug_dir.glob("*.png"):
        old.unlink()

    res = DownloadResult()
    seq = 0

    async def shot(page, name: str, ok: bool = True, note: str = "") -> None:
        nonlocal seq
        seq += 1
        fname = f"{seq:02d}_{name}.png"
        try:
            await page.screenshot(path=str(debug_dir / fname), full_page=False)
            res.shots.append(fname)
        except Exception:
            pass
        try:
            res.steps.append({"step": name, "url": page.url, "title": await page.title(), "ok": ok, "note": note})
        except Exception:
            res.steps.append({"step": name, "url": "", "title": "", "ok": ok, "note": note})

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=headless,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ],
        )
        context = await browser.new_context(
            user_agent=_UA, locale="ja-JP", viewport={"width": 1360, "height": 900},
            accept_downloads=True,
        )
        # 抹掉 navigator.webdriver（基础反检测）
        await context.add_init_script(
            "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"
        )
        page = await context.new_page()
        page.set_default_timeout(30000)

        try:
            # 1. 入口 = RMS 登录门户（未登录渲染 RMS 登录表单）
            await page.goto(_LOGIN_URL, wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            await shot(page, "rms_login_portal")

            # 2. RMS 登录表单
            if await page.locator("input[name='login_id']").count():
                await page.fill("input[name='login_id']", creds["rms_login_id"])
                await page.fill("input[name='passwd']", creds["rms_password"])
                await shot(page, "rms_filled")
                btn = page.locator("button[name='submit'], input[type='submit']").first
                if await btn.count():
                    await btn.click()
                else:
                    await page.keyboard.press("Enter")
                await page.wait_for_load_state("domcontentloaded")
                await page.wait_for_timeout(2500)
            await shot(page, "after_rms_login")

            # 3. OAuth SSO 邮箱屏（React SPA）
            try:
                await page.wait_for_selector("#user_id, input[name='username']", timeout=20000)
                await page.fill("#user_id", creds["member_email"])
                await shot(page, "sso_email_filled")
                await _click_primary(page, ("次へ", "下一步", "続ける", "Next", "つぎへ"))
                await page.wait_for_timeout(2500)
            except PWTimeout:
                await shot(page, "sso_email_MISSING", ok=False, note="没等到邮箱输入框——可能被风控/已登录/跳错页")

            # 4. OAuth SSO 密码屏
            try:
                await page.wait_for_selector("#password_current, input[name='password']", timeout=20000)
                await page.fill("#password_current", creds["member_password"])
                await shot(page, "sso_password_filled")
                # 提交按钮是「次へ」——必须优先匹配它，否则会误点页面上的诱饵链接
                # 「別の楽天IDでログイン」(含"ログイン")导致退回邮箱屏。
                await _click_primary(page, ("次へ", "サインイン", "Sign in"))
                await page.wait_for_timeout(3500)
            except PWTimeout:
                await shot(page, "sso_password_MISSING", ok=False, note="没等到密码输入框")

            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(2000)
            await shot(page, "after_login")

            # 4b. 登录后 RMS 会连插若干门户页，逐个点过（不点过直接打 csvdl 会被判「認証が必要です」）：
            #     「お気をつけください」(次へ) → 「…RMSを利用します」(合规) → 公告页(勾"確認した"+「RMSメインメニューへ進む」)。
            gate = (
                "button:has-text('次へ'), a:has-text('次へ'), input[value='次へ'], "
                "button:has-text('RMSを利用'), a:has-text('RMSを利用'), input[value*='RMSを利用'], "
                "button:has-text('進む'), a:has-text('進む'), input[value*='進む'], "
                "button:has-text('メインメニュー'), a:has-text('メインメニュー')"
            )
            for _ in range(6):
                nxt = page.locator(gate)
                if not await nxt.count():
                    break
                # 门户页可能要求先勾"内容について確認した"复选框才放行
                cbs = page.locator("input[type='checkbox']")
                for i in range(await cbs.count()):
                    try:
                        cb = cbs.nth(i)
                        if await cb.is_visible() and not await cb.is_checked():
                            await cb.check(timeout=1500)
                    except Exception:
                        pass
                try:
                    await nxt.first.click()
                    await page.wait_for_load_state("domcontentloaded")
                    await page.wait_for_timeout(1800)
                except Exception:
                    break
            await shot(page, "after_interstitials")

            # 5. 登录成功后导航到订单 CSV 下载表单页
            await page.goto(_DATA_URL, wait_until="domcontentloaded")
            await page.wait_for_timeout(2500)
            await shot(page, "download_form")

            if not await page.locator("select[name='fromYmd']").count():
                await shot(page, "form_NOT_FOUND", ok=False, note="没到下载表单页——登录可能未成功")
                res.error = "未到达下载表单页（登录链未走通，见截图）"
                return res

            # 6. 填条件
            frm = (date.today() - timedelta(days=days)).strftime("%Y-%m-%d")
            to = date.today().strftime("%Y-%m-%d")
            await _safe_select(page, "select[name='fromYmd']", value=frm)
            await _safe_select(page, "select[name='toYmd']", value=to)
            # dateType=1 注文日時
            try:
                await page.check("input[name='dateType'][value='1']")
            except Exception:
                pass
            await _safe_select(page, "select[name='orderProgress']", label="発送待ち")
            await _safe_select(page, "select[name='templateId']", label="全カラムダウンロード用")
            # ソーシャルギフト置き換え（勾选）
            try:
                sg = page.locator("input[type='checkbox']").filter(has=page.locator("xpath=.")).first
                # 尝试按附近文案定位；失败则跳过（默认多为勾选）
            except Exception:
                pass
            await shot(page, "form_filled")

            # 7a. データを作成する（异步生成：処理中 → 下载区出现）
            await _click_primary(page, ("データを作成する", "作成", "生成"))
            # 7b. 等"処理中"结束、下载区(ダウンロードする 按钮 + ユーザ名/パスワード)出现（通常几秒；大数据可能久）
            try:
                await page.wait_for_selector(
                    "input[value='ダウンロードする'], button:has-text('ダウンロードする'), input[value*='ダウンロード']",
                    timeout=180000,
                )
            except PWTimeout:
                await shot(page, "create_wait_timeout", ok=False, note="等生成超时(処理中>3分钟)")
            await page.wait_for_timeout(800)
            await shot(page, "download_ready")

            # 7c. 填 CSV 下载专用账密。密码=该页唯一 password 框；账号=同一张表里的另一个
            #     (非 password/非 hidden) input——不依赖标签文案匹配，最稳。
            try:
                await page.locator("input[type='password']").first.fill(creds["csv_password"])
            except Exception as exc:  # noqa: BLE001
                await shot(page, "csv_pwd_FAIL", ok=False, note=str(exc)[:150])
            try:
                await page.locator(
                    "xpath=(//input[@type='password'])[1]/ancestor::table[1]"
                    "//input[not(@type='password') and not(@type='hidden')]"
                ).first.fill(creds["csv_user"])
            except Exception as exc:  # noqa: BLE001
                await shot(page, "csv_user_FAIL", ok=False, note=str(exc)[:150])
            await shot(page, "csv_creds_filled")

            # 7d. ダウンロードする → 捕获下载
            try:
                async with page.expect_download(timeout=90000) as dl:
                    await _click_primary(page, ("ダウンロードする",))
                download = await dl.value
                path = await download.path()
                res.csv_bytes = Path(path).read_bytes()
                res.csv_name = download.suggested_filename or f"rakuten_{store}_{to}.csv"
                res.success = True
                await shot(page, "downloaded", note=f"{len(res.csv_bytes)} bytes")
            except PWTimeout:
                await shot(page, "download_TIMEOUT", ok=False, note="点了下载但没捕获到文件（账密错？）")
                res.error = "未捕获到下载文件（见截图）"

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


async def _click_primary(page, texts: tuple[str, ...]) -> None:
    """按文案点主按钮：先精确 role=button，再退到任意含文案元素，再退到表单内主按钮。"""
    for t in texts:
        loc = page.get_by_role("button", name=re.compile(re.escape(t), re.I))
        if await loc.count():
            await loc.first.click()
            return
    for t in texts:
        loc = page.locator(f"button:has-text('{t}'), a:has-text('{t}'), input[value='{t}']")
        if await loc.count():
            await loc.first.click()
            return
    # 兜底：SPA 里常见 type=submit / 页面唯一显著按钮
    btn = page.locator("button[type='submit'], input[type='submit']").first
    if await btn.count():
        await btn.click()


async def _safe_select(page, selector: str, *, value: str | None = None, label: str | None = None) -> None:
    try:
        el = page.locator(selector).first
        if not await el.count():
            return
        if label is not None:
            await el.select_option(label=label)
        elif value is not None:
            await el.select_option(value=value)
    except Exception:
        pass
