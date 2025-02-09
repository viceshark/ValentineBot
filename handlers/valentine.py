import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

from states import MessageState
from database import get_users, save_valentine, get_username_by_id

logger = logging.getLogger(__name__)
async def send_valentine_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    current_user_id = update.effective_user.id
    users = get_users()
    users = [user for user in users if user[0] != current_user_id]

    if not users:
        await query.edit_message_text("Нет зарегистрированных пользователей для отправки валентинки. Жми /start")
        return ConversationHandler.END

    keyboard = []
    for user in users:
        keyboard.append([InlineKeyboardButton(user[1], callback_data=f"user_{user[0]}")])
    keyboard.append([InlineKeyboardButton("Передумал", callback_data="cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Выбери получателя:", reply_markup=reply_markup)
    return MessageState.WAITING_FOR_MESSAGE

async def choose_receiver(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    receiver_id = int(query.data.split("_")[1])
    context.user_data['receiver_id'] = receiver_id
    await query.edit_message_text("🫦 🫦 🫦 Что хочешь сказать своему валентиносу 🫦 🫦 🫦:")
    return MessageState.WAITING_FOR_MESSAGE

async def handle_message(update: Update, context: CallbackContext):
    message = update.message.text
    context.user_data['message'] = message
    logger.info(f"Message set to: {message}")
    await update.message.reply_text("Приложи свою картинку сладкий 😽:")
    return MessageState.WAITING_FOR_ATTACHED_IMAGE

async def handle_attached_image(update: Update, context: CallbackContext):
    photo_file = update.message.photo[-1]
    file_path = f"resources/user_images/{photo_file.file_id}.jpg"
    new_file = await photo_file.get_file()
    await new_file.download_to_drive(file_path)

    receiver_id = context.user_data.get('receiver_id')
    message = context.user_data.get('message')
    sender_id = update.effective_user.id

    save_valentine(sender_id, receiver_id, message, "attached", file_path)

    try:
        await context.bot.send_message(
            chat_id=receiver_id,
            text=f"🎉 Тебе пришла валентинка!  💞 💞 💞"
        )
        await context.bot.send_photo(
            chat_id=receiver_id,
            photo=photo_file.file_id,
            caption=message
        )
    except Exception as e:
        logger.error(f"Не удалось отправить сообщение получателю: {e}")
    receiver_username = get_username_by_id(receiver_id)
    await update.message.reply_text("💞 💞 💞 💞 💞 💞 💞 💞 💞 💞 💞 💞 💞 💞 💞 💞 💞 💞 💞 💞  Твое послание доставлено получателю! 💞 💞 💞 💞 💞 💞 💞 💞 💞 💞 💞 💞 💞 💞 💞 💞 💞 💞 💞 💞")
    await update.message.reply_text("Чекай что получилось:")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Получатель: {receiver_username}"
    )
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=photo_file.file_id,
        caption=message
    )
    keyboard = [
        [InlineKeyboardButton("Дело сделано, босс!", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Ты булочка 🐶", reply_markup=reply_markup)
    return ConversationHandler.END