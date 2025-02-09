import logging

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def cancel(update: Update, context: CallbackContext):
    """Отмена действия и возврат в меню"""
    try:
        # Получаем сообщение из update
        if update.message:
            message = update.message
        elif update.callback_query:
            query = update.callback_query
            message = query.message
            await query.answer()  # Подтверждаем обработку callback
        else:
            logger.error("Не удалось получить сообщение")
            return

        # Очищаем контекст
        context.user_data.clear()

        # Отправляем сообщение об отмене
        await message.reply_text("Пока-пока! Жми /start если хочешь еще раз")

        return ConversationHandler.END

    except Exception as e:
        logger.error(f"Ошибка в cancel: {e}")
        if "message" in locals():
            await message.reply_text("🔥 Не удалось отменить действие")
        return ConversationHandler.END