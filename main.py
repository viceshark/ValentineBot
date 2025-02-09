import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from dotenv import load_dotenv
import os

import database
from handlers.random_valentine import send_random_valentine
from handlers.start import start, send_start_menu
from handlers.valentine import send_valentine_menu, choose_receiver, handle_message, handle_attached_image
from handlers.cancel import cancel
from states import MessageState

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig( level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Инициализация базы данных
database.init_db()

def main():
    application = Application.builder().token(os.getenv("BOT_TOKEN")).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MessageState.WAITING_FOR_RECEIVER: [
                CallbackQueryHandler(send_valentine_menu, pattern="^send_valentine$"),
                CallbackQueryHandler(send_random_valentine, pattern="^random_valentine$"),
                CallbackQueryHandler(cancel, pattern="^cancel$")
            ],
            MessageState.WAITING_FOR_MESSAGE: [
                CallbackQueryHandler(choose_receiver, pattern="^user_"),
                CallbackQueryHandler(cancel, pattern="^cancel$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
            ],
            MessageState.WAITING_FOR_ATTACHED_IMAGE: [
                CallbackQueryHandler(cancel, pattern="^cancel$"),
                MessageHandler(filters.PHOTO, handle_attached_image)
            ],
            MessageState.WAITING_FOR_RANDOM_VALENTINE: [
                CallbackQueryHandler(send_random_valentine, pattern="^random_valentine$"),
                CallbackQueryHandler(cancel, pattern="^cancel$")
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel),
                   CallbackQueryHandler(start, pattern="^start$"),
                   CallbackQueryHandler(cancel, pattern="^cancel$")],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(start, pattern="^start$"))
    application.add_handler(CallbackQueryHandler(cancel, pattern="^cancel$"))
    application.run_polling()

if __name__ == "__main__":
    main()