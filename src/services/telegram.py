# src/service/telegram_service.py
from queue import Queue
from typing import Dict, List
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
from src.models.telegram import Update, Bot, CallbackContext
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from src.config.settings import settings
import logging

# Thiết lập logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TelegramService:
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot
        self.update_queue: Queue = Queue()
        self.dispatcher: Dispatcher = Dispatcher(
            bot,
            self.update_queue,
            workers=1
        )
        self.client: OpenAI = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.conversation_history: Dict[int, List[ChatCompletionMessageParam]] = {}
        self._register_handlers()

    def _register_handlers(self) -> None:
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(
            MessageHandler(Filters.text & ~Filters.command, self.handle_message)
        )

    def start(self, update: Update, context: CallbackContext) -> None:
        chat_id: int = update.message.chat_id
        self.conversation_history[chat_id] = []
        update.message.reply_text(
            "Xin chào! Tôi là LEV OMED BOT. Hãy gửi tin nhắn để trò chuyện!"
        )

    def handle_message(self, update: Update, context: CallbackContext) -> None:
        chat_id: int = update.message.chat_id
        user_message: str = update.message.text
        if chat_id not in self.conversation_history:
            self.conversation_history[chat_id] = []
        self.conversation_history[chat_id].append(
            {"role": "user", "content": user_message}
        )
        response: str = self.get_openai_response(chat_id)
        update.message.reply_text(response)
        self.conversation_history[chat_id].append(
            {"role": "assistant", "content": response}
        )

    def get_openai_response(self, chat_id: int) -> str:
        try:
            system_message: ChatCompletionMessageParam = {
                "role": "system",
                "content": "Bạn là một trợ lý AI thân thiện, trả lời ngắn gọn và tự nhiên.",
            }
            messages: List[ChatCompletionMessageParam] = [
                system_message
            ] + self.conversation_history[chat_id][-5:]

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=150,
                temperature=0.7,
            )
            if response.choices[0].message.content is None:
                return "Xin lỗi, tôi gặp lỗi khi xử lý yêu cầu của bạn!"
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI error: {str(e)}")
            return "Xin lỗi, tôi gặp lỗi khi xử lý yêu cầu của bạn!"

    def echo(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text(f"Bạn đã nói: {update.message.text}")

    def process_update(self, update: Update) -> None:
        self.dispatcher.process_update(update)
