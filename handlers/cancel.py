from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler


async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text("Отменено.")
    return ConversationHandler.END