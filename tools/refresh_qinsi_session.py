"""
秦丝生意通 Session 续期工具（在本地 Mac 上运行，不是 NAS）

用法：
  # 本地测试（API 在本机）
  conda run -n wms-mvp python -m tools.refresh_qinsi_session

  # NAS 部署（API 在 NAS）
  conda run -n wms-mvp python -m tools.refresh_qinsi_session --api http://192.168.1.x:8000 --token YOUR_JWT

流程：
  1. 在本地 Mac 打开 Chromium 窗口
  2. 自动填写账号密码，等待你手动完成滑块验证
  3. 登录成功后自动检测，把 cookies 上传到 WMS API
  4. NAS 上的 Docker 服务立即可以用新 cookies 抓取秦丝数据

注意：
  - 每 7 天运行一次即可（gisALogin cookie 有效期 7 天）
  - 需要在本地安装 playwright：conda run -n wms-mvp playwright install chromium
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

import httpx

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
QINSI_USERNAME = env.get("QINSI_USERNAME", "")
QINSI_PASSWORD = env.get("QINSI_PASSWORD", "")
QINSI_BASE_URL = env.get("QINSI_BASE_URL", "https://web.syt.qinsilk.com/gis/admin/")
_DEFAULT_API = env.get("NAS_API_URL", "http://localhost:8000")
_DEFAULT_TOKEN = env.get("NAS_JWT_TOKEN") or None


async def _check_qinsi_auth(cookies: dict[str, str]) -> bool:
    try:
        async with httpx.AsyncClient(cookies=cookies, follow_redirects=True, timeout=10) as client:
            r = await client.get(
                "https://web.syt.qinsilk.com/gis/admin/pubuser/getUserInfo.ac",
                headers={"X-Requested-With": "XMLHttpRequest"},
            )
            return r.json().get("statusCode") == 1
    except Exception:
        return False


async def do_login_and_upload(api_base: str, api_token: str | None) -> bool:
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("❌  Playwright 未安装，请运行：")
        print("    conda run -n wms-mvp pip install playwright")
        print("    conda run -n wms-mvp playwright install chromium")
        return False

    print("=" * 60)
    print("秦丝生意通 Session 续期")
    print("=" * 60)
    print(f"账号: {QINSI_USERNAME or '(未配置，请检查 .env)'}")
    print(f"秦丝: {QINSI_BASE_URL}")
    print(f"WMS:  {api_base}")
    print()

    if not QINSI_USERNAME:
        print("❌  请在 .env 中配置 QINSI_USERNAME 和 QINSI_PASSWORD")
        return False

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=False,
            slow_mo=300,
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

        print("正在打开登录页...")
        await page.goto(QINSI_BASE_URL, wait_until="domcontentloaded", timeout=30_000)
        await page.wait_for_timeout(1500)

        # 自动填写账号密码
        try:
            u = page.locator('#userName').first
            if await u.count():
                await u.fill(QINSI_USERNAME)
                p = page.locator('#pass').first
                await p.fill(QINSI_PASSWORD)
                print("✓  已自动填写账号密码")
                print()
                print("━" * 40)
                print(">>> 请在浏览器里完成滑块验证并点击登录 <<<")
                print("━" * 40)
        except Exception:
            print("提示：请在浏览器里手动输入账号密码并完成验证")

        # 等待登录成功（检测 cookies，最多 5 分钟）
        print()
        print("等待登录成功（最多 5 分钟）...")
        success = False
        for i in range(150):
            await page.wait_for_timeout(2000)
            cookies_list = await context.cookies()
            flat = {c["name"]: c["value"] for c in cookies_list if "qinsilk.com" in c.get("domain", "")}
            if flat and await _check_qinsi_auth(flat):
                print(f"✓  登录成功！获取到 {len(cookies_list)} 个 cookies")
                success = True
                # 上传到 WMS API
                await _upload_cookies(api_base, api_token, cookies_list)
                break
            if i % 5 == 0 and i > 0:
                remaining = 300 - i * 2
                print(f"  等待中... 剩余 {remaining} 秒")

        if not success:
            print("❌  超时（5分钟），请重试")

        await page.wait_for_timeout(2000)
        await browser.close()
        return success


async def _upload_cookies(api_base: str, api_token: str | None, cookies_list: list) -> None:
    target = f"{api_base.rstrip('/')}/api/v1/qinsi/upload-session"

    # 如果 api_base 是本地，直接写文件更简单
    if "localhost" in api_base or "127.0.0.1" in api_base:
        session_file = project_root / "app" / "data" / "qinsi_session.json"
        session_file.parent.mkdir(parents=True, exist_ok=True)
        session_file.write_text(json.dumps(cookies_list, ensure_ascii=False, indent=2))
        print(f"✓  Session 已直接写入本地文件: {session_file}")
        return

    # 远程上传到 NAS API
    if not api_token:
        print("⚠   未提供 --token，无法上传到远程 WMS")
        print("    本地保存 cookies 到 qinsi_session_backup.json，请手动复制到 NAS")
        bak = project_root / "app" / "data" / "scraper_debug" / "qinsi_session_backup.json"
        bak.parent.mkdir(parents=True, exist_ok=True)
        bak.write_text(json.dumps(cookies_list, ensure_ascii=False, indent=2))
        print(f"    文件: {bak}")
        return

    print(f"正在上传到 {target} ...")
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(
                target,
                json={"cookies": cookies_list},
                headers={"Authorization": f"Bearer {api_token}"},
            )
            data = r.json()
            if data.get("ok"):
                print(f"✓  {data['message']}")
                print("  NAS 上的秦丝同步已可以使用！")
            else:
                print(f"❌  上传失败: {data.get('message', r.text[:200])}")
    except Exception as exc:
        print(f"❌  上传请求失败: {exc}")
        print("    备份文件保存中...")
        bak = project_root / "app" / "data" / "scraper_debug" / "qinsi_session_backup.json"
        bak.write_text(json.dumps(cookies_list, ensure_ascii=False, indent=2))
        print(f"    {bak}")


def main():
    parser = argparse.ArgumentParser(description="秦丝生意通 Session 续期工具")
    parser.add_argument(
        "--api",
        default=_DEFAULT_API,
        help=f"WMS API 地址（默认读取 .env NAS_API_URL: {_DEFAULT_API}）",
    )
    parser.add_argument(
        "--token",
        default=_DEFAULT_TOKEN,
        help="WMS JWT token（默认读取 .env NAS_JWT_TOKEN）",
    )
    args = parser.parse_args()
    asyncio.run(do_login_and_upload(args.api, args.token))


if __name__ == "__main__":
    main()
