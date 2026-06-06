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
├── core/config.py          # Settings loaded from .env (Pydantic v2) incl. JWT config
├── db/
│   ├── base.py             # SQLAlchemy DeclarativeBase + TimestampMixin
│   ├── session.py          # Async engine and session factory
│   └── init_db.py          # Auto-create tables on startup + ALTER TABLE migrations + admin user seed
├── models/
│   ├── product.py          # Products (JAN code as PK, name_jp/zh, units_per_case)
│   ├── user.py             # Users table (id, username, password_hash, is_active)
│   ├── inventory_record.py # Stock buckets (warehouse/customer/location/expiration)
│   ├── stock_transaction.py # Audit log (IN/OUT/ADJUST, source, user_id FK)
│   ├── warehouse.py        # Warehouses (+ allow_negative_stock flag)
│   ├── chat_report_draft.py
│   ├── rakuten_shipment_draft.py
│   └── inventory_count_draft.py  # Monthly count reconciliation drafts
├── schemas/
│   ├── inventory.py        # Core request/response DTOs + WarehouseStatusRead
│   └── inventory_count.py  # Count reconciliation DTOs
├── services/
│   ├── auth.py             # JWT encode/decode, bcrypt hash/verify, CurrentUser dataclass
│   ├── inventory.py        # Stock in/out/adjust (accept user_id), search, low-stock alerts
│   ├── chat_reports.py     # Gemini-powered chat parsing, draft apply
│   ├── rakuten_shipments.py # Rakuten CSV parsing + product reconciliation
│   └── inventory_count.py  # HTML/Excel parsing, reconciliation calc, draft apply
├── api/
│   ├── deps.py             # require_auth (JWT Bearer OR X-API-Key) → CurrentUser
│   └── v1/
│       ├── router.py
│       └── endpoints/
│           ├── auth.py            # POST /auth/login, POST /auth/users, GET /auth/me
│           ├── inventory.py       # GET /search, POST /stock-in/out/adjust, imports
│           ├── warehouses.py      # CRUD + PATCH /{id}/allow-negative
│           ├── customers.py
│           ├── admin.py
│           ├── health.py
│           ├── status.py          # GET /status — data freshness per warehouse
│           └── inventory_count.py # Upload/preview/export/apply count sheets
├── static/
│   ├── app.html            # Main SPA — login, dashboard, all stock operations
│   └── count_import.html   # Legacy monthly count reconciliation page
└── bot/
    ├── dispatcher.py       # Query-only: /search, /search_sku, /status, /whoami, /start
    └── polling.py          # Async polling loop entry point
├── scrapers/
│   └── qinsi_scraper.py    # httpx client for 秦丝生意通 API (no browser); session management
tools/                      # Standalone CLI scripts (run with python -m tools.*)
├── refresh_qinsi_session.py       # Run on Mac to renew 秦丝 cookies and upload to NAS API
├── intercept_qinsi_api.py         # Debug tool: capture 秦丝 API calls via Playwright proxy
├── init_inventory_from_count.py
├── import_product_catalog.py
├── import_rakuten_shipment_csv.py
└── convert_rakuten_csv_encoding.py
```

## Operational Design Decisions

### Authentication

All mutation endpoints require authentication. The `require_auth` dependency in `app/api/deps.py` accepts **either**:

- `Authorization: Bearer <jwt>` — issued by `POST /api/v1/auth/login`, carries `user_id` and `username`
- `X-API-Key: <key>` — legacy header for CLI tools, maps to `CurrentUser(id=None, username="api_key")`

`CurrentUser` is a dataclass with `id: int | None` and `username: str`. When `id` is not None, it's stored on `StockTransaction.user_id` for audit tracking.

**Auto-create admin user on startup**: Set `ADMIN_USERNAME` + `ADMIN_PASSWORD` env vars; `init_db()` calls `_ensure_admin_user()` which creates the user if it doesn't exist.

**JWT config**: `JWT_SECRET_KEY` (env var, default `change-me-in-production`), 30-day expiry.

Read-only endpoints (search, status, count preview) are unauthenticated.

Generate an API key (for tool scripts): `python -c "import secrets; print(secrets.token_hex(32))"`

### 冷启动期负库存策略 (Cold-Start & Negative Stock)

**背景**: 公司每月底盘点，但统计结果可能到次月5日才完成。这段窗口期内进出库持续发生。如果强制要求库存非负，操作就会卡死。

**已实现**:

- `Warehouse.allow_negative_stock: bool = False` 列控制每个仓库的开关。
- `stock_out_item` 中，当 `record.quantity < payload.quantity` 且该仓库开启了此标志时，**不抛出** `InsufficientStockError`，直接扣减至负值并写入 transaction。负库存是合法业务数据，代表"已记录但开期余额未知的出库"。
- 盘点数据到位后，通过盘点导入 web UI 用 `source="physical_count"` 的 ADJUST 事务将余额修正至实际值。
- Telegram 管理员命令 `/allow_negative WAREHOUSE_NAME on|off` 控制开关。
- API: `PATCH /api/v1/warehouses/{id}/allow-negative?enabled=true`。
- `_maybe_create_low_stock_alert` 正确处理 `quantity < 0`：仅在余额首次过阈值时触发一次告警（`low_stock_alert_sent` 标志防止重复）。

### 月度盘点对账工作流 (Physical Count Reconciliation)

**背景**: 盘点在月底（如5月31日）进行，但汇总数据到次月5日才出来。这段期间继续有出入库记录。不能直接用盘点数量覆盖当前库存。

**对账公式**:

```text
目标库存 = 盘点数量(5.31) + Σ(6.1起的所有WMS出入库变动)
ADJUST量 = 目标库存 - 当前WMS库存
```

**已实现** — 网页操作入口：`http://NAS-IP:8000/count-import`

操作步骤：

1. 上传文件（`.html` 来自秦丝生意通，或 `.xlsx` 通用格式）
2. 选择盘点日期（实物盘点当天，不是录入日期）+ 仓库 + 客户
3. 系统解析文件，计算每个 SKU 的对账数据，生成草稿（`InventoryCountDraft`）
4. 预览表显示：JAN、商品名、盘点量、盘后WMS变动、目标库存、当前库存、ADJUST量
5. 可导出 Excel 留存
6. 确认导入 → 批量写 `source="physical_count"` 的 ADJUST 事务

**秦丝HTML解析细节**：

- 解析 `id="list5"` 的 `ui-jqgrid-btable` 表格（list4 是详情，list5 是摘要）
- 关键列索引：条码[7]、商品名称[3]、盘点数量[12]
- 条码字段可能含非数字前缀（如"店铺4573626631065"），用 `"".join(ch for ch in raw if ch.isdigit())` 剥离
- 同一JAN出现多次（秦丝数据问题）：合并数量，取首次出现的商品名

### 秦丝生意通 API 同步 (Qinsi ERP Integration)

**背景**: 秦丝生意通是公司的 ERP 系统，记录采购单（入库）和销售单（出库）。WMS 通过直接调用秦丝后端 API 来同步这些记录，作为微信报库解析的补充来源。

**认证机制（关键）**:

- 秦丝登录需要阿里云滑块 CAPTCHA，只能在有图形界面的真实浏览器中完成。Playwright 自动化环境下 CAPTCHA 始终失败。
- 登录成功后，`gisALogin` cookie 有效期 **7 天**，可单独用于所有 API 调用（服务端自动续期 JSESSIONID）。
- **NAS 部署续期流程**：在本地 Mac 运行 `tools/refresh_qinsi_session.py`，Playwright 在 Mac 上打开浏览器完成滑块验证，登录成功后将 cookies POST 到 NAS 的 `POST /api/v1/qinsi/upload-session` 接口保存。每 7 天操作一次，约 1 分钟。

```bash
# Mac 上运行（不是 NAS），替换为实际 NAS 地址和 JWT
conda run -n wms-mvp python -m tools.refresh_qinsi_session \
  --api http://NAS-IP:8000 \
  --token YOUR_JWT_TOKEN
```

**Session 文件**: `app/data/qinsi_session.json`（Playwright cookie 列表格式，在 Docker volume 内持久化）。

**已发现的关键 API 端点**（Base: `https://web.syt.qinsilk.com/gis/admin`）:

| 用途 | 端点 |
| --- | --- |
| 验证 session | `GET /pubuser/getUserInfo.ac` → `statusCode == 1` |
| 销售单列表（出库） | `GET /inner/sale/wholesaleOrdersListJSON.ac` |
| 销售单商品明细 | `POST /inner/sale/wholesaleOrdersGet.ac?ordersSn=<sn>` → `orderGoods[]` |
| 采购单列表（入库） | `GET /inner/orders/purchase/purchaseListJSON.ac` |
| 采购单商品明细 | `POST /inner/orders/purchase/purchaseGet.ac?purchaseSn=<sn>` → `orderGoods[]` |

**数量字段**：`orderGoods[].quantity`（不是 `number`）。验证：`quantity * price = trueAmount`。`number` 是下单时的仓库可用量快照，不用于计算。

**StockTransaction.source**: `"qinsi_scrape"`

**WMS API**:

- `GET /api/v1/qinsi/auth-status` — 检查 session 有效性（无需认证）
- `POST /api/v1/qinsi/upload-session` — 接收 Mac 端上传的 cookies（需认证）
- `POST /api/v1/qinsi/scrape` — 拉取指定日期范围的出入库记录（需认证）
- `POST /api/v1/qinsi/apply` — 将勾选记录写入 WMS（需认证）

### 状态与最后操作时间查询 (Last-Activity Status Query)

**背景**: 忙碌期间数据录入会延迟数天。操作员无法判断系统数据是否与实际情况同步。乐天仓库（由Rakuten CSV驱动）和普通仓库（由微信报库驱动）的数据新鲜度完全独立，必须分开显示。

**已实现**:

- `GET /api/v1/status`：按仓库聚合查询 `stock_transactions`，返回：
  - `last_stock_in_at`、`last_stock_out_at`：各仓库最后出入库时间
  - `last_csv_apply_at`：最后一次 Rakuten CSV 导入时间
  - `data_gap_days`：距今天的数据滞后天数
  - `negative_stock_count`：当前负库存 SKU 数量
- Telegram `/status` 命令（查询级权限）：输出相同信息，格式化为聊天消息。
- 实现在 `get_system_status()` service 函数中，单次 JOIN 聚合查询，无额外追踪表。

## Concurrency Model

### 已实现的行级锁保护（单用户MVP阶段完整）

| 场景                 | 保护机制                                                   |
| -------------------- | ---------------------------------------------------------- |
| 同一库存桶并发出库   | `_find_single_inventory_record` 内 `SELECT FOR UPDATE`     |
| 入库并发创建重复桶   | `stock_in_item` 查询现有记录前 `SELECT FOR UPDATE`         |
| 同一草稿重复提交     | `get_*_draft(with_for_update=True)` 锁定草稿行             |
| 低库存标志竞争翻转   | `_maybe_create_low_stock_alert` 内 `Product` 行锁          |

### 多用户并发 — 规划方案（暂不实现，思路存档）

1. **Transfer死锁**: 用户A做A→B调拨，用户B同时做B→A。修复：始终按 `min(warehouse_id)` 规范顺序获取锁。

2. **Telegram消息重投**: 写入 `reference_id=f"tg:{message.message_id}"`，在 `(source, reference_id)` 上加DB唯一约束实现幂等。

3. **连接池耗尽**: 在 `session.py` 设置 `pool_size=10, max_overflow=5`，根据实测并发量调整。

4. **全仓盘点期间的顾问锁**: 执行全量ADJUST时，用 `pg_advisory_xact_lock(warehouse_id)` 防止并发出入库干扰。

5. **Draft长时间搁置**: 考虑在 apply 入口增加 re-validation，若草稿超龄则重新校验而非直接应用。

## Key Architectural Patterns

### Draft-Apply Pattern (Safety for Bulk Operations)

三类批量操作都使用两阶段工作流：

| 草稿模型 | 触发方式 | Apply 命令 |
| --- | --- | --- |
| `ChatReportDraft` | Telegram `/parse_report` | `/apply_report DRAFT_ID` |
| `RakutenShipmentDraft` | Telegram 发送CSV文件 | `/apply_rakuten_csv DRAFT_ID` |
| `InventoryCountDraft` | Web UI 上传文件 | Web UI 确认按钮 |

所有草稿模型有 `status` 字段（`"parsed"` → `"applied"`），apply 时用 `SELECT FOR UPDATE` 锁定草稿行防止重复提交。

**Ambiguity handling**: When a JAN search returns multiple candidates, return `ambiguous_product` error and stop — never guess. The operator must supply a more specific identifier and retry.

### Inventory Record as Stock Bucket

`InventoryRecord` 由复合键唯一标识：

```text
(product_jan, warehouse_id, customer_id, location_code, expiration_date)
```

`customer_id` 可为 NULL。过滤时注意：`customer_id IS NULL` 不能用 `==`，需用 `.is_(None)`（否则 SQL 生成 `= NULL` 永远不匹配）。

所有数量为单品级别（不是箱数）。每次变动写入不可变的 `StockTransaction`，`source` 字段可选值：`telegram` / `rakuten_csv` / `chat_report` / `physical_count`。

低库存告警：`total_quantity < 2 * units_per_case`（仅 `units_per_case` 已设置时）。`low_stock_alert_sent` 标志防止重复，股票恢复时自动重置。

### Product Search with Ranking

JAN codes support multiple formats: full 13-digit, last 6 digits, digits 7–11 (bundle packs), or last 5 digits. Search ranks by specificity. Names (JP and ZH) are also searchable.

### Telegram Bot (Query Only)

The bot handles **read-only** commands. All mutations moved to the web UI. Permitted commands:

- `/start` — help text
- `/whoami` — show caller's Telegram user ID (no permission check)
- `/status` — warehouse data freshness (requires query permission)
- `/search <kw>` — inventory search (requires query permission)
- `/search_sku <kw>` — product master search (requires query permission)

**Permission tiers** (defined in env vars, all checked by `_require_query_permission`):

- `TELEGRAM_QUERY_USER_IDS`: query-only access
- `TELEGRAM_OPERATOR_USER_IDS`: same as query (mutation commands removed)
- `TELEGRAM_ADMIN_USER_IDS`: same as query (mutation commands removed)

### Web UI Pattern

Static files mounted at `/static` via `StaticFiles(directory="app/static")` in `main.py`. Each UI page is a self-contained HTML file with inline CSS and vanilla JS (no CDN dependencies — works offline on NAS). The JS calls the REST API directly using `fetch()` with `Authorization: Bearer <jwt>` header stored in `localStorage`.

Current UI pages:

- `GET /` and `GET /app` → `app/static/app.html` — main SPA (login, dashboard, all stock ops, imports, settings)
- `GET /count-import` → `app/static/count_import.html` — legacy monthly count reconciliation

**SPA design**: CSS variables for light/dark mode, system font stack, indigo accent (#6366f1 light / #818cf8 dark). Login screen → sidebar nav → section panels. Stores JWT in `localStorage`. On load, validates token via `GET /auth/me` before showing app shell.

## Running the Project

### Start All Services

```bash
docker compose up --build
```

- API + Web UI: <http://localhost:8000> (Swagger at `/docs`)
- 盘点导入页面: <http://localhost:8000/count-import>
- Telegram bot: polling (connects automatically)
- Data persists in Docker named volume `newproject_postgres_data`
  - `docker compose down` preserves data; `docker compose down -v` deletes it

### Environment Setup

Copy `.env.example` to `.env` and fill in:

```env
POSTGRES_DB=wms
POSTGRES_USER=wms_user
POSTGRES_PASSWORD=your_password
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_OPERATOR_USER_IDS=your_telegram_id
TELEGRAM_ADMIN_USER_IDS=your_telegram_id
GEMINI_API_KEY=your_key
API_KEY=your_api_key          # legacy X-API-Key for CLI tools
JWT_SECRET_KEY=your_secret    # generate: python -c "import secrets; print(secrets.token_hex(32))"
ADMIN_USERNAME=admin          # auto-created on first startup
ADMIN_PASSWORD=your_password  # must set before first run
```

### First-Time Data Import

Run against a started postgres (from project root, using local conda env):

```bash
# 1. Import product catalog
DATABASE_URL=postgresql+asyncpg://wms_user:your_password@localhost:5432/wms \
/Users/mac/anaconda3/bin/conda run -n wms-mvp \
python -m app.tools.import_product_catalog --file "./商品箱规数据5.12.xlsx"

# 2. Initialize inventory from count sheets (--replace overwrites existing)
DATABASE_URL=postgresql+asyncpg://wms_user:your_password@localhost:5432/wms \
/Users/mac/anaconda3/bin/conda run -n wms-mvp \
python -m app.tools.init_inventory_from_count \
  --rakuten-file "./4-30-rakuten.xlsx" \
  --normal-file "./4-30-normal.xlsx" \
  --replace
```

Or inside the Docker container:

```bash
docker compose exec api python -m app.tools.import_product_catalog --file "/app/imports/products.xlsx"
```

## Adding New Features

### New Telegram Command (query only)

1. Add `@telegram_router.message(Command("command_name"))` handler in `app/bot/dispatcher.py`
2. Call read-only service functions (search, status)
3. Use `await _require_query_permission(message)` for access control — bot no longer supports mutations

### New API Endpoint

1. Add route file in `app/api/v1/endpoints/`, register in `app/api/v1/router.py`
2. Define Pydantic request/response models in `app/schemas/`
3. Delegate business logic to `app/services/`
4. Add `dependencies=[Depends(require_api_key)]` to mutation endpoints

### New Web UI Page

1. Create self-contained HTML in `app/static/` (inline CSS + vanilla JS, no CDN)
2. Add `GET /your-page` route in `main.py` returning `FileResponse`
3. JS calls `/api/v1/...` with `X-API-Key` from `localStorage`

### New Database Model

1. Create ORM class in `app/models/` inheriting `Base` and `TimestampMixin`
2. Import it in `app/models/__init__.py` so `metadata.create_all()` picks it up
3. For new columns on existing tables, add `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` in `init_db.py`

## Important Configuration Notes

- **API Key**: Required for all mutation endpoints. Set `API_KEY` in `.env`. If not configured, mutations return 503.
- **Telegram Bot Mode**: `TELEGRAM_BOT_MODE=local_polling` for development. Switch to `webhook` for production.
- **Gemini Model**: Defaults to `gemini-2.5-flash`. Override via `GEMINI_MODEL` env var.
- **Schema Migrations**: Uses `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` in `init_db.py` on startup. Not suitable for column renames or drops.
- **Rakuten CSV Encoding**: Auto-detects `cp932`, `utf-8-sig`, `shift_jis`, `utf-8`. Product number format: `JAN[-SetCount]` × order quantity (`-0` treated as ×1).
- **Default Warehouse/Customer**: `普通仓库`/`店铺` for normal ops; `乐天仓库`/`乐天` for Rakuten CSV imports.
- **Gemini Prompt Security**: `_build_chat_report_prompt` wraps user text in `<chat_log>` tags with an explicit guard instruction to prevent prompt injection.

## Data Analysis

For reporting, query from `stock_transactions` and join outward:

```text
stock_transactions → inventory_records → products → warehouses → customers
```

Key `source` values: `telegram` / `rakuten_csv` / `chat_report` / `physical_count`

`physical_count` ADJUST transactions have `note` format: `盘点日期:YYYY-MM-DD 盘点量:N 盘后变动:±N`

## Supply Chain Domain Roadmap

以下待提升项暂不实现，设计新功能时需考虑其兼容性。

### FEFO出库顺序（先到期先出）

`_resolve_first_inventory_record` 当前按 `id ASC`（录入顺序）选择库存桶。对于有 `expiration_date` 的食品，改为 `expiration_date ASC NULLS LAST` 即可。这是单行改动，但有食品安全合规含义，需在食品类商品全面录入后切换。

### 负库存与零库存告警扩展

- **零库存/负库存告警**: `/stockout_report` 命令列出余量 ≤ 0 的所有SKU，分仓库展示。
- **过剩库存告警**: `total_quantity > N * units_per_case`（N可配置）时提醒，防止资金占用。

### 月度损耗追踪（盘点对账升级）

现有盘点导入已写入 `source="physical_count"` 的 ADJUST 事务。下一步：在 apply 时自动计算并写入损耗统计：

```text
理论余量 = 上次盘点余量 + Σ本期入库 - Σ本期出库
损耗 = 盘点数量 - 理论余量（负值=盗损/损耗，正值=入库漏录）
```

将差异写入 `note` 字段，并提供 `/shrinkage_report YYYY-MM` 命令输出。

### 乐天订单与出库对账

Rakuten CSV 记录"已配送数量"。若接入乐天RMS订单feed，可对比订单量 vs 实际出库量（发现少发/漏发）。需新增 `RakutenOrder` 模型和对账服务。

### ABC速度分级

每月按SKU移动量排序，分A（前20%）、B、C三级，存储在 `Product.velocity_class` 列。A类商品分配近码头库位、优先循环盘点、低库存阈值更高。
