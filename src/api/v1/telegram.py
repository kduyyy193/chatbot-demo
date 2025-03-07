# src/api/v1/telegram.py
from fastapi import APIRouter, Request, HTTPException
from src.services.telegram import TelegramService
from src.models.telegram import Update, Bot
from src.config.settings import settings
import asyncio
from src.logger_config import setup_logging

logger = setup_logging()

router = APIRouter()

bot = Bot(settings.TELEGRAM_BOT_TOKEN)
telegram_service = TelegramService(bot)


@router.post("/webhook")
async def webhook(request: Request):
    try:
        body = await request.body()
        logger.info(f"TOken: {settings.TELEGRAM_BOT_TOKEN}")
        logger.info("Received webhook data: {body}")
        if not body:
            raise HTTPException(status_code=400, detail="Empty request body")
        update = Update.de_json(await request.json(), bot)
        if update is None:
            raise HTTPException(status_code=400, detail="Invalid update data")
        await asyncio.get_event_loop().run_in_executor(None, telegram_service.process_update, update)
        return {"status": "ok"}
    except ValueError as e:
        logger.error(f"JSON decode error: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid JSON data")
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def setup_webhook():
    logger.info(f"Setting webhook to: {settings.WEBHOOK_URL}")
    success = bot.set_webhook(url=settings.WEBHOOK_URL)
    if not success:
        logger.error("Failed to set Telegram webhook")
        raise RuntimeError("Failed to set Telegram webhook")
    logger.info("Webhook set successfully")
