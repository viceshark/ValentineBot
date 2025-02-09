import logging
import sqlite3

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

import database
from states import MessageState

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext):
    """Обработка команды /start и возврата в меню"""
    try:
        # Определяем источник вызова: сообщение или callback-кнопка
        if update.message:
            message = update.message
        elif update.callback_query:
            query = update.callback_query
            message = query.message
            await query.answer()  # Подтверждаем нажатие кнопки
        else:
            logger.error("Не удалось получить сообщение или callback_query")
            return

        context.user_data.clear()

        user = message.from_user
        await message.reply_text(
            f"Здарова, {user.first_name}! Я Вики - бот для отправки валентинок команды Pegasus 🦄🪽"
        )
        try:
            database.register_user(user.id, user.username)
            await message.reply_text("✅ Вы успешно зарегистрированы!")
        except sqlite3.IntegrityError:
            logger.info(f"Пользователь {user.username} уже зарегистрирован (IntegrityError).")
        except Exception as e:
            logger.error(f"Ошибка при регистрации пользователя: {e}")

        keyboard = [
            [InlineKeyboardButton("💌 Отправить валентинку", callback_data="send_valentine")],
            [InlineKeyboardButton("🌈 Получить валентинку от команды", callback_data="random_valentine")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text("Выбери действие:", reply_markup=reply_markup)

        return MessageState.WAITING_FOR_RECEIVER

    except Exception as e:
        logger.error(f"Критическая ошибка в /start: {str(e)}")
        await message.reply_text("🚫 Произошла ошибка. Попробуйте позже через /start")
        return ConversationHandler.END

async def register_user(update: Update, context: CallbackContext):
    user = update.effective_user
    try:
        database.register_user(user.id, user.username)
        await update.message.reply_text("Вы успешно зарегистрировались!")
    except sqlite3.IntegrityError:
        logger.info(f"Пользователь {user.username} уже зарегистрирован (IntegrityError).")
    except Exception as e:
        logger.error(f"Ошибка при регистрации пользователя: {e}")

async def send_start_menu(update: Update, context: CallbackContext):
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = [
        [InlineKeyboardButton("Отправить валентинку", callback_data="send_valentine")],
        [InlineKeyboardButton("Получить валентинку от команды", callback_data="random_valentine")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выбери действие:", reply_markup=reply_markup)