# 供应链分析与需求预测 — 开发备忘

## 当前数据模型（2026-06）

每笔库存变动都写入 `stock_transactions`，以下字段现已可用于分析：

| 字段 | 说明 |
|------|------|
| `transaction_type` | `IN` / `OUT` / `ADJUST` |
| `quantity_change` | 变动数量，OUT 为负值 |
| `source` | 数据来源（见下表） |
| `reference_id` | 秦丝记录：`qinsi:{order_no}:{jan_code}` |
| `created_at` | WMS 录入时间（≠ 实际业务时间） |
| `note` | 自由文本，秦丝记录含实际日期字符串 |
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

---

## 已知缺陷（分析时会踩的坑）

### 1. 实际业务日期没有独立字段 ⚠️ 最关键

- **现状**：`created_at` 是 WMS 录入时间，可能比实际业务发生滞后数天。
  - 秦丝订单实际日期：埋在 `note` 文本里（`秦丝记录日期:2026-05-10`），不可直接 SQL 过滤。
  - Rakuten CSV：配送日期同样未作为独立列保存。
  - 盘点 ADJUST：`note` 含 `盘点日期:YYYY-MM-DD`，也是文本。
- **影响**：无法直接做时序分析（按周/月销量趋势）；必须 `LIKE` 解析 `note`，脆弱且慢。
- **解决方案**：

```sql
ALTER TABLE stock_transactions ADD COLUMN transaction_date DATE;
```

写入规则：
- 秦丝同步：使用 `ScrapedRecord.record_date`（爬虫从订单获取的实际日期）
- Rakuten CSV：使用 CSV 中的配送/出货日期列
- 手动操作 / 微信报库：默认 `created_at::date`，可选允许操作员手填
- 盘点 ADJUST：使用盘点日期

**优先级：高** — 不加此字段，所有时序分析都要绕路解析文本。

---

### 2. 出库缺少客户/渠道维度

- **现状**：客户字段已从 inventory_record 定位键中移除（2026-06 重构），现在每条 transaction 没有结构化的"出库目的地/客户"字段。
  - 乐天出库：可通过 `source='rakuten_csv'` 识别渠道，但没有具体收货方。
  - 秦丝销售单：`customer_name` 在 `ScrapedRecord` 里，但 apply 时未写入 transaction。
- **影响**：无法做 SKU × 客户/渠道的销量分解；只能区分乐天 vs 普通，无法细分普通渠道的具体客户。
- **解决方案**：

```sql
ALTER TABLE stock_transactions ADD COLUMN channel VARCHAR(64);
-- 或者复用 note 字段补充结构化前缀
```

写入规则：
- 秦丝销售单：写入 `ScrapedRecord.customer_name`
- Rakuten：固定 `'乐天'`
- 微信报库：由 AI 解析结果提供，或操作员手填

**优先级：中** — 当前只有两个主渠道（乐天/普通），暂时够用；多客户场景需要。

---

### 3. 入库缺少供应商字段

- **现状**：秦丝采购单的 `supplier_name` 爬虫已能获取（`ScrapedRecord.customer_name` 对 IN 方向存的是供应商名），但 apply 时未写入 transaction。
- **影响**：无法做 SKU × 供应商的采购分析，无法计算各供应商的供货周期（Lead Time）。
- **解决方案**：同上，用 `channel` 字段或新增 `supplier VARCHAR(64)` 列写入供应商名。

**优先级：中**

---

### 4. 无采购与销售的配对（Lead Time 计算）

- **现状**：入库和出库分别记录，但没有"这批货是为了履行哪个订单"的关联。
- **影响**：无法直接计算从采购到售出的库存周转天数；Lead Time 只能靠统计均值估算。
- **解决方案**：需要引入"采购单"概念，或至少在入库 transaction 上记录 `purchase_order_no`。

**优先级：低** — 待供应商关系稳定后再做。

---

### 5. 无 ABC 速度分级

- **现状**：产品表无 `velocity_class` 字段（CLAUDE.md 中有规划）。
- **影响**：无法自动识别高频 SKU（A 类）来优化库位和补货策略。
- **解决方案**：定期任务（每月）按 SKU 出库量排序，写入 `Product.velocity_class` ('A'/'B'/'C')。

**优先级：低** — 需要历史数据积累后才有意义。

---

## 实施路线建议

```
第一阶段（立即，数据质量）
└── 加 transaction_date 列 + 补全写入逻辑（秦丝/Rakuten/盘点）

第二阶段（数据丰富，渠道分析）
└── 加 channel/supplier 列 → 秦丝 apply 时写入客户/供应商名

第三阶段（分析应用）
└── 导出接口 / BI 连接（Metabase / Grafana / Superset）
└── ABC 分级定期任务
└── 安全库存阈值自动计算（基于历史出库均值 + 标准差）

第四阶段（进阶）
└── Lead Time 追踪（采购单与入库配对）
└── 需求预测模型（移动平均 / 简单回归，输入：时序出库数据）
```

---

## 当前可用的分析查询示例

```sql
-- 按月按SKU出库量（用录入时间，精度有限）
SELECT
    date_trunc('month', st.created_at) AS month,
    ir.product_jan,
    p.name_jp,
    SUM(ABS(st.quantity_change)) AS total_out
FROM stock_transactions st
JOIN inventory_records ir ON ir.id = st.inventory_record_id
JOIN products p ON p.jan_code = ir.product_jan
WHERE st.transaction_type = 'OUT'
  AND st.source IN ('rakuten_csv', 'qinsi_scrape', 'chat_report')
GROUP BY 1, 2, 3
ORDER BY 1 DESC, 4 DESC;

-- 按渠道出库对比
SELECT
    source,
    date_trunc('month', created_at) AS month,
    SUM(ABS(quantity_change)) AS qty
FROM stock_transactions
WHERE transaction_type = 'OUT'
GROUP BY 1, 2
ORDER BY 2 DESC, 3 DESC;

-- 当前负库存清单
SELECT ir.product_jan, p.name_jp, w.name AS warehouse, ir.quantity
FROM inventory_records ir
JOIN products p ON p.jan_code = ir.product_jan
JOIN warehouses w ON w.id = ir.warehouse_id
WHERE ir.quantity < 0
ORDER BY ir.quantity ASC;
```
