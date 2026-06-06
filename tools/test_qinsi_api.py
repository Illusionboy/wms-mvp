"""
用保存的 cookies 直接调秦丝生意通 API，探索出入库记录接口。

运行：
  conda run -n wms-mvp python -m tools.test_qinsi_api
"""
from __future__ import annotations

import asyncio
import json
from datetime import date, timedelta
from pathlib import Path

import httpx

project_root = Path(__file__).parent.parent
DEBUG_DIR = project_root / "app" / "data" / "scraper_debug"
BASE = "https://web.syt.qinsilk.com/gis/admin"

# ── 加载 cookies ──────────────────────────────────────────────────────────────
raw_cookies = json.loads((DEBUG_DIR / "qinsi_cookies.json").read_text())
cookies: dict[str, str] = {}
for c in raw_cookies:
    # 只取 web.syt.qinsilk.com 和 .qinsilk.com 域名的
    if "qinsilk.com" in c.get("domain", ""):
        cookies[c["name"]] = c["value"]

print(f"加载 {len(cookies)} 个 cookies")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://web.syt.qinsilk.com/gis/admin/main.ac",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/json;charset=UTF-8",
}


async def post(client: httpx.AsyncClient, path: str, body: dict | None = None) -> dict:
    r = await client.post(f"{BASE}{path}", json=body or {}, headers=HEADERS)
    print(f"  POST {path} → {r.status_code}")
    try:
        return r.json()
    except Exception:
        print(f"  [non-JSON] {r.text[:200]}")
        return {}


async def get(client: httpx.AsyncClient, path: str, params: dict | None = None) -> dict:
    r = await client.get(f"{BASE}{path}", params=params, headers=HEADERS)
    print(f"  GET  {path} → {r.status_code}")
    try:
        return r.json()
    except Exception:
        print(f"  [non-JSON] {r.text[:200]}")
        return {}


async def main():
    today = date.today()
    week_ago = today - timedelta(days=7)
    date_fmt = "%Y-%m-%d %H:%M:%S"
    t_begin = week_ago.strftime("%Y-%m-%d 00:00:00")
    t_end   = today.strftime("%Y-%m-%d 23:59:59")

    async with httpx.AsyncClient(cookies=cookies, follow_redirects=True, timeout=15) as client:

        # ── 1. 确认 session 有效 ────────────────────────────────────────────
        print("\n=== 1. 验证 Session ===")
        data = await get(client, "/pubuser/getUserInfo.ac")
        if data:
            print(f"  用户: {json.dumps(data, ensure_ascii=False)[:200]}")
        else:
            print("  ❌ Session 已失效，请重新运行 intercept_qinsi_api.py 登录")
            return

        # ── 2. 获取仓库列表 ─────────────────────────────────────────────────
        print("\n=== 2. 仓库列表 ===")
        data = await post(client, "/inner/storehouse/storehouseSelectJSON.ac?showDisable=1&filterComStore=2")
        print(f"  {json.dumps(data, ensure_ascii=False)[:400]}")

        # ── 3. 尝试出入库流水接口（猜测常见路径）──────────────────────────────
        print("\n=== 3. 探索出入库流水接口 ===")
        candidates = [
            ("/inner/storehouse/storehouseFlowListJSON.ac", {"page": 1, "rows": 5,
                "createTimeBegin": t_begin, "createTimeEnd": t_end}),
            ("/inner/storehouse/goodsFlowListJSON.ac", {"page": 1, "rows": 5,
                "createTimeBegin": t_begin, "createTimeEnd": t_end}),
            ("/inner/storehouse/inventoryFlowListJSON.ac", {"page": 1, "rows": 5,
                "createTimeBegin": t_begin, "createTimeEnd": t_end}),
            ("/inner/goods/goodsFlow/goodsFlowListJSON.ac", {"page": 1, "rows": 5}),
            ("/inner/storehouse/stockFlowListJSON.ac", {"page": 1, "rows": 5}),
            ("/inner/storehouse/storehouseRecordListJSON.ac", {"page": 1, "rows": 5}),
        ]
        for path, params in candidates:
            r = await client.get(f"{BASE}{path}", params=params, headers=HEADERS)
            size = len(r.text)
            print(f"  GET {path} → {r.status_code}  ({size}B)")
            if r.status_code == 200 and size > 50:
                try:
                    j = r.json()
                    print(f"    ✓ 有数据: {json.dumps(j, ensure_ascii=False)[:300]}")
                    break
                except Exception:
                    pass

        # ── 4. 采购入库单（已知有效） ────────────────────────────────────────
        print("\n=== 4. 采购单（入库）===")
        data = await get(client, "/inner/orders/purchase/purchaseListJSON.ac", {
            "itemType": 1, "state": 12,
            "createTimeBegin": t_begin, "createTimeEnd": t_end,
            "rows": 5, "page": 1, "sidx": "", "sord": "asc",
            "_search": "false",
        })
        print(f"  {json.dumps(data, ensure_ascii=False)[:500]}")

        # ── 5. 销售出库单（已知有效） ────────────────────────────────────────
        print("\n=== 5. 销售单（出库）===")
        data = await get(client, "/inner/sale/wholesaleOrdersListJSON.ac", {
            "itemType": 1, "state": 12,
            "createTimeBegin": t_begin, "createTimeEnd": t_end,
            "rows": 5, "page": 1, "sidx": "", "sord": "asc",
            "_search": "false", "isShowPrintCounts": 1,
        })
        print(f"  {json.dumps(data, ensure_ascii=False)[:500]}")

        # ── 6. 在销售单里找商品明细结构 ─────────────────────────────────────
        print("\n=== 6. 单据商品明细（以销售单为例）===")
        # 先拿一个 ordersSn
        sale_list = data if isinstance(data, dict) else {}
        rows = sale_list.get("rows", [])
        if rows:
            sn = rows[0].get("ordersSn", "")
            print(f"  示例订单号: {sn}")
            detail = await post(client, f"/inner/sale/wholesaleOrdersGet.ac?ordersSn={sn}")
            goods = detail.get("goodsList", detail.get("goods", []))
            print(f"  商品列表 ({len(goods)} 项):")
            for g in goods[:3]:
                print(f"    {json.dumps(g, ensure_ascii=False)[:200]}")

        # ── 7. 保存原始响应供参考 ────────────────────────────────────────────
        result_path = DEBUG_DIR / "api_explore_result.json"
        result_path.write_text(json.dumps({
            "purchase_sample": sale_list,  # just a placeholder
        }, indent=2, ensure_ascii=False))
        print(f"\n✓ 探索完成，详情见 {result_path}")


if __name__ == "__main__":
    asyncio.run(main())
