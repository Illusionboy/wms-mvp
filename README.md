# WMS MVP

仓库管理系统 — Web UI 为主操作界面，Telegram Bot 为查询伴侣。NAS / Docker 自托管。

## 技术栈

- FastAPI + PostgreSQL 16 + SQLAlchemy 2.0 async
- JWT 认证 (PyJWT 2.9.0, HS256) + bcrypt (passlib 1.7.4)
- Telegram Bot (aiogram 3, polling) — 仅查询
- Gemini API (gemini-2.5-flash) — 微信报库 AI 解析
- BeautifulSoup4 + lxml — 秦丝生意通 HTML 盘点单解析
- openpyxl — Excel 读写
- Docker Compose

## 快速启动

### 1. 准备 `.env`

```bash
cp .env.example .env
```

必填项：

```env
POSTGRES_DB=wms
POSTGRES_USER=wms_user
POSTGRES_PASSWORD=your_password
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_QUERY_USER_IDS=your_telegram_user_id
GEMINI_API_KEY=your_gemini_api_key
JWT_SECRET_KEY=your_jwt_secret         # 生成：python -c "import secrets; print(secrets.token_hex(32))"
ADMIN_USERNAME=admin                    # 首次启动自动创建此账号
ADMIN_PASSWORD=your_admin_password
API_KEY=your_api_key                    # 仅 CLI 工具脚本需要
```

### 2. 启动服务

```bash
docker compose up --build
```

服务地址：

- **主 Web UI**: <http://localhost:8000/app> （或直接访问 <http://localhost:8000>）
- **API Swagger**: <http://localhost:8000/docs>
- **盘点导入**: <http://localhost:8000/count-import>
- **Telegram Bot**: 自动 polling，不需要公网域名

PostgreSQL 数据保存在 Docker named volume `newproject_postgres_data`。`docker compose down` 保留数据，`docker compose down -v` 删除数据。

## 首次登录

首次启动后，用 `ADMIN_USERNAME` / `ADMIN_PASSWORD` 登录 Web UI。初始管理员账号由 `init_db()` 自动创建。

如需添加其他用户：登录后进入 **设置 → 添加用户**，或调用 `POST /api/v1/auth/users`。

## 首次数据导入

先启动数据库：

```bash
docker compose up -d postgres
```

### 商品字典导入

#### 方式一：Web UI（推荐）

登录后进入 **商品管理** → 上传 Excel 文件。

#### 方式二：API

```bash
curl -X POST http://localhost:8000/api/v1/inventory/imports/product-catalog \
  -H "Authorization: Bearer <your_jwt>" \
  -F "file=@商品箱规数据.xlsx"
```

#### 方式三：命令行工具

```bash
DATABASE_URL=postgresql+asyncpg://wms_user:your_password@localhost:5432/wms \
python -m app.tools.import_product_catalog --file "./商品箱规数据.xlsx"
```

表头需含 `JAN`（或 `条码`）、`商品名`（或 `日文`），可选 `中文`、`箱入れ数`。

### 初始盘点库存导入

```bash
DATABASE_URL=postgresql+asyncpg://wms_user:your_password@localhost:5432/wms \
python -m app.tools.init_inventory_from_count \
  --rakuten-file "./4-30-rakuten.xlsx" \
  --normal-file "./4-30-normal.xlsx" \
  --replace
```

`--replace` 覆盖现有库存。两张表无表头，第 1 列 JAN，第 2 列数量。

## Web UI 功能

| 功能 | 说明 |
| ------ | ------ |
| 仪表盘 | 各仓库最后入/出库时间、最后盘点时间、数据延迟天数、负库存 SKU 数 |
| 入库 | 搜索商品 → 选仓库/客户/库位 → 提交 |
| 出库 | 搜索商品 → 选仓库/客户 → 提交 |
| 调整 | 设定库存实际数量，写入 ADJUST 事务 |
| 查询 | 按 JAN/商品名搜索库存 |
| 微信报库 | 粘贴聊天记录 → AI 解析草稿 → 预览 → 确认导入 |
| 乐天 CSV | 上传 RMS 出货 CSV → 直接写入出库记录 |
| 盘点导入 | 上传秦丝 HTML 或 Excel → 对账预览 → 确认应用 |
| 商品管理 | 上传商品字典 Excel，搜索商品主数据 |
| 设置 | 添加用户、新增仓库/客户 |

## Telegram Bot（查询）

Bot 仅支持读操作：

```text
/whoami          — 查看自己的 Telegram user id（无需权限）
/status          — 各仓库数据状态（需授权）
/search <关键词>  — 搜索库存（JAN/商品名）
/search_sku <关键词> — 搜索商品字典
```

权限通过 `TELEGRAM_QUERY_USER_IDS` / `TELEGRAM_OPERATOR_USER_IDS` / `TELEGRAM_ADMIN_USER_IDS` 控制（三级均有查询权限）。

## 秦丝生意通同步

### 工作原理

WMS 通过 httpx 直接调用秦丝生意通后端 API（无浏览器），拉取采购单（入库）和销售单（出库）的商品明细，写入 WMS 事务（`source="qinsi_scrape"`）。

认证使用秦丝的 `gisALogin` session cookie，**有效期 7 天**。

### 首次授权（初始化 / 每 7 天续期）

秦丝登录需要阿里云滑块验证码，只能在有图形界面的 Mac 上完成。登录成功后 cookies 自动上传到 NAS。

**第一步（一次性配置）**：在 `.env` 中填写：

```env
NAS_API_URL=http://192.168.x.x:8000      # NAS 的 IP 和端口
NAS_JWT_TOKEN=eyJhbGci...                # WMS 登录后从浏览器 localStorage 获取
```

JWT token 获取方式：打开 WMS 网页 → F12 → Console → `localStorage.getItem('token')`

**之后每次续期**（Mac 上运行，不是 NAS）：

```bash
./refresh_qinsi.sh
```

脚本自动读取 `.env` 中的地址和 token，打开 Chromium 窗口，完成滑块验证后自动上传到 NAS。

流程：① 自动填写账号密码 → ② 手动完成滑块 → ③ cookies 自动 POST 到 NAS → ④ 立即生效

**本地开发（API 在本机）**：直接运行 `./refresh_qinsi.sh`，`NAS_API_URL` 留空或填 `http://localhost:8000` 时直接写入本地文件，无需 token。

### 检查授权状态

```bash
curl http://localhost:8000/api/v1/qinsi/auth-status
```

### 使用同步功能

登录 Web UI → **秦丝同步** 标签：选择日期范围 → 抓取 → 按订单勾选（点「展开」查看商品明细）→ 确认写入。

## 月度盘点对账

访问 <http://localhost:8000/count-import> 或 Web UI **盘点导入** 标签：

1. 上传秦丝生意通 `.html` 或 `.xlsx` 盘点单
1. 选择盘点日期（实物盘点当天）、仓库、客户
1. 系统计算对账量：`目标库存 = 盘点数量 + Σ(盘点日期之后的WMS入出库变动)`；`ADJUST量 = 目标库存 - 当前WMS库存`
1. 预览表格（可按"有差异"筛选），可导出 Excel 留存
1. 确认应用 → 写入 `source="physical_count"` 的 ADJUST 事务

## 负库存模式

月底盘点数据到次月 5 日才到，这段窗口期出入库不能停。管理员可按仓库开启负库存：

- Web UI：**设置 → 仓库管理**
- API：`PATCH /api/v1/warehouses/{id}/allow-negative?enabled=true`

开启后出库可超过当前库存量，余额变为负值（合法业务数据）。盘点数据到位后用盘点导入修正。

## API 认证

所有变库存端点需要认证头：

- `Authorization: Bearer <jwt>` — 通过 `POST /api/v1/auth/login` 获取
- `X-API-Key: <key>` — 兼容 CLI 工具脚本

查询端点（search、status、count preview）无需认证。

## 数据分析

从 `stock_transactions` 出发，关联 `inventory_records → products → warehouses → customers`。

`source` 值：`telegram` / `rakuten_csv` / `chat_report` / `physical_count` / `web_ui`

`physical_count` 事务的 `note` 格式：`盘点日期:YYYY-MM-DD 盘点量:N 盘后变动:±N`

`stock_transactions.user_id` 关联 `users.id`，可追踪每笔操作的操作员。
