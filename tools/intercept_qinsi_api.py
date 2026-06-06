"""
拦截秦丝生意通的登录API请求

步骤：
1. 启动 Chromium（有界面）
2. 监听所有 XHR/fetch 请求
3. 用户在浏览器里手动登录（含滑块验证）
4. 脚本捕获并打印登录请求的 URL、headers、body、response
5. 之后所有页面请求也会被打印

这样我们就能知道后端 API，之后用 httpx 直接调，不再需要浏览器。

运行：
  conda run -n wms-mvp python -m tools.intercept_qinsi_api
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent

def load_env(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env

env = load_env(project_root / ".env")
BASE_URL = env.get("QINSI_BASE_URL", "https://web.syt.qinsilk.com/gis/admin/")

DEBUG_DIR = project_root / "app" / "data" / "scraper_debug"
DEBUG_DIR.mkdir(parents=True, exist_ok=True)

captured: list[dict] = []

def should_log(url: str) -> bool:
    """过滤掉静态资源，只看API请求"""
    skip = [".js", ".css", ".png", ".jpg", ".gif", ".ico", ".woff", ".ttf", ".svg"]
    return not any(url.endswith(s) or f"{s}?" in url for s in skip)


async def main():
    from playwright.async_api import async_playwright, Request, Response

    print("=" * 60)
    print("秦丝生意通 API 拦截工具")
    print("=" * 60)
    print(f"目标: {BASE_URL}")
    print()
    print("操作步骤：")
    print("  1. 浏览器窗口打开后，【手动】输入账号密码并完成验证码")
    print("  2. 登录成功后，随便浏览几个页面（出入库记录等）")
    print("  3. 回到此终端按 Ctrl+C 结束，API 信息会被保存")
    print()

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",  # 隐藏自动化特征
            ],
        )
        context = await browser.new_context(
            locale="zh-CN",
            timezone_id="Asia/Tokyo",
            # 模拟正常浏览器 UA
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )

        # 隐藏 webdriver 标志
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """)

        page = await context.new_page()

        # ── 监听所有请求和响应 ──────────────────────────────────────
        async def on_request(request: Request):
            url = request.url
            if not should_log(url):
                return
            entry = {
                "type": "REQUEST",
                "method": request.method,
                "url": url,
                "headers": dict(request.headers),
                "post_data": request.post_data,
            }
            captured.append(entry)
            print(f"\n→ {request.method} {url[:120]}")
            if request.post_data:
                try:
                    body = json.loads(request.post_data)
                    # 隐藏密码
                    if "password" in body:
                        body["password"] = "***"
                    print(f"  Body: {json.dumps(body, ensure_ascii=False)[:300]}")
                except Exception:
                    print(f"  Body: {request.post_data[:200]}")

        async def on_response(response: Response):
            url = response.url
            if not should_log(url):
                return
            status = response.status
            try:
                body = await response.json()
                body_str = json.dumps(body, ensure_ascii=False)[:300]
            except Exception:
                try:
                    body_str = (await response.text())[:200]
                except Exception:
                    body_str = "(binary)"
            entry = {
                "type": "RESPONSE",
                "status": status,
                "url": url,
                "body_preview": body_str,
            }
            captured.append(entry)
            print(f"  ← {status} {url[:100]}")
            print(f"     {body_str[:150]}")

        page.on("request", on_request)
        page.on("response", on_response)

        await page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30_000)
        print("\n[浏览器已打开]")
        print("请在浏览器里：")
        print("  1. 手动输入账号密码")
        print("  2. 完成滑块验证")
        print("  3. 登录后点击「出入库记录」页面看一看")
        print()
        print("脚本等待 120 秒，期间所有网络请求都会被记录。")
        print("等够了会自动关闭浏览器并保存结果。")
        print()

        # 倒计时等待，每10秒打印一次提示
        WAIT_SECONDS = 120
        for remaining in range(WAIT_SECONDS, 0, -10):
            await asyncio.sleep(10)
            current_url = page.url
            cookies = await context.cookies()
            print(f"  [剩余 {remaining-10}s] URL: {current_url[:80]}  Cookies: {len(cookies)}个")

        # 保存截图
        await page.screenshot(path=str(DEBUG_DIR / "intercept_final.png"), full_page=True)

        # 保存当前 cookies
        cookies = await context.cookies()
        cookie_path = DEBUG_DIR / "qinsi_cookies.json"
        cookie_path.write_text(json.dumps(cookies, indent=2, ensure_ascii=False))
        print(f"\n✓ Cookies 已保存: {cookie_path}")

        # 同时复制到 scraper 使用的 session 文件
        session_path = project_root / "app" / "data" / "qinsi_session.json"
        session_path.parent.mkdir(parents=True, exist_ok=True)
        session_path.write_text(json.dumps(cookies, indent=2, ensure_ascii=False))
        print(f"✓ Session 文件已更新: {session_path}")
        print(f"  Cookie 数量: {len(cookies)}")
        for c in cookies:
            print(f"    {c['name']} = {str(c['value'])[:40]}...")

        # 保存所有捕获的请求
        log_path = DEBUG_DIR / "api_calls.json"
        log_path.write_text(json.dumps(captured, indent=2, ensure_ascii=False))
        print(f"\n✓ API 请求日志已保存: {log_path}")
        print(f"  共捕获 {len(captured)} 条记录")

        # 找出关键的 API 请求
        print("\n=== 关键 API 请求（非静态资源）===")
        seen_urls: set[str] = set()
        for entry in captured:
            if entry["type"] == "REQUEST" and entry["url"] not in seen_urls:
                seen_urls.add(entry["url"])
                url = entry["url"]
                # 跳过第三方
                if "qinsilk.com" in url or "syt.qinsilk" in url:
                    print(f"  {entry['method']} {url}")

        await browser.close()

    print("\n完成！根据上面的 API 列表，我们可以直接用 httpx 调用，不再需要浏览器。")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n已退出")
