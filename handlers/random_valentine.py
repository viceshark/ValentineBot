import itertools
import logging
import os
import random
from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

from phrases import VALENTINE_PHRASES
from states import MessageState

IMAGES_DIR = "resources/images"

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_random_valentine(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()  # Подтверждаем обработку callback

    try:
        #TODO:Вынеси в отдельную функуцию формирование уникальных валентинок

        # Инициализируем хранилище отправленных комбинаций
        if "sent_valentines" not in context.user_data:
            context.user_data["sent_valentines"] = []

        # Получаем все возможные комбинации
        images = [f for f in os.listdir(IMAGES_DIR) if f.endswith(('.jpg', '.png'))]
        phrases = VALENTINE_PHRASES
        all_combinations = list(itertools.product(images, phrases))

        if not all_combinations:
            await query.message.reply_text("😢 Нет доступных валентинок")
            return

        # Исключаем уже отправленные комбинации
        available = [c for c in all_combinations
                     if c not in context.user_data["sent_valentines"]]

        # Если все комбинации исчерпаны - начинаем сначала
        if not available:
            available = all_combinations
            context.user_data["sent_valentines"] = []

        # Выбираем случайную комбинацию
        selected_image, selected_phrase = random.choice(available)
        context.user_data["sent_valentines"].append((selected_image, selected_phrase))

        # Отправляем валентинку
        image_path = os.path.join(IMAGES_DIR, selected_image)
        with open(image_path, "rb") as photo:
            await query.message.reply_photo(
                photo=InputFile(photo),
                caption=selected_phrase
            )

            # Кнопки после отправки
            keyboard = [
                [InlineKeyboardButton("🔄 Хочу еще", callback_data="random_valentine")],
                [InlineKeyboardButton("Сдаться", callback_data="cancel")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text("Что дальше?", reply_markup=reply_markup)

            # Переходим в состояние ожидания повтора
            return MessageState.WAITING_FOR_RANDOM_VALENTINE

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await query.message.reply_text("❌ Не удалось отправить валентинку")
        return ConversationHandler.END