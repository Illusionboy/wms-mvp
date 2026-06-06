"""
深入探索秦丝 API：找出入库流水接口 + 看订单商品明细结构。

运行：
  conda run -n wms-mvp python -m tools.test_qinsi_api2
"""
from __future__ import annotations

import asyncio
import json
import re
from datetime import date, timedelta
from pathlib import Path

import httpx

project_root = Path(__file__).parent.parent
DEBUG_DIR = project_root / "app" / "data" / "scraper_debug"
BASE = "https://web.syt.qinsilk.com/gis/admin"

raw_cookies = json.loads((DEBUG_DIR / "qinsi_cookies.json").read_text())
cookies: dict[str, str] = {}
for c in raw_cookies:
    if "qinsilk.com" in c.get("domain", ""):
        cookies[c["name"]] = c["value"]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://web.syt.qinsilk.com/gis/admin/main.ac",
    "X-Requested-With": "XMLHttpRequest",
}

today = date.today()
week_ago = today - timedelta(days=7)
t_begin = week_ago.strftime("%Y-%m-%d 00:00:00")
t_end   = today.strftime("%Y-%m-%d 23:59:59")


async def main():
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=True, timeout=20) as client:

        # ── A. 拉取仓库管理 HTML 模板，解析 JS 里调用的 API 路径 ────────────
        print("=== A. 解析仓库出入库页面模板 ===")
        templates_to_try = [
            "/gis/template/nadmin/inner/storehouse/storehouseFlow.html",
            "/gis/template/nadmin/inner/storehouse/goodsFlow.html",
            "/gis/template/nadmin/inner/storehouse/storehouseRecord.html",
            "/gis/template/nadmin/inner/goods/goodsFlow.html",
            "/gis/template/nadmin/inner/storehouse/storehouseIn.html",
            "/gis/template/nadmin/inner/storehouse/storehouseOut.html",
        ]
        for tmpl in templates_to_try:
            url = f"https://web.syt.qinsilk.com{tmpl}"
            r = await client.get(url, headers=HEADERS)
            if r.status_code == 200 and len(r.text) > 200:
                print(f"  ✓ 找到: {tmpl}  ({len(r.text)}B)")
                # 提取 JS 里出现的 .ac 接口调用
                apis = re.findall(r'[\'"](/gis/[^\'"\s]+\.ac)[\'"]', r.text)
                for a in set(apis):
                    print(f"    API: {a}")
                (DEBUG_DIR / f"tmpl_{tmpl.split('/')[-1]}").write_text(r.text)
            else:
                print(f"  ✗ {tmpl} → {r.status_code}")

        # ── B. 从 main.ac 找导航菜单 URL（含 mid 参数对应的功能模块）─────────
        print("\n=== B. 抓取主页，找导航菜单 ===")
        r = await client.get(f"https://web.syt.qinsilk.com/gis/admin/main.ac", headers=HEADERS)
        if r.status_code == 200:
            html = r.text
            # 找 inner/storehouse 相关链接
            links = re.findall(r'inner/storehouse[^"\'<\s]*', html)
            print(f"  storehouse 相关链接 ({len(links)}个): {list(set(links))[:20]}")
            # 找所有 mid= 参数
            mids = re.findall(r'mid=(\d+)[^>]*>(.*?)</a>', html, re.DOTALL)
            for mid, label in mids[:30]:
                label = re.sub(r'<[^>]+>', '', label).strip()
                if label:
                    print(f"  mid={mid}: {label}")

        # ── C. 尝试用 mid 参数加载仓库流水页 ──────────────────────────────
        print("\n=== C. 试探仓库流水页面 mid ===")
        for mid in range(1, 25):
            r = await client.get(
                f"{BASE}/inner/storehouse/storehouseFlow.ac",
                params={"mid": mid},
                headers={**HEADERS, "X-Requested-With": ""},
            )
            if r.status_code == 200 and "jqgrid" in r.text.lower():
                print(f"  ✓ mid={mid} 找到 jqgrid 页面 ({len(r.text)}B)")
                # 提取 listJSON url
                apis = re.findall(r'url\s*:\s*[\'"]([^\'"]+ListJSON[^\'"]*)[\'"]', r.text)
                print(f"    API: {apis}")
                break
            elif r.status_code == 200:
                print(f"  mid={mid} → 200 but no jqgrid ({len(r.text)}B)")

        # ── D. 订单商品明细（完整 JSON） ────────────────────────────────────
        print("\n=== D. 销售单商品明细（完整响应）===")
        # 先拿最新一笔销售单号
        r = await client.get(f"{BASE}/inner/sale/wholesaleOrdersListJSON.ac", params={
            "itemType": 1, "state": 12,
            "createTimeBegin": t_begin, "createTimeEnd": t_end,
            "rows": 1, "page": 1, "sidx": "", "sord": "asc",
            "_search": "false", "isShowPrintCounts": 1,
        }, headers=HEADERS)
        rows = r.json().get("rows", [])
        if not rows:
            print("  没有销售单")
        else:
            sn = rows[0]["ordersSn"]
            order_id = rows[0]["id"]
            print(f"  销售单: {sn}  id={order_id}")

            # 方法1: POST JSON
            r1 = await client.post(
                f"{BASE}/inner/sale/wholesaleOrdersGet.ac?ordersSn={sn}",
                json={},
                headers={**HEADERS, "Content-Type": "application/json"},
            )
            data1 = r1.json()
            print(f"  wholesaleOrdersGet (JSON POST) keys: {list(data1.keys())}")
            obj = data1.get("object", data1)
            if isinstance(obj, dict):
                print(f"  object keys: {list(obj.keys())}")
                goods = obj.get("goodsList", obj.get("itemList", obj.get("goods", [])))
                print(f"  商品列表 ({len(goods)} 项):")
                for g in goods[:2]:
                    print(f"    {json.dumps(g, ensure_ascii=False)[:300]}")

            # 方法2: 试试 goodsSnList 接口
            r2 = await client.post(
                f"{BASE}/inner/goods/goodssn/goodsSnListJSON.ac?ordersSn={sn}&type=11",
                json={},
                headers={**HEADERS, "Content-Type": "application/json"},
            )
            print(f"\n  goodsSnListJSON → {r2.status_code}: {r2.text[:300]}")

        # ── E. 采购单商品明细 ────────────────────────────────────────────────
        print("\n=== E. 采购单商品明细 ===")
        r = await client.get(f"{BASE}/inner/orders/purchase/purchaseListJSON.ac", params={
            "itemType": 1, "state": 12,
            "createTimeBegin": t_begin, "createTimeEnd": t_end,
            "rows": 1, "page": 1, "sidx": "", "sord": "asc", "_search": "false",
        }, headers=HEADERS)
        rows = r.json().get("rows", [])
        if rows:
            sn = rows[0]["purchaseSn"]
            print(f"  采购单: {sn}")
            r2 = await client.post(
                f"{BASE}/inner/orders/purchase/purchaseGet.ac?purchaseSn={sn}",
                json={},
                headers={**HEADERS, "Content-Type": "application/json"},
            )
            data2 = r2.json()
            print(f"  purchaseGet keys: {list(data2.keys())}")
            obj = data2.get("object", data2)
            if isinstance(obj, dict):
                print(f"  object keys: {list(obj.keys())}")
                goods = obj.get("goodsList", obj.get("itemList", obj.get("goods", [])))
                print(f"  商品列表 ({len(goods)} 项):")
                for g in goods[:2]:
                    print(f"    {json.dumps(g, ensure_ascii=False)[:300]}")

        print("\n✓ 完成")


if __name__ == "__main__":
    asyncio.run(main())
