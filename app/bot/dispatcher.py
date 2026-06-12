from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message

from app.db.session import AsyncSessionLocal
from app.services.inventory import search_inventory_items, search_products


telegram_router = Router(name="telegram")


@telegram_router.message(Command("start"))
async def start(message: Message) -> None:
    await message.answer(
        "WMS 查询机器人\n\n"
        "查询命令（需要授权）：\n"
        "/search JAN或商品名 — 查库存\n"
        "/search_sku JAN或商品名 — 查商品字典\n"
        "/status — 各仓库数据状态\n"
        "/whoami — 查看你的 Telegram ID\n\n"
        "库存操作请访问 Web 管理界面。"
    )


@telegram_router.message(Command("whoami"))
async def whoami(message: Message) -> None:
    user = message.from_user
    if user is None:
        await message.answer("Cannot identify this Telegram user.")
        return
    await message.answer(
        f"user_id: {user.id}\n"
        f"username: @{user.username or '-'}\n"
        f"name: {user.full_name}"
    )


@telegram_router.message(Command("status"))
async def status(message: Message) -> None:
    if not await _require_query_permission(message):
        return
    async with AsyncSessionLocal() as session:
        from app.services.inventory import get_system_status
        rows = await get_system_status(session)
    if not rows:
        await message.answer("No warehouses found.")
        return
    lines = []
    for row in rows:
        neg_flag = " [负库存模式]" if row.allow_negative_stock else ""
        lines.append(f"📦 {row.warehouse_name}{neg_flag}")
        if row.last_stock_in_at:
            lines.append(f"  最后入库: {row.last_stock_in_at.strftime('%Y-%m-%d %H:%M')}")
        if row.last_stock_out_at:
            lines.append(f"  最后出库: {row.last_stock_out_at.strftime('%Y-%m-%d %H:%M')}")
        if row.last_csv_apply_at:
            lines.append(f"  最后CSV: {row.last_csv_apply_at.strftime('%Y-%m-%d %H:%M')}")
        if row.data_gap_days is not None:
            if row.data_gap_days == 0:
                lines.append("  数据延迟: 今天有录入")
            else:
                lines.append(f"  ⚠️ 数据延迟: {row.data_gap_days} 天")
        else:
            lines.append("  ⚠️ 尚无库存记录")
        if row.negative_stock_count > 0:
            lines.append(f"  🔴 负库存SKU: {row.negative_stock_count} 个")
    await _answer_long(message, "\n".join(lines))


@telegram_router.message(Command("search"))
async def search(message: Message) -> None:
    if not await _require_query_permission(message):
        return
    keyword = _command_args(message.text)
    if not keyword:
        await message.answer("用法: /search JAN或商品名")
        return
    await _do_search(message, keyword)


@telegram_router.message(lambda message: bool(message.text) and not message.text.startswith("/"))
async def default_search(message: Message) -> None:
    """未带任何指令的纯文本消息，默认按 /search 处理。"""
    if not await _require_query_permission(message):
        return
    keyword = (message.text or "").strip()
    if not keyword:
        return
    await _do_search(message, keyword)


async def _do_search(message: Message, keyword: str) -> None:
    async with AsyncSessionLocal() as session:
        items = await search_inventory_items(session=session, keyword=keyword, limit=10)
    if not items:
        await message.answer(f"未找到商品: {keyword}")
        return
    lines: list[str] = []
    for product in items:
        lines.append(f"{product.jan_code} | {product.name_jp} | {product.name_zh or '-'}")
        if not product.inventory_records:
            lines.append("  无库存记录")
            continue
        for record in product.inventory_records:
            customer = record.customer.name if record.customer else "-"
            lines.append(
                f"  {record.warehouse.name} | 数量: {record.quantity} | "
                f"库位: {record.location_code} | 客户: {customer}"
            )
    await _answer_long(message, "\n".join(lines))


@telegram_router.message(Command("search_sku", "search_SKU"))
async def search_sku(message: Message) -> None:
    if not await _require_query_permission(message):
        return
    keyword = _command_args(message.text)
    if not keyword:
        await message.answer("用法: /search_sku JAN或商品名")
        return
    async with AsyncSessionLocal() as session:
        products = await search_products(session=session, keyword=keyword, limit=10)
    if not products:
        await message.answer(f"未找到商品: {keyword}")
        return
    lines = []
    for p in products:
        case_text = f"{p.units_per_case}/箱" if p.units_per_case else "-"
        lines.append(f"{p.jan_code} | {p.name_jp} | {p.name_zh or '-'} | {case_text}")
    await message.answer("\n".join(lines))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _command_args(text: str | None) -> str:
    if not text:
        return ""
    parts = text.split(maxsplit=1)
    return parts[1].strip() if len(parts) > 1 else ""


async def _require_query_permission(message: Message) -> bool:
    from app.models.telegram_allowed_user import TelegramAllowedUser

    user = message.from_user
    if user is None:
        await message.answer("Cannot identify user.")
        return False
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        allowed = await session.scalar(
            select(TelegramAllowedUser).where(
                TelegramAllowedUser.telegram_user_id == user.id
            )
        )
    if allowed is None:
        await message.answer(
            "⛔ 无访问权限。\n"
            f"请联系管理员将你的 ID（{user.id}）添加到授权列表。"
        )
        return False
    return True


async def _answer_long(message: Message, text: str) -> None:
    MAX_LEN = 4000
    if len(text) <= MAX_LEN:
        await message.answer(text)
        return
    for i in range(0, len(text), MAX_LEN):
        await message.answer(text[i:i + MAX_LEN])


def create_dispatcher(bot: Bot) -> Dispatcher:
    dp = Dispatcher()
    dp.include_router(telegram_router)
    return dp
