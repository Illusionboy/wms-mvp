# 供应链分析与需求预测 — 开发备忘

## 当前数据模型（2026-06，已更新）

每笔库存变动都写入 `stock_transactions`，以下字段现已可用于分析：

| 字段 | 说明 |
|------|------|
| `transaction_type` | `IN` / `OUT` / `ADJUST` |
| `quantity_change` | 变动数量，OUT 为负值 |
| `source` | 数据来源（见下表） |
| `reference_id` | 秦丝记录：`qinsi:{order_no}:{jan_code}`；贸易出库：`trade:{draft_id}:{line_index}` |
| `transaction_date` | **实际业务日期**（独立列，见下方"写入情况"） |
| `created_at` | WMS 录入时间（`transaction_date` 为 NULL 时的回退） |
| `customer` | 出库对方（结构化列，见下方"写入情况"） |
| `supplier` | 入库对方（结构化列，见下方"写入情况"） |
| `note` | 自由文本备注 |
| `user_id` | 操作人 FK → `users` |
| `inventory_record_id` | FK → `inventory_records` → `product_jan` / `warehouse_id` |

### source 可选值

| source | 含义 |
|--------|------|
| `rakuten_csv` | 乐天 RMS 出货 CSV |
| `qinsi_scrape` | 秦丝生意通同步（采购/销售单） |
| `chat_report` | 微信报库 AI 解析 |
| `physical_count` | 月末盘点 ADJUST |
| `web_ui` | 手动入库/出库/调整 |
| `trade_shipment` | 贸易批发出库（Excel/拍照上传，Gemini 解析） |
| `telegram` | Telegram bot（仅查询，不产生 transaction） |

### `transaction_date` 写入情况

| 来源 | 写入逻辑 |
| --- | --- |
| 秦丝批量 | `ScrapedRecord.record_date`（秦丝订单实际日期） |
| 盘点 ADJUST | `document.count_date`（盘点当天） |
| 手动入/出/调整 | 前端可选日期选择器（留空为 NULL） |
| 乐天 CSV / 微信报库 / 贸易出库 | **暂为 NULL**，查询时回退到 `created_at` — 见下方「待办」 |

### `customer` / `supplier` 写入情况

| 来源 | 字段 | 取值 |
| --- | --- | --- |
| 秦丝同步 apply | OUT → `customer`；IN → `supplier` | `ScrapedRecord.customer_name`（秦丝订单对方名称） |
| 贸易出库 apply | `customer` | 客户代码（mm/kk/cp/hn/xm/mmm 等） |
| 其余来源 | NULL | — |

`customer`/`supplier` 仅用于分析查询，**不影响** `InventoryRecord` 库存桶定位（桶仍按 `(product_jan, warehouse_id)`）。

---

## 已实现的历史查询端点 (`app/api/v1/endpoints/analytics.py`)

只读、无需认证：

- `GET /api/v1/analytics/counterparties` — 所有出现过的 `supplier`/`customer` 名称列表
- `GET /api/v1/analytics/supplier-history?supplier=...&from_date=...&to_date=...&warehouse_id=...` — 按供应商查 IN 事务
- `GET /api/v1/analytics/customer-history?customer=...&from_date=...&to_date=...&warehouse_id=...` — 按客户查 OUT 事务
- `GET /api/v1/analytics/product-history?jan_code=...&from_date=...&to_date=...&transaction_type=...` — 按 JAN 查全部事务
- `GET /api/v1/analytics/product-summary?jan_code=...&from_date=...&to_date=...` — 按 JAN 聚合 IN/OUT/ADJUST 总量

日期过滤对 `transaction_date IS NULL` 的记录宽松放行，避免历史数据因缺失日期被排除。

另有 `POST /api/v1/rakuten/order-analysis`（`app/api/v1/endpoints/rakuten_order.py`）：上传乐天订单文件，按 JAN 汇总并与「乐天仓库」库存比对（`ok`/`insufficient`/`no_record`/`unknown`），只读不写入。

---

## 待办（分析时仍会踩的坑）

### 1. transaction_date 在乐天 CSV / 微信报库 / 贸易出库中仍为 NULL

- **现状**：Rakuten CSV 中有配送日期列、微信报库 AI 解析结果中有交易日期字段，贸易出库有上传/单据日期，但三者 apply 逻辑均未写入 `transaction_date`。
- **影响**：这三类事务的时序分析只能用 `created_at`（录入时间），可能比实际业务日期滞后。
- **解决方案**：在对应 apply 逻辑中补全写入，参考秦丝同步 (`ScrapedRecord.record_date`) 和盘点 (`document.count_date`) 的现有写法。

**优先级：中**

---

### 2. 无采购与销售的配对（Lead Time 计算）

- **现状**：入库和出库分别记录，但没有"这批货是为了履行哪个订单"的关联。
- **影响**：无法直接计算从采购到售出的库存周转天数；Lead Time 只能靠统计均值估算。
- **解决方案**：需要引入"采购单"概念，或至少在入库 transaction 上记录 `purchase_order_no`。

**优先级：低** — 待供应商关系稳定后再做。

---

### 3. 无 ABC 速度分级

- **现状**：产品表无 `velocity_class` 字段（CLAUDE.md 中有规划）。
- **影响**：无法自动识别高频 SKU（A 类）来优化库位和补货策略。
- **解决方案**：定期任务（每月）按 SKU 出库量排序，写入 `Product.velocity_class` ('A'/'B'/'C')。

**优先级：低** — 需要历史数据积累后才有意义。

---

## 实施路线建议

```
已完成
├── transaction_date 列（秦丝/盘点/手动已写入）
├── customer/supplier 结构化列（秦丝/贸易出库已写入）
└── 历史查询端点 (/analytics/*) + 乐天订单库存比对 (/rakuten/order-analysis)

第一阶段（数据质量收尾）
└── 补全 transaction_date：乐天 CSV / 微信报库 / 贸易出库

第二阶段（分析应用）
├── 导出接口 / BI 连接（Metabase / Grafana / Superset），可直接调用 /analytics/* 端点
├── ABC 分级定期任务
└── 安全库存阈值自动计算（基于历史出库均值 + 标准差）

第三阶段（进阶）
├── Lead Time 追踪（采购单与入库配对）
└── 需求预测模型（移动平均 / 简单回归，输入：/analytics/product-history 时序数据）
```

---

## 当前可用的分析查询示例

```sql
-- 按月按SKU出库量（优先用 transaction_date，缺失时回退 created_at）
SELECT
    date_trunc('month', COALESCE(st.transaction_date, st.created_at::date)) AS month,
    ir.product_jan,
    p.name_jp,
    SUM(ABS(st.quantity_change)) AS total_out
FROM stock_transactions st
JOIN inventory_records ir ON ir.id = st.inventory_record_id
JOIN products p ON p.jan_code = ir.product_jan
WHERE st.transaction_type = 'OUT'
  AND st.source IN ('rakuten_csv', 'qinsi_scrape', 'chat_report', 'trade_shipment')
GROUP BY 1, 2, 3
ORDER BY 1 DESC, 4 DESC;

-- 按渠道(source)出库对比
SELECT
    source,
    date_trunc('month', COALESCE(transaction_date, created_at::date)) AS month,
    SUM(ABS(quantity_change)) AS qty
FROM stock_transactions
WHERE transaction_type = 'OUT'
GROUP BY 1, 2
ORDER BY 2 DESC, 3 DESC;

-- 按客户出库汇总（结构化 customer 列，秦丝/贸易出库适用）
SELECT
    customer,
    ir.product_jan,
    p.name_jp,
    SUM(ABS(st.quantity_change)) AS total_out
FROM stock_transactions st
JOIN inventory_records ir ON ir.id = st.inventory_record_id
JOIN products p ON p.jan_code = ir.product_jan
WHERE st.transaction_type = 'OUT' AND st.customer IS NOT NULL
GROUP BY 1, 2, 3
ORDER BY 1, 4 DESC;

-- 当前负库存清单
SELECT ir.product_jan, p.name_jp, w.name AS warehouse, ir.quantity
FROM inventory_records ir
JOIN products p ON p.jan_code = ir.product_jan
JOIN warehouses w ON w.id = ir.warehouse_id
WHERE ir.quantity < 0
ORDER BY ir.quantity ASC;
```
