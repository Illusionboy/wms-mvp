"""
最终确认：秦丝出入库记录 + 商品明细结构。

运行：
  conda run -n wms-mvp python -m tools.test_qinsi_api3
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

raw_cookies = json.loads((DEBUG_DIR / "qinsi_cookies.json").read_text())
cookies = {c["name"]: c["value"] for c in raw_cookies if "qinsilk.com" in c.get("domain", "")}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://web.syt.qinsilk.com/gis/admin/main.ac",
    "X-Requested-With": "XMLHttpRequest",
}

today = date.today()
week_ago = today - timedelta(days=7)
t_begin = week_ago.strftime("%Y-%m-%d 00:00:00")
t_end   = today.strftime("%Y-%m-%d 23:59:59")


async def main():
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=True, timeout=20) as client:

        # ── 1. storeOrderList: 出入库记录列表 ─────────────────────────────
        print("=== 1. 出入库记录列表 (storeOrderList) ===")

        # 先试 GET
        r = await client.get(f"{BASE}/inner/storehouse/storeOrderList.ac", params={
            "mid": 3, "page": 1, "rows": 10,
            "createTimeBegin": t_begin, "createTimeEnd": t_end,
            "_search": "false",
        }, headers=HEADERS)
        print(f"  GET → {r.status_code}  ({len(r.text)}B)")
        print(f"  前500字: {r.text[:500]}")

        # 再试 storeOrderListJSON
        r2 = await client.get(f"{BASE}/inner/storehouse/storeOrderListJSON.ac", params={
            "page": 1, "rows": 10,
            "createTimeBegin": t_begin, "createTimeEnd": t_end,
            "_search": "false",
        }, headers=HEADERS)
        print(f"\n  GET storeOrderListJSON → {r2.status_code}  ({len(r2.text)}B)")
        if r2.status_code == 200:
            try:
                data = r2.json()
                print(f"  keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                rows = data.get("rows", []) if isinstance(data, dict) else []
                print(f"  行数: {len(rows)}")
                if rows:
                    print(f"  第一行: {json.dumps(rows[0], ensure_ascii=False)[:400]}")
                    (DEBUG_DIR / "storeOrderListJSON_sample.json").write_text(
                        json.dumps(data, indent=2, ensure_ascii=False)
                    )
                    print("  ✓ 保存到 storeOrderListJSON_sample.json")
            except Exception as e:
                print(f"  JSON解析失败: {e}")
                print(f"  响应: {r2.text[:300]}")

        # ── 2. 销售单商品明细 orderGoods ──────────────────────────────────
        print("\n=== 2. 销售单 orderGoods 字段 ===")
        r = await client.get(f"{BASE}/inner/sale/wholesaleOrdersListJSON.ac", params={
            "itemType": 1, "state": 12,
            "createTimeBegin": t_begin, "createTimeEnd": t_end,
            "rows": 1, "page": 1, "_search": "false", "isShowPrintCounts": 1,
        }, headers=HEADERS)
        rows = r.json().get("rows", [])
        if rows:
            sn = rows[0]["ordersSn"]
            r2 = await client.post(
                f"{BASE}/inner/sale/wholesaleOrdersGet.ac?ordersSn={sn}",
                json={}, headers={**HEADERS, "Content-Type": "application/json"},
            )
            data = r2.json()
            order_goods = data.get("orderGoods", [])
            print(f"  salesSn={sn}  orderGoods: {len(order_goods)} 项")
            for g in order_goods[:3]:
                print(f"    {json.dumps(g, ensure_ascii=False)[:400]}")
            (DEBUG_DIR / "sale_order_detail.json").write_text(
                json.dumps(data, indent=2, ensure_ascii=False)
            )
            print("  ✓ 完整响应已保存到 sale_order_detail.json")

        # ── 3. 采购单商品明细 orderGoods ──────────────────────────────────
        print("\n=== 3. 采购单 orderGoods 字段 ===")
        r = await client.get(f"{BASE}/inner/orders/purchase/purchaseListJSON.ac", params={
            "itemType": 1, "state": 12,
            "createTimeBegin": t_begin, "createTimeEnd": t_end,
            "rows": 1, "page": 1, "_search": "false",
        }, headers=HEADERS)
        rows = r.json().get("rows", [])
        if rows:
            sn = rows[0]["purchaseSn"]
            r2 = await client.post(
                f"{BASE}/inner/orders/purchase/purchaseGet.ac?purchaseSn={sn}",
                json={}, headers={**HEADERS, "Content-Type": "application/json"},
            )
            data = r2.json()
            order_goods = data.get("orderGoods", [])
            print(f"  purchaseSn={sn}  orderGoods: {len(order_goods)} 项")
            for g in order_goods[:3]:
                print(f"    {json.dumps(g, ensure_ascii=False)[:400]}")
            (DEBUG_DIR / "purchase_order_detail.json").write_text(
                json.dumps(data, indent=2, ensure_ascii=False)
            )
            print("  ✓ 完整响应已保存到 purchase_order_detail.json")

        # ── 4. 库存现量（goodsStoredList）─────────────────────────────────
        print("\n=== 4. 库存现量 goodsStoredListJSON ===")
        r = await client.get(f"{BASE}/inner/storehouse/goodsStoredListJSON.ac", params={
            "page": 1, "rows": 5, "_search": "false",
        }, headers=HEADERS)
        print(f"  → {r.status_code}  {r.text[:400]}")


if __name__ == "__main__":
    asyncio.run(main())
