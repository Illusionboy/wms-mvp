"""
秦丝生意通爬虫调试脚本

用法：
  cd "New project"
  conda run -n wms-mvp python -m tools.test_qinsi_scraper

功能：
  1. 登录秦丝生意通，截图记录每一步
  2. 尝试导航到出入库记录
  3. 打印页面上找到的所有 <table> 的 id/class 和列标题
  4. 所有截图保存到 app/data/scraper_debug/
  5. 如果成功找到数据表，打印前5行作为样本

不写数据库，纯探索用。
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

# ── 读取 .env ────────────────────────────────────────────────────────────────
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"

def load_env(path: Path) -> dict[str, str]:
    env = {}
    if not path.exists():
        return env
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env

env = load_env(env_path)
QINSI_USERNAME = env.get("QINSI_USERNAME", "")
QINSI_PASSWORD = env.get("QINSI_PASSWORD", "")
QINSI_BASE_URL = env.get("QINSI_BASE_URL", "https://web.syt.qinsilk.com/gis/admin/")

DEBUG_DIR = project_root / "app" / "data" / "scraper_debug"
DEBUG_DIR.mkdir(parents=True, exist_ok=True)

if not QINSI_USERNAME or not QINSI_PASSWORD:
    print("❌  QINSI_USERNAME / QINSI_PASSWORD 未在 .env 中配置")
    sys.exit(1)

print(f"✓  账号: {QINSI_USERNAME}")
print(f"✓  目标: {QINSI_BASE_URL}")
print(f"✓  截图目录: {DEBUG_DIR}\n")


# ── 选择器（与 qinsi_scraper.py 保持一致，可直接修改这里测试）────────────────
SELECTORS = {
    "login_username": [
        'input[name="loginName"]',
        'input[placeholder*="账号"]',
        'input[placeholder*="用户名"]',
        'input[type="text"]:first-of-type',
    ],
    "login_password": [
        'input[name="password"]',
        'input[type="password"]',
    ],
    "login_submit": [
        'button[type="submit"]',
        'button:has-text("登录")',
        '.login-btn',
        'input[type="submit"]',
    ],
    "post_login_indicator": [
        '.ant-layout-sider',
        '.sidebar',
        '[class*="menu"]',
        'nav',
        '.el-menu',
    ],
    "nav_inventory": [
        'li:has-text("库存")',
        'a:has-text("库存管理")',
        '[class*="menu-item"]:has-text("库存")',
    ],
    "nav_stock_record": [
        'li:has-text("出入库")',
        'a:has-text("出入库记录")',
        'a:has-text("出入库明细")',
        '[class*="menu-item"]:has-text("出入库")',
    ],
}


async def screenshot(page, name: str) -> Path:
    p = DEBUG_DIR / f"{name}.png"
    await page.screenshot(path=str(p), full_page=True)
    print(f"  📸 截图: {p.name}")
    return p


async def try_selectors(page, candidates: list[str]) -> tuple[str | None, object]:
    for sel in candidates:
        try:
            el = page.locator(sel).first
            if await el.count() > 0:
                return sel, el
        except Exception:
            continue
    return None, None


async def main():
    from playwright.async_api import async_playwright

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=False,  # 有窗口方便观察，确认后改 True
            slow_mo=500,     # 放慢500ms，看清每一步
            args=["--no-sandbox"],
        )
        context = await browser.new_context(
            locale="zh-CN",
            timezone_id="Asia/Tokyo",
        )
        page = await context.new_page()

        # ── Step 1: 打开登录页 ──────────────────────────────────────────────
        print("─── Step 1: 打开登录页 ───")
        await page.goto(QINSI_BASE_URL, wait_until="domcontentloaded", timeout=30_000)
        await page.wait_for_timeout(2000)
        await screenshot(page, "01_login_page")
        print(f"  URL: {page.url}")

        # 探索登录页结构
        inputs = await page.locator("input").all()
        print(f"  找到 input 元素: {len(inputs)} 个")
        for i, inp in enumerate(inputs[:6]):
            t = await inp.get_attribute("type") or "text"
            nm = await inp.get_attribute("name") or ""
            ph = await inp.get_attribute("placeholder") or ""
            print(f"    [{i}] type={t} name={nm!r} placeholder={ph!r}")

        # ── Step 2: 填写登录表单 ────────────────────────────────────────────
        print("\n─── Step 2: 填写登录表单 ───")
        matched_u, u_el = await try_selectors(page, SELECTORS["login_username"])
        if not u_el:
            print("  ❌ 找不到用户名输入框，请看截图后更新 SELECTORS['login_username']")
            await screenshot(page, "02_no_username_input")
            await browser.close()
            return
        print(f"  ✓ 用户名框: {matched_u}")
        await u_el.fill(QINSI_USERNAME)

        matched_p, p_el = await try_selectors(page, SELECTORS["login_password"])
        if not p_el:
            print("  ❌ 找不到密码输入框")
            await screenshot(page, "02_no_password_input")
            await browser.close()
            return
        print(f"  ✓ 密码框: {matched_p}")
        await p_el.fill(QINSI_PASSWORD)

        await screenshot(page, "02_form_filled")

        matched_s, submit = await try_selectors(page, SELECTORS["login_submit"])
        if not submit:
            print("  ❌ 找不到登录按钮，尝试按 Enter")
            await page.keyboard.press("Enter")
        else:
            print(f"  ✓ 登录按钮: {matched_s}")
            await submit.click()

        # ── Step 3: 等待登录结果 ────────────────────────────────────────────
        print("\n─── Step 3: 等待登录跳转 ───")
        await page.wait_for_timeout(3000)
        await screenshot(page, "03_after_login")
        print(f"  URL: {page.url}")

        matched_ind, indicator = await try_selectors(page, SELECTORS["post_login_indicator"])
        if not indicator:
            print("  ❌ 未检测到已登录状态，请检查账号密码或验证码")
            print("  提示：查看截图 03_after_login.png")
            # 打印页面 title 和 body 开头
            title = await page.title()
            print(f"  页面标题: {title}")
            body_text = await page.locator("body").inner_text()
            print(f"  页面文本前300字符:\n    {body_text[:300]}")
            await browser.close()
            return
        print(f"  ✓ 已登录，检测到: {matched_ind}")

        # ── Step 4: 探索导航结构 ────────────────────────────────────────────
        print("\n─── Step 4: 探索导航菜单 ───")
        # 打印所有菜单文本
        nav_els = await page.locator("nav, .ant-menu, .el-menu, [class*='sidebar'], [class*='menu']").all()
        for el in nav_els[:3]:
            text = (await el.inner_text()).strip()
            if text:
                print(f"  菜单文本（前200字）: {text[:200]}")

        # 尝试导航到出入库记录
        print("\n─── Step 5: 尝试导航到出入库记录 ───")

        # 先试直接 URL hash
        fragments_to_try = [
            "#/inventoryLog",
            "#/stockRecord",
            "#/inoutRecord",
            "#/warehouseRecord",
        ]
        nav_success = False
        for frag in fragments_to_try:
            target = QINSI_BASE_URL.rstrip("/") + "/" + frag
            print(f"  尝试: {target}")
            await page.goto(target, wait_until="domcontentloaded", timeout=10_000)
            await page.wait_for_timeout(2000)
            tables = await page.locator("table").all()
            if tables:
                print(f"  ✓ 找到表格 ({len(tables)}个)！URL: {page.url}")
                nav_success = True
                break

        if not nav_success:
            print("  直接URL未成功，尝试菜单点击…")
            matched_inv, inv_el = await try_selectors(page, SELECTORS["nav_inventory"])
            if inv_el:
                print(f"  ✓ 点击: {matched_inv}")
                await inv_el.click()
                await page.wait_for_timeout(1000)

            matched_rec, rec_el = await try_selectors(page, SELECTORS["nav_stock_record"])
            if rec_el:
                print(f"  ✓ 点击: {matched_rec}")
                await rec_el.click()
                await page.wait_for_timeout(2000)
                nav_success = True

        await screenshot(page, "05_record_page")
        print(f"  URL: {page.url}")

        # ── Step 6: 探索页面上的所有表格 ────────────────────────────────────
        print("\n─── Step 6: 探索页面表格 ───")
        tables = await page.locator("table").all()
        print(f"  找到 table 元素: {len(tables)} 个")

        for ti, tbl in enumerate(tables[:5]):
            tbl_id = await tbl.get_attribute("id") or ""
            tbl_cls = (await tbl.get_attribute("class") or "")[:60]
            headers = await tbl.locator("th").all_inner_texts()
            print(f"\n  Table[{ti}] id={tbl_id!r} class=…{tbl_cls}…")
            if headers:
                print(f"  列标题({len(headers)}列): {headers}")
            # 前3行数据
            rows = await tbl.locator("tbody tr").all()
            print(f"  数据行数: {len(rows)}")
            for ri, row in enumerate(rows[:3]):
                cells = await row.locator("td").all_inner_texts()
                print(f"    行{ri}: {cells}")

        # 保存当前页完整 HTML 供分析
        html_path = DEBUG_DIR / "06_record_page.html"
        html = await page.content()
        html_path.write_text(html, encoding="utf-8")
        print(f"\n  完整 HTML 已保存: {html_path.name} ({len(html)//1024}KB)")

        print("\n─── 完成 ───")
        print("请查看截图目录：", DEBUG_DIR)
        print("根据实际页面结构更新 app/scrapers/qinsi_scraper.py 里的 DEFAULT_SELECTORS")

        await page.wait_for_timeout(3000)  # 停留3秒观察
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
