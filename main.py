import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from dotenv import load_dotenv
import os

import database
from handlers.start import start, send_start_menu
from handlers.valentine import send_valentine_menu, choose_receiver, handle_message, choose_image_type, handle_attached_image
from handlers.cancel import cancel
from states import MessageState

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация базы данных
database.init_db()

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
        },
        fallbacks=[CommandHandler("cancel", cancel),
                   CallbackQueryHandler(start, pattern="^start$")],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()