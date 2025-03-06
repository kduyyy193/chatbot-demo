# src/service/telegram_service.py
from queue import Queue
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
from src.models.telegram import Update, Bot, CallbackContext

class TelegramService:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.update_queue = Queue()
        self.dispatcher = Dispatcher(bot, self.update_queue, workers=1)
        self._register_handlers()

    def _register_handlers(self):
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.echo))

    def start(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text("Xin chào! Tôi là bot demo. Gửi tin nhắn bất kỳ để tôi trả lời!")

    def echo(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text(f"Bạn đã nói: {update.message.text}")

    def process_update(self, update: Update):
        self.dispatcher.process_update(update)