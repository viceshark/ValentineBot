from telegram import Update
from telegram.ext import CallbackContext

import database
from states import MessageState
from database import register_user

async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    await update.message.reply_text(f"🎉 Привет, {user.first_name}! Я Вики - бот для отправки валентинок команды Pegasus.")
    await register_user(update, context)
    await send_start_menu(update, context)
    return MessageState.WAITING_FOR_RECEIVER

async def register_user(update: Update, context: CallbackContext):
    user = update.effective_user
    try:
        database.register_user(user.id, user.username)
        await update.message.reply_text("Вы успешно зарегистрировались!")
    except ValueError as e:
        await update.message.reply_text(str(e))

async def send_start_menu(update: Update, context: CallbackContext):
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = [
        [InlineKeyboardButton("Отправить валентинку", callback_data="send_valentine")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выбери действие:", reply_markup=reply_markup)