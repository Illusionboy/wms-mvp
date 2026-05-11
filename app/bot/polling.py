import asyncio
import logging

from app.bot.dispatcher import create_bot, create_dispatcher
from app.core.config import settings
from app.db.init_db import init_db
from app.db.session import engine


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required to start Telegram polling.")

    await init_db()
    bot = create_bot(settings.telegram_bot_token)
    dispatcher = create_dispatcher()
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
