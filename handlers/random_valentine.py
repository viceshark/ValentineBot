import itertools
import logging
import os
import random
from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

from phrases import VALENTINE_PHRASES
from states import MessageState


# t.vasiliev    Исправил директорию с изображениями
IMAGES_DIR = "images"

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_random_valentine(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()  # Подтверждаем обработку callback

    try:
        # Инициализируем хранилище отправленных картинок для пользователя
        if "sent_images" not in context.user_data:
            context.user_data["sent_images"] = []

        # Получаем все доступные картинки
        images = [f for f in os.listdir(IMAGES_DIR) if f.endswith(('.jpg', '.png'))]

        if not images:
            await query.message.reply_text("😢 Нет доступных картинок")
            return

        # Исключаем уже отправленные картинки
        available = [img for img in images if img not in context.user_data["sent_images"]]

        # Если все картинки исчерпаны - начинаем сначала
        # t.vasiliev    Исправил баг бесконечных валентинок
        # if not available:
        #     available = images
        #     context.user_data["sent_images"] = []

        # Выбираем случайную картинку
        selected_image = random.choice(available)
        context.user_data["sent_images"].append(selected_image)
        logger.info("Картинки пользователя:")
        logger.info(context.user_data["sent_images"])
        # Отправляем картинку
        image_path = os.path.join(IMAGES_DIR, selected_image)
        with open(image_path, "rb") as photo:
            await query.message.reply_photo(
                photo=InputFile(photo),
            )

        # Добавляем кнопки после отправки картинки
        keyboard = [
            [InlineKeyboardButton("🔄 Хочу еще", callback_data="random_valentine")],
            [InlineKeyboardButton("❌ Сдаться", callback_data="cancel")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Что дальше?", reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await query.message.reply_text("Валентинки кончились 😭")