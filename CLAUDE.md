# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**WMS MVP** - A warehouse inventory management system. Primary interface is a modern web SPA (`/app`); a Telegram bot serves as a read-only query companion. Designed for NAS/Docker self-hosted deployment.

**Core Purpose**: Enable warehouse operators to manage inventory through a web UI (stock-in/out/adjust, AI-powered chat report parsing, Rakuten CSV import, monthly count reconciliation). The Telegram bot handles queries only (search, status). All mutations require JWT authentication.

## Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 16 (async with asyncpg)
- **ORM**: SQLAlchemy 2.0 with async support
- **Auth**: JWT (PyJWT 2.9.0, HS256, 30-day tokens) + bcrypt (passlib 1.7.4)
- **Telegram**: aiogram 3.17 (polling mode - no public domain required)
- **AI**: Google Gemini API (`google-genai==1.55.0`, model `gemini-2.5-flash`) for structured JSON parsing of chat reports
- **HTML Parsing**: BeautifulSoup4 + lxml (for 秦丝生意通 inventory count sheets)
- **Data Formats**: Excel (openpyxl) for product catalogs and inventory counts, CSV for Rakuten RMS shipments
- **Qinsi ERP Client**: httpx 0.28.1 (async HTTP, no browser) for 秦丝生意通 API calls
- **Container**: Docker Compose (postgres, api, bot services)

## Coding Conventions

- Use Python 3.11+ type hints on all functions and class attributes.
- All database interaction must use SQLAlchemy 2.0 async mode — never use raw SQL strings or sync sessions.
- Every new ORM model must inherit from `Base` and `TimestampMixin` (provides `created_at`/`updated_at`).
- Write Pydantic schemas in `app/schemas/` before implementing business logic.
- Location code format: 区-排-层 (e.g., `A-12-03`).
- **Batch mutations must use the Draft-Apply two-step flow** — never apply a bulk change in a single step without operator confirmation.
- **Every stock mutation must write a `StockTransaction`** — never update `InventoryRecord.quantity` alone. `StockTransaction` is the source of truth for all history. Records are never modified or deleted (`ON DELETE RESTRICT` on all FKs).

## Project Structure

```text
app/
├── main.py                 # FastAPI app + StaticFiles mount + /app and /count-import routes
├── core/config.py          # Settings loaded from .env (Pydantic v2) incl. JWT + qinsi_warehouse_map
├── db/
│   ├── base.py             # SQLAlchemy DeclarativeBase + TimestampMixin
│   ├── session.py          # Async engine and session factory
│   └── init_db.py          # Auto-create tables on startup + ALTER TABLE migrations + admin user seed
├── models/
│   ├── product.py          # Products (JAN code as PK, name_jp/zh, units_per_case)
│   ├── user.py             # Users table (id, username, password_hash, is_active)
│   ├── inventory_record.py # Stock buckets keyed by (product_jan, warehouse_id)
│   ├── stock_transaction.py # Audit log (IN/OUT/ADJUST, source, user_id FK, transaction_date)
│   ├── warehouse.py        # Warehouses (+ allow_negative_stock flag)
│   ├── chat_report_draft.py
│   ├── rakuten_shipment_draft.py
│   └── inventory_count_draft.py  # Monthly count reconciliation drafts
├── schemas/
│   ├── inventory.py        # Core request/response DTOs + WarehouseStatusRead + ProductUpdate
│   └── inventory_count.py  # Count reconciliation DTOs
├── services/
│   ├── auth.py             # JWT encode/decode, bcrypt hash/verify, CurrentUser dataclass
│   ├── inventory.py        # Stock in/out/adjust (accept user_id, transaction_date), search, alerts
│   ├── chat_reports.py     # Gemini-powered chat parsing, draft apply
│   ├── rakuten_shipments.py # Rakuten CSV parsing + product reconciliation
│   └── inventory_count.py  # HTML/Excel parsing, reconciliation calc, draft apply
├── api/
│   ├── deps.py             # require_auth (JWT Bearer OR X-API-Key) → CurrentUser
│   └── v1/
│       ├── router.py
│       └── endpoints/
│           ├── auth.py            # POST /auth/login, POST /auth/users, GET /auth/me
│           ├── inventory.py       # GET /search, POST /stock-in/out/adjust, PATCH /products/{jan}
│           ├── warehouses.py      # CRUD + PATCH /{id}/allow-negative
│           ├── customers.py
│           ├── admin.py
│           ├── health.py
│           ├── status.py          # GET /status — data freshness per warehouse
│           ├── inventory_count.py # Upload/preview/export/apply count sheets
│           └── qinsi_scrape.py    # GET /auth-status, POST /upload-session /scrape /apply
├── static/
│   ├── app.html            # Main SPA — login, dashboard, all stock operations
│   └── count_import.html   # Legacy monthly count reconciliation page
├── bot/
│   ├── dispatcher.py       # Query-only: /search, /search_sku, /status, /whoami, /start
│   └── polling.py          # Async polling loop entry point
└── scrapers/
    └── qinsi_scraper.py    # httpx client for 秦丝生意通 API (no browser); session management
tools/                      # Standalone CLI scripts (run with python -m tools.*)
├── refresh_qinsi_session.py          # Run on Mac to renew 秦丝 cookies and upload to NAS API
├── consolidate_inventory_buckets.py  # One-time migration: merge multi-bucket records to (product, warehouse)
├── intercept_qinsi_api.py            # Debug tool: capture 秦丝 API calls via Playwright proxy
docs/
└── supply_chain_analytics.md  # Analytics gap analysis and dev roadmap for demand forecasting
```

## Operational Design Decisions

### Authentication

All mutation endpoints require authentication. The `require_auth` dependency in `app/api/deps.py` accepts **either**:

- `Authorization: Bearer <jwt>` — issued by `POST /api/v1/auth/login`, carries `user_id` and `username`
- `X-API-Key: <key>` — legacy header for CLI tools, maps to `CurrentUser(id=None, username="api_key")`

`CurrentUser` is a dataclass with `id: int | None` and `username: str`. When `id` is not None, it's stored on `StockTransaction.user_id` for audit tracking.

**Auto-create admin user on startup**: Set `ADMIN_USERNAME` + `ADMIN_PASSWORD` env vars; `init_db()` calls `_ensure_admin_user()` which creates the user if it doesn't exist.

**JWT config**: `JWT_SECRET_KEY` (env var, default `change-me-in-production`), 30-day expiry.

Read-only endpoints (search, status, count preview, negative-stock list) are unauthenticated.

### Inventory Record as Stock Bucket

`InventoryRecord` is effectively keyed by **`(product_jan, warehouse_id)`** — one record per product per warehouse.

The `UniqueConstraint` in the model still spans `(product_jan, warehouse_id, customer_id, location_code, expiration_date)` at the DB level, but `customer_id`, `location_code`, and `expiration_date` are always `NULL` / `"A-00-00"` / `NULL` on all new records. `_find_single_inventory_record` only filters by `(product_jan, warehouse_id)`.

**Customer is note-only**: customer information is stored in `StockTransaction.note` for reference; it does not affect which inventory bucket is selected. All customer UI elements in the frontend are hidden.

**Migration script**: If existing data has multiple buckets per `(product, warehouse)` (from the old schema), run:

```bash
docker compose exec api python -m tools.consolidate_inventory_buckets
```

This merges duplicate records, re-routes transactions, and normalises `location_code="A-00-00"`, `customer_id=NULL`.

All quantities are in individual units (not cases). Every change writes an immutable `StockTransaction`; the `source` field values are: `telegram` / `rakuten_csv` / `chat_report` / `physical_count` / `web_ui` / `qinsi_scrape` / `trade_shipment`.

Low-stock alert: `total_quantity < 2 * units_per_case` (only when `units_per_case` is set). `low_stock_alert_sent` flag prevents duplicates; resets automatically when stock recovers.

### 冷启动期负库存策略 (Cold-Start & Negative Stock)

**背景**: 公司每月底盘点，但统计结果可能到次月5日才完成。这段窗口期内进出库持续发生。

**已实现**:

- `Warehouse.allow_negative_stock: bool = False` 控制每个仓库的开关。
- Web UI **设置 → 仓库管理** 中每个仓库有「开启/关闭」按钮（调用 `PATCH /api/v1/warehouses/{id}/allow-negative?enabled=true`）。
- `stock_out_item` 中，当库存不足且该仓库开启了此标志时，**不抛出** `InsufficientStockError`，直接扣减至负值并写入 transaction。
- 当无现存库存桶时（`InventoryRecordNotFoundError`），且负库存开启，自动创建桶（`quantity=0`）再扣减。
- DB 层面**没有** `CHECK (quantity >= 0)` 约束（在 `init_db.py` 启动时通过 `DROP CONSTRAINT IF EXISTS` 移除）。
- 负库存 SKU 清单：仪表盘中点击「负库存 SKU」数字展开（调用 `GET /api/v1/inventory/negative-stock?warehouse_id=`）。
- 盘点数据到位后，通过盘点导入 web UI 用 `source="physical_count"` 的 ADJUST 事务将余额修正至实际值。

### 月度盘点对账工作流 (Physical Count Reconciliation)

**对账公式**:

```text
目标库存 = 盘点数量(5.31) + Σ(6.1起的所有WMS出入库变动)
ADJUST量 = 目标库存 - 当前WMS库存
```

操作步骤：

1. 上传文件（`.html` 来自秦丝生意通，或 `.xlsx` 通用格式）
2. 选择盘点日期（实物盘点当天，不是录入日期）+ 仓库
3. 系统解析文件，计算每个 SKU 的对账数据，生成草稿（`InventoryCountDraft`）
4. 预览表显示：JAN、商品名、盘点量、盘后WMS变动、目标库存、当前库存、ADJUST量
5. 可导出 Excel 留存
6. 确认导入 → 批量写 `source="physical_count"` 的 ADJUST 事务，`transaction_date` 设为盘点日期

**秦丝HTML解析细节**：

- 解析 `id="list5"` 的 `ui-jqgrid-btable` 表格（list4 是详情，list5 是摘要）
- 关键列索引：条码[7]、商品名称[3]、盘点数量[12]
- 条码字段可能含非数字前缀（如"店铺4573626631065"），用 `"".join(ch for ch in raw if ch.isdigit())` 剥离
- 同一JAN出现多次（秦丝数据问题）：合并数量，取首次出现的商品名

### 秦丝生意通 API 同步 (Qinsi ERP Integration)

**认证机制（关键）**:

- 秦丝登录需要阿里云滑块 CAPTCHA，只能在有图形界面的真实浏览器中完成。
- 登录成功后，`gisALogin` cookie 有效期 **7 天**。
- **NAS 部署续期流程**：在本地 Mac 运行 `tools/refresh_qinsi_session.py`，登录成功后将 cookies POST 到 NAS 的 `POST /api/v1/qinsi/upload-session` 接口。每 7 天操作一次，约 1 分钟。
- **简化运行**：在 `.env` 中配置 `NAS_API_URL` 和 `NAS_JWT_TOKEN`，直接运行 `./refresh_qinsi.sh`（已加入 `.gitignore`）。

**仓库自动映射**：`QINSI_WAREHOUSE_MAP` 环境变量（JSON 字符串）将秦丝仓库名映射到 WMS 仓库名。apply 时按每条记录的 `warehouse_name` 自动解析，无需手动选择仓库。

```env
QINSI_WAREHOUSE_MAP={"北津守仓库":"普通仓库","乐天仓库":"乐天仓库"}
```

**`transaction_date`**：apply 时自动使用秦丝订单的实际日期（`ScrapedRecord.record_date`），不是 WMS 录入时间。

**数据模型**：`ScrapedRecord` 中 `order_no` 为订单号（用于前端分组），`jan_code`/`product_name`/`quantity`/`warehouse_name`/`customer_name`/`record_date` 为单品级别字段。`customer_name` 对 IN 方向为供应商名，对 OUT 方向为客户名（仅展示，不写入库存桶定位）。幂等：`reference_id = "qinsi:{order_no}:{jan_code}"`，重复提交自动跳过。

**WMS API**:

- `GET /api/v1/qinsi/auth-status` — 检查 session 有效性（无需认证）
- `POST /api/v1/qinsi/upload-session` — 接收 Mac 端上传的 cookies（需认证）
- `POST /api/v1/qinsi/scrape` — 拉取指定日期范围的出入库记录（需认证）
- `POST /api/v1/qinsi/apply` — 将勾选记录写入 WMS；按每条 `warehouse_name` 自动匹配仓库（需认证）

### 状态与最后操作时间查询 (Last-Activity Status Query)

- `GET /api/v1/status`：按仓库聚合查询 `stock_transactions`，返回：
  - `last_stock_in_at`、`last_stock_out_at`：各仓库最后出入库录入时间
  - `last_csv_apply_at`：最后一次 Rakuten CSV 导入时间
  - `last_physical_count_at`：最后一次盘点时间
  - `data_gap_days`：数据滞后天数
  - `negative_stock_count`：当前负库存 SKU 数量（点击可查看明细）
- 实现在 `get_system_status()` service 函数中，单次 JOIN 聚合查询。

### Transaction Date（交易日期）

`StockTransaction.transaction_date DATE` — 实际业务发生日期，与 `created_at`（WMS 录入时间）分开存储。

| 来源 | `transaction_date` 填写逻辑 |
| --- | --- |
| 秦丝批量 | `ScrapedRecord.record_date`（秦丝订单实际日期） |
| 盘点 ADJUST | `document.count_date`（盘点当天） |
| 手动入/出/调整 | 前端可选日期选择器（留空为 NULL，查询时用 `created_at` 回退） |
| 乐天 CSV / 微信报库 | 暂为 NULL（待后续补充） |

这是时序分析和需求预测的核心轴。详见 `docs/supply_chain_analytics.md`。

## Concurrency Model

### 已实现的行级锁保护（单用户MVP阶段完整）

| 场景                 | 保护机制                                                   |
| -------------------- | ---------------------------------------------------------- |
| 同一库存桶并发出库   | `_find_single_inventory_record` 内 `SELECT FOR UPDATE`     |
| 入库并发创建重复桶   | `stock_in_item` 查询现有记录前 `SELECT FOR UPDATE`         |
| 同一草稿重复提交     | `get_*_draft(with_for_update=True)` 锁定草稿行             |
| 低库存标志竞争翻转   | `_maybe_create_low_stock_alert` 内 `Product` 行锁          |

### 多用户并发 — 规划方案（暂不实现，思路存档）

1. **Transfer死锁**: 始终按 `min(warehouse_id)` 规范顺序获取锁。
2. **Telegram消息重投**: `reference_id=f"tg:{message.message_id}"`，在 `(source, reference_id)` 上加DB唯一约束。
3. **连接池耗尽**: 在 `session.py` 设置 `pool_size=10, max_overflow=5`。
4. **全仓盘点期间的顾问锁**: 用 `pg_advisory_xact_lock(warehouse_id)` 防止并发干扰。

## Key Architectural Patterns

### Draft-Apply Pattern (Safety for Bulk Operations)

| 草稿模型 | 触发方式 | Apply 命令 |
| --- | --- | --- |
| `ChatReportDraft` | Web UI 粘贴聊天记录 | Web UI 确认按钮 |
| `RakutenShipmentDraft` | Web UI 上传 CSV | Web UI 确认按钮 |
| `InventoryCountDraft` | Web UI 上传文件 | Web UI 确认按钮 |

所有草稿模型有 `status` 字段（`"parsed"` → `"applied"`），apply 时用 `SELECT FOR UPDATE` 锁定草稿行防止重复提交。

**Ambiguity handling**: When a JAN search returns multiple candidates, return `ambiguous_product` error and stop — never guess.

### Product Search with Ranking

JAN codes support multiple formats: full 13-digit, last 6 digits, digits 7–11 (bundle packs), or last 5 digits. Search ranks by specificity. Names (JP and ZH) are also searchable.

### Telegram Bot (Query Only)

- `/start` — help text
- `/whoami` — show caller's Telegram user ID (no permission check)
- `/status` — warehouse data freshness (requires query permission)
- `/search <kw>` — inventory search (requires query permission)
- `/search_sku <kw>` — product master search (requires query permission)

**Permission tiers**: `TELEGRAM_QUERY_USER_IDS` / `TELEGRAM_OPERATOR_USER_IDS` / `TELEGRAM_ADMIN_USER_IDS` — all three have query access.

### Web UI Pattern

Static files mounted at `/static` via `StaticFiles(directory="app/static")` in `main.py`. Each UI page is a self-contained HTML file with inline CSS and vanilla JS (no CDN dependencies — works offline on NAS). JWT stored in `localStorage`.

Current UI pages:

- `GET /` and `GET /app` → `app/static/app.html` — main SPA
- `GET /count-import` → `app/static/count_import.html` — legacy monthly count reconciliation

**SPA design**: CSS variables for light/dark mode, system font stack, indigo accent (#6366f1 light / #818cf8 dark).

**Customer fields are hidden in the UI**: All `*-customer` selects have `style="display:none"`. Customer information is note-only and does not affect inventory bucket selection.

## Running the Project

### Start / Update Services

```bash
# First run or after code changes (always use --build after pulling new code)
docker compose up -d --build api

# Full rebuild (all services)
docker compose up --build
```

> `docker compose restart api` does NOT pick up code changes — the code is baked into the image at build time.

### Environment Setup

Copy `.env.example` to `.env` and fill in:

```env
POSTGRES_DB=wms
POSTGRES_USER=wms_user
POSTGRES_PASSWORD=your_password
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_QUERY_USER_IDS=your_telegram_id
GEMINI_API_KEY=your_key
API_KEY=your_api_key
JWT_SECRET_KEY=your_secret
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_password
NAS_API_URL=http://192.168.x.x:8000          # for refresh_qinsi.sh
NAS_JWT_TOKEN=eyJhbGci...                    # for refresh_qinsi.sh
QINSI_WAREHOUSE_MAP={"北津守仓库":"普通仓库","乐天仓库":"乐天仓库"}
```

### First-Time Data Import

```bash
# Import product catalog
docker compose exec api python -m app.tools.import_product_catalog --file "/app/imports/products.xlsx"

# Initialize inventory from count sheets
docker compose exec api python -m app.tools.init_inventory_from_count \
  --rakuten-file "/app/imports/4-30-rakuten.xlsx" \
  --normal-file "/app/imports/4-30-normal.xlsx" \
  --replace

# Consolidate inventory buckets (run once after upgrading from old multi-bucket schema)
docker compose exec api python -m tools.consolidate_inventory_buckets
```

## Adding New Features

### New API Endpoint

1. Add route file in `app/api/v1/endpoints/`, register in `app/api/v1/router.py`
2. Define Pydantic request/response models in `app/schemas/`
3. Delegate business logic to `app/services/`
4. Add `dependencies=[Depends(require_auth)]` to mutation endpoints

### New Database Model

1. Create ORM class in `app/models/` inheriting `Base` and `TimestampMixin`
2. Import it in `app/models/__init__.py` so `metadata.create_all()` picks it up
3. For new columns on existing tables, add `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` in `init_db.py`

## Important Configuration Notes

- **API Key**: Set `API_KEY` in `.env`. If not configured, mutations return 503.
- **Gemini Model**: Defaults to `gemini-2.5-flash`. Override via `GEMINI_MODEL` env var.
- **Schema Migrations**: Uses `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` in `init_db.py` on startup. Not suitable for column renames or drops.
- **Rakuten CSV Encoding**: Auto-detects `cp932`, `utf-8-sig`, `shift_jis`, `utf-8`. Product number format: `JAN[-SetCount]` × order quantity (`-0` treated as ×1).
- **Gemini Prompt Security**: `_build_chat_report_prompt` wraps user text in `<chat_log>` tags with an explicit guard instruction to prevent prompt injection.
- **Qinsi Warehouse Map**: `QINSI_WAREHOUSE_MAP` must be valid JSON. Missing entries cause per-record errors (reported in apply result), not a total failure.

## Data Analysis

For reporting, query from `stock_transactions` and join outward:

```text
stock_transactions → inventory_records → products → warehouses
```

Key fields for analytics:

| 字段 | 说明 |
| --- | --- |
| `transaction_date` | 实际业务日期（时序分析的主轴） |
| `created_at` | WMS 录入时间（`transaction_date` 为 NULL 时的回退） |
| `transaction_type` | IN / OUT / ADJUST |
| `quantity_change` | 变动量（OUT 为负） |
| `source` | 数据来源渠道 |
| `reference_id` | 秦丝：`qinsi:{order_no}:{jan_code}` |

`physical_count` ADJUST 事务的 `note` 格式：`盘点日期:YYYY-MM-DD 盘点量:N 盘后变动:±N`

详细分析规划见 `docs/supply_chain_analytics.md`。

## Supply Chain Domain Roadmap

以下待提升项暂不实现，设计新功能时需考虑其兼容性。

### transaction_date 补全（乐天 CSV / 微信报库）

Rakuten CSV 和微信报库的 `transaction_date` 目前为 NULL。Rakuten CSV 中有配送日期列，微信报库 AI 解析结果中有交易日期字段，后续在对应 apply 逻辑中补全写入。

### 渠道/供应商字段

秦丝销售单的客户名、采购单的供应商名目前仅展示于前端，未结构化存入 transaction。后续可新增 `channel VARCHAR(64)` 或 `supplier VARCHAR(64)` 列用于渠道分解分析。

### FEFO出库顺序（先到期先出）

`_find_single_inventory_record` 当前按 `id ASC` 选择。对有 `expiration_date` 的食品，改为 `expiration_date ASC NULLS LAST` 即可（单行改动，需在食品类商品全面录入后切换）。

### 月度损耗追踪

在盘点 apply 时自动计算 `理论余量 = 上次盘点余量 + Σ本期入库 - Σ本期出库`，将损耗写入 `note`。

### ABC速度分级

每月按 SKU 移动量排序，分 A/B/C 三级，存储在 `Product.velocity_class` 列。
