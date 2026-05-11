from fastapi import APIRouter, HTTPException, Request, status

from app.bot.dispatcher import create_bot, create_dispatcher
from app.core.config import settings

router = APIRouter()


@router.post("/webhook/{secret}")
async def telegram_webhook(secret: str, request: Request) -> dict[str, str]:
    if secret != settings.telegram_webhook_secret:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid webhook secret.")
    if not settings.telegram_bot_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Telegram bot token is not configured.",
        )

    from aiogram.types import Update

    payload = await request.json()
    bot = create_bot(settings.telegram_bot_token)
    dispatcher = create_dispatcher()
    update = Update.model_validate(payload, context={"bot": bot})
    try:
        await dispatcher.feed_update(bot, update)
    finally:
        await bot.session.close()
    return {"status": "ok"}
