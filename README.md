# WMS MVP

Telegram Bot を前端にした在庫検索・入出庫・AI 報庫整理システムです。

## 技术栈

- FastAPI
- PostgreSQL 16
- SQLAlchemy 2.0 async
- Telegram Bot polling
- Gemini API structured JSON parsing
- Docker Compose

## 启动

1. 准备 `.env`

```bash
cp .env.example .env
```

至少需要确认：

```env
POSTGRES_DB=wms
POSTGRES_USER=wms_user
POSTGRES_PASSWORD=your_password
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_OPERATOR_USER_IDS=your_telegram_user_id
TELEGRAM_ADMIN_USER_IDS=your_telegram_user_id
GEMINI_API_KEY=your_gemini_api_key
```

2. 启动服务

```bash
docker compose up --build
```

服务：

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Admin: `http://localhost:8000/api/v1/admin`
- Telegram bot: polling，不需要公网域名

PostgreSQL 数据保存在 Docker named volume `newproject_postgres_data` 中。`docker compose down` 不会删除数据，`docker compose down -v` 会删除数据。

## 4 月 30 日初始盘点表导入

你现在有两张无表头 Excel：

- 乐天仓库盘点表
- 普通仓库盘点表

格式要求：

- 第 1 列：JAN Code
- 第 2 列：数量
- 没有表头

导入规则：

| Excel | Warehouse | Customer | Location |
| --- | --- | --- | --- |
| 乐天仓库盘点表 | `乐天仓库` | `乐天` | `A-00-00` |
| 普通仓库盘点表 | `普通仓库` | `店铺` | `A-00-00` |

如果商品主数据里还没有对应 JAN，脚本会先创建一个占位商品：

- `jan_code`: Excel 第一列
- `name_jp`: 同 JAN
- `name_zh`: 空
- `units_per_case`: 空

后续可以再用 `/add_product` 或商品主数据导入补全商品名和箱入数。

### 推荐导入方式

先启动数据库：

```bash
docker compose up -d postgres
```

然后在本机 conda 环境运行。注意本机连接数据库要用 `localhost`，不是 Docker 内部的 `postgres`：

```bash
DATABASE_URL=postgresql+asyncpg://wms_user:your_password@localhost:5432/wms \
/Users/mac/anaconda3/bin/conda run -n wms-mvp python -m app.tools.init_inventory_from_count \
  --rakuten-file "/absolute/path/to/rakuten.xlsx" \
  --normal-file "/absolute/path/to/normal.xlsx" \
  --replace
```

`--replace` 表示用这次盘点数量覆盖这两个仓库/客户组合的现有库存。首次初始化建议使用。

如果你的文件就在项目根目录，例如：

```bash
DATABASE_URL=postgresql+asyncpg://wms_user:your_password@localhost:5432/wms \
/Users/mac/anaconda3/bin/conda run -n wms-mvp python -m app.tools.init_inventory_from_count \
  --rakuten-file "./4-30-rakuten.xlsx" \
  --normal-file "./4-30-normal.xlsx" \
  --replace
```

导入后可以通过 Telegram 查询：

```text
/search 123456
```

## Telegram 常用命令

查看自己的 Telegram user id：

```text
/whoami
```

查询：

```text
/search JAN_OR_NAME
```

只查商品字典，不看库存：

```text
/search_sku JAN_OR_NAME
```

`/search` 和 `/search_sku` 都支持完整 JAN、后六位、倒数第六到倒数第二位/后五位、日文名、中文名。

添加商品：

```text
/add_product JAN 商品名
/add_product JAN 商品名 箱入数
/add_product JAN 商品名 箱入数 中文名
```

没有箱入数的商品不会触发采购预警。

入库：

```text
/stock_in JAN 仓库名 数量
```

出库：

```text
/stock_out JAN 仓库名 数量
```

如果仓库名匹配 `乐天仓库`，省略客户时默认客户为 `乐天`；其它仓库默认客户为 `店铺`。

盘点修正：

```text
/stock_adjust JAN 仓库名 实际数量
```

仓库调拨：

```text
/transfer JAN 源仓库 目标仓库 数量
```

客户归属调拨：

```text
/transfer_customer JAN 仓库 源客户 目标客户 数量
```

乐天 RMS 出货 CSV：

```text
把文件 caption 写成：/rakuten_csv
或回复 CSV 文件：/rakuten_csv
```

单独发送 CSV 文件不会自动导入为乐天出库，避免以后其它文件功能误触发。

机器人会生成一个草稿 ID，并预览按 JAN 汇总后的出库数量。确认无误后执行：

```text
/apply_rakuten_csv DRAFT_ID
```

如果预览里有 `product_not_found`、`inventory_record_not_found` 或 `insufficient_stock`，默认不会出库。确认这些问题行后续手动处理时，可以只应用正常行并跳过问题行：

```text
/apply_rakuten_csv DRAFT_ID ignore
```

默认从 `乐天仓库` 的 `乐天` 客户库存扣减。如果需要临时指定：

```text
/rakuten_csv 仓库名 客户名
```

## AI 报库导入

先解析并保存 draft：

```text
/parse_report 普通仓库 店铺
粘贴多条聊天记录
```

确认 draft：

```text
/show_report DRAFT_ID
```

应用 draft：

```text
/apply_report DRAFT_ID
```

修改 draft：

```text
/set_report_meta DRAFT_ID IN|OUT 仓库 客户
/set_report_line DRAFT_ID 行号 JAN 数量 商品名
/add_report_line DRAFT_ID JAN 数量 商品名
/del_report_line DRAFT_ID 行号
```

## 乐天 RMS 出货 CSV 导入

RMS 下载的出货 CSV 可以直接导入为乐天出库。

日常使用建议走 Telegram：把 CSV 文件发给机器人，确认预览后 `/apply_rakuten_csv DRAFT_ID`。

默认规则：

- 仓库：`乐天仓库`
- 客户：`乐天`
- source：`rakuten_csv`
- `商品番号` 解析规则沿用旧快递单脚本：
  - `JAN-套数` 乘以 `個数`
  - `JAN` 没有 `-` 时套数按 1
  - `-0` 按 1 处理

先预览解析结果，不更新数据库：

```bash
python -m app.tools.import_rakuten_shipment_csv \
  --file "/path/to/rakuten.csv" \
  --preview
```

在 Docker 容器里执行：

```bash
docker compose exec api python -m app.tools.import_rakuten_shipment_csv \
  --file "/app/imports/rakuten_20260511.csv" \
  --preview
```

确认无误后正式出库：

```bash
docker compose exec api python -m app.tools.import_rakuten_shipment_csv \
  --file "/app/imports/rakuten_20260511.csv"
```

也可以通过 API 上传：

```text
POST /api/v1/inventory/imports/rakuten-shipment
```

这个接口会自动尝试 `cp932`、`utf-8-sig`、`shift_jis`、`utf-8` 解码。

## 库存预警

商品有 `units_per_case` 时，出库后如果总库存少于 2 箱，会给 Telegram 操作者发送采购提醒。

为了避免重复提醒，商品有 `low_stock_alert_sent` 标记。库存重新回到 2 箱以上后，提醒状态会自动解除。

## 数据分析思路

后续做客户、仓库、商品分析时，建议从 `stock_transactions` 出发：

```text
stock_transactions
  -> inventory_records
  -> products
  -> warehouses
  -> customers
```

可以分析：

- 某客户入库/出库趋势
- 某仓库库存分布
- 某商品流转
- Telegram / AI 报库 / CSV 等不同 source 的来源占比
- 采购预警商品列表

## 注意事项

当前 MVP 启动时会自动创建表，并对部分新增列做轻量 `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`。正式生产环境建议切换到 Alembic migration。
