import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
    CallbackQueryHandler,
    ConversationHandler,
)
from dotenv import load_dotenv
import os
import database
# TODO: Декомпозировать на разные файлы. Вынести хендлеры сообщений и хендлеры картинок
# TODO: Поправить баг с возвращением в меню выбора чуваков
# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация базы данных
database.init_db()

# Определение состояний
class MessageState:
    WAITING_FOR_RECEIVER = 1
    WAITING_FOR_MESSAGE = 2
    WAITING_FOR_IMAGE_TYPE = 3
    WAITING_FOR_ATTACHED_IMAGE = 4
    WAITING_FOR_SELECTED_IMAGE = 5


# Команда /start
async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    await update.message.reply_text(f"🎉 Привет, {user.first_name}! Я Вики - бот для отправки валентинок команды Pegasus.")
    await register_user(update, context)
    await send_start_menu(update, context)
    return MessageState.WAITING_FOR_RECEIVER


# Регистрация пользователя
async def register_user(update: Update, context: CallbackContext):
    user = update.effective_user
    try:
        database.register_user(user.id, user.username)
        await update.message.reply_text("Вы успешно зарегистрировались!")
    except ValueError as e:
        await update.message.reply_text(str(e))


# Отправка начального меню
async def send_start_menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Отправить валентинку", callback_data="send_valentine")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выбери действие:", reply_markup=reply_markup)


# Обработка нажатия на кнопку "Отправить валентинку"
async def send_valentine_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    # Исключаем текущего пользователя из списка получателей
    current_user_id = update.effective_user.id
    users = database.get_users()
    users = [user for user in users if user[0] != current_user_id]  # Исключаем себя

    if not users:
        await query.edit_message_text("Нет зарегистрированных пользователей для отправки валентинки.")
        return ConversationHandler.END

    keyboard = []
    for user in users:
        keyboard.append([InlineKeyboardButton(user[1], callback_data=f"user_{user[0]}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Выбери получателя:", reply_markup=reply_markup)
    return MessageState.WAITING_FOR_MESSAGE


# Обработка выбора получателя
async def choose_receiver(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    receiver_id = int(query.data.split("_")[1])
    context.user_data['receiver_id'] = receiver_id
    await query.edit_message_text("🫦 🫦 🫦 Что хочешь сказать своему валентиносу 🫦 🫦 🫦:")
    return MessageState.WAITING_FOR_MESSAGE


# Обработка текстового сообщения (текст валентинки)
async def handle_message(update: Update, context: CallbackContext):
    message = update.message.text
    context.user_data['message'] = message

    keyboard = [
        [InlineKeyboardButton("Приложить свою картинку", callback_data="attach_image")],
        # TODO: Починить выбор из предложенных. Дб выбор из любых картинок в директории
        # [InlineKeyboardButton("Выбрать из предложенных", callback_data="select_image")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("  😽 😽 😽 Выбери способ отправки картинки  😽 😽 😽:", reply_markup=reply_markup)
    return MessageState.WAITING_FOR_IMAGE_TYPE


# Обработка выбора типа картинки
async def choose_image_type(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    image_type = query.data
    context.user_data['image_type'] = image_type

    if image_type == "attach_image":
        await query.edit_message_text("Приложи свою картинку сладкий 😽:")
        return MessageState.WAITING_FOR_ATTACHED_IMAGE
    elif image_type == "select_image":
        keyboard = [
            [InlineKeyboardButton("Картинка 1", callback_data="image_1.jpg")],
            [InlineKeyboardButton("Картинка 2", callback_data="image_2.jpg")],
            [InlineKeyboardButton("Картинка 3", callback_data="image_3.jpg")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Выбери из предложенных картинок:", reply_markup=reply_markup)
        return MessageState.WAITING_FOR_SELECTED_IMAGE


# Обработка приложенной картинки
async def handle_attached_image(update: Update, context: CallbackContext):
    photo_file = update.message.photo[-1]
    file_path = f"user_images/{photo_file.file_id}.jpg"
    new_file = await photo_file.get_file()
    await new_file.download_to_drive(file_path)

    receiver_id = context.user_data.get('receiver_id')
    message = context.user_data.get('message')
    sender_id = update.effective_user.id

    # Сохраняем валентинку в базу данных
    database.save_valentine(sender_id, receiver_id, message, "attached", file_path)

    # Отправляем уведомление получателю
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

    await update.message.reply_text("💞 💞 💞 Твое сладкое послание доставлено получателю! 💞 💞 💞")
    # TODO: должны показать валентинку тому кто ее отправил см main.py:137
    # Выводим текущему пользователю отправленное сообщение и картинку
    # await update.message.reply_text("Ты отправил валентинку! Молодец! Вот она:")
    # await context.bot.send_message(
    #     chat_id=update.effective_chat.id,
    #     text=f"Получатель: {database.get_username_by_id(receiver_id)}"
    # )
    # await context.bot.send_message(
    #     chat_id=update.effective_chat.id,
    #     text=f"Сообщение: {message}"
    # )
    # await context.bot.send_photo(
    #     chat_id=update.effective_chat.id,
    #     photo=open(f"images/{image_name}", "rb"),
    #     caption="Твоя валентинка с картинкой!"
    # )
    await send_start_menu(update, context)  # Возвращаем в начальное меню
    return ConversationHandler.END


# Обработка выбранной картинки
async def handle_selected_image(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    image_name = query.data
    receiver_id = context.user_data.get('receiver_id')
    message = context.user_data.get('message')
    sender_id = update.effective_user.id

    # Сохраняем валентинку в базу данных
    database.save_valentine(sender_id, receiver_id, message, "selected", image_name)

    # Отправляем уведомление получателю
    try:
        await context.bot.send_message(
            chat_id=receiver_id,
            text=f"🎉 Тебе пришла валентинка!\n\nСообщение: {message}"
        )
        await context.bot.send_photo(
            chat_id=receiver_id,
            photo=open(f"images/{image_name}", "rb"),  # Отправляем выбранную картинку
            caption="Валентинка с картинкой!"
        )
    except Exception as e:
        logger.error(f"Не удалось отправить сообщение получателю: {e}")

    await send_start_menu(update, context)  # Возвращаем в начальное меню
    return ConversationHandler.END


# Отмена диалога
async def cancel(update: Update, context: CallbackContext):

    await update.message.reply_text("Отменено.")
    return ConversationHandler.END


# Основная функция
def main():
    application = Application.builder().token(os.getenv("BOT_TOKEN")).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MessageState.WAITING_FOR_RECEIVER: [
                CallbackQueryHandler(send_valentine_menu, pattern="^send_valentine$")
            ],
            MessageState.WAITING_FOR_MESSAGE: [
                CallbackQueryHandler(choose_receiver, pattern="^user_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
            ],
            MessageState.WAITING_FOR_IMAGE_TYPE: [
                CallbackQueryHandler(choose_image_type, pattern="^(attach_image|select_image)$")
            ],
            MessageState.WAITING_FOR_ATTACHED_IMAGE: [
                MessageHandler(filters.PHOTO, handle_attached_image)
            ],
            MessageState.WAITING_FOR_SELECTED_IMAGE: [
                CallbackQueryHandler(handle_selected_image, pattern="^image_")
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()