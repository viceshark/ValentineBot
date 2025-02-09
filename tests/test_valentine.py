import unittest
from unittest.mock import MagicMock, patch
from handlers.valentine import send_valentine_menu, choose_receiver, handle_message, handle_attached_image
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from states import MessageState

class TestValentineHandlers(unittest.TestCase):

    @patch('database.get_users')
    @patch('logging.Logger.info')
    @patch('logging.Logger.error')
    async def test_send_valentine_menu_with_users(self, mock_error, mock_info, mock_get_users):
        # Подготовка моков
        mock_get_users.return_value = [(123456789, "user1"), (987654321, "user2")]

        # Подготовка объектов Update и CallbackContext
        update = MagicMock(spec=Update)
        update.callback_query = MagicMock(spec=Update.callback_query)
        update.callback_query.message = MagicMock(spec=Update.callback_query.message)
        update.callback_query.message.reply_text = MagicMock()
        update.callback_query.answer = MagicMock()

        context = MagicMock(spec=CallbackContext)
        context.user_data = {}
        context.effective_user.id = 645723579

        # Вызов функции
        result = await send_valentine_menu(update, context)

        # Проверки
        update.callback_query.answer.assert_called_once()
        mock_get_users.assert_called_once()
        update.callback_query.message.reply_text.assert_called_once_with(
            "Выбери получателя:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("user1", callback_data="user_123456789")],
                [InlineKeyboardButton("user2", callback_data="user_987654321")],
                [InlineKeyboardButton("Передумал", callback_data="cancel")]
            ])
        )
        mock_info.assert_not_called()
        mock_error.assert_not_called()
        self.assertEqual(result, MessageState.WAITING_FOR_MESSAGE)

    @patch('database.get_users')
    @patch('logging.Logger.info')
    @patch('logging.Logger.error')
    async def test_send_valentine_menu_no_users(self, mock_error, mock_info, mock_get_users):
        # Подготовка моков
        mock_get_users.return_value = []

        # Подготовка объектов Update и CallbackContext
        update = MagicMock(spec=Update)
        update.callback_query = MagicMock(spec=Update.callback_query)
        update.callback_query.message = MagicMock(spec=Update.callback_query.message)
        update.callback_query.message.reply_text = MagicMock()
        update.callback_query.answer = MagicMock()

        context = MagicMock(spec=CallbackContext)
        context.user_data = {}
        context.effective_user.id = 645723579

        # Вызов функции
        result = await send_valentine_menu(update, context)

        # Проверки
        update.callback_query.answer.assert_called_once()
        mock_get_users.assert_called_once()
        update.callback_query.message.reply_text.assert_called_once_with(
            "Нет зарегистрированных пользователей для отправки валентинки. Жми /start"
        )
        mock_info.assert_not_called()
        mock_error.assert_not_called()
        self.assertEqual(result, ConversationHandler.END)

    @patch('database.get_users')
    @patch('logging.Logger.info')
    @patch('logging.Logger.error')
    async def test_choose_receiver(self, mock_error, mock_info, mock_get_users):
        # Подготовка моков
        mock_get_users.return_value = [(123456789, "user1"), (987654321, "user2")]

        # Подготовка объектов Update и CallbackContext
        update = MagicMock(spec=Update)
        update.callback_query = MagicMock(spec=Update.callback_query)
        update.callback_query.message = MagicMock(spec=Update.callback_query.message)
        update.callback_query.message.reply_text = MagicMock()
        update.callback_query.answer = MagicMock()
        update.callback_query.data = "user_123456789"

        context = MagicMock(spec=CallbackContext)
        context.user_data = {}

        # Вызов функции
        result = await choose_receiver(update, context)

        # Проверки
        update.callback_query.answer.assert_called_once()
        mock_get_users.assert_not_called()
        update.callback_query.message.reply_text.assert_called_once_with(
            "🫦 🫦 🫦 Что хочешь сказать своему валентиносу 🫦 🫦 🫦:"
        )
        mock_info.assert_called_once_with("Receiver ID set to: 123456789")
        mock_error.assert_not_called()
        self.assertEqual(result, MessageState.WAITING_FOR_MESSAGE)

    @patch('database.get_users')
    @patch('logging.Logger.info')
    @patch('logging.Logger.error')
    async def test_handle_message(self, mock_error, mock_info, mock_get_users):
        # Подготовка моков
        mock_get_users.return_value = [(123456789, "user1"), (987654321, "user2")]

        # Подготовка объектов Update и CallbackContext
        update = MagicMock(spec=Update)
        update.message = MagicMock(spec=Update.message)
        update.message.text = "Это моя валентинка!"
        update.message.reply_text = MagicMock()

        context = MagicMock(spec=CallbackContext)
        context.user_data = {}

        # Вызов функции
        result = await handle_message(update, context)

        # Проверки
        mock_get_users.assert_not_called()
        update.message.reply_text.assert_called_once_with("Приложи свою картинку сладкий 😽:")
        mock_info.assert_called_once_with("Message set to: Это моя валентинка!")
        mock_error.assert_not_called()
        self.assertEqual(result, MessageState.WAITING_FOR_ATTACHED_IMAGE)

    @patch('database.save_valentine')
    @patch('database.get_username_by_id')
    @patch('logging.Logger.info')
    @patch('logging.Logger.error')
    async def test_handle_attached_image(self, mock_error, mock_info, mock_get_username_by_id, mock_save_valentine):
        # Подготовка моков
        mock_save_valentine.return_value = None
        mock_get_username_by_id.return_value = "user1"

        # Подготовка объектов Update и CallbackContext
        update = MagicMock(spec=Update)
        update.message = MagicMock(spec=Update.message)
        update.message.photo = [MagicMock()]
        update.message.photo[-1].file_id = "AgACAgIAAxkBAAIJT2QY..."
        update.message.reply_text = MagicMock()

        context = MagicMock(spec=CallbackContext)
        context.user_data = {
            'receiver_id': 123456789,
            'message': "Это моя валентинка!"
        }
        context.effective_user.id = 645723579
        context.bot = MagicMock(spec=CallbackContext.bot)
        context.bot.send_message = MagicMock()
        context.bot.send_photo = MagicMock()

        # Вызов функции
        result = await handle_attached_image(update, context)

        # Проверки
        update.message.reply_text.assert_called_once_with("💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖  Твое послание доставлено получателю! 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖")
        update.message.reply_text.assert_called_with("Чекай что получилось:")
        context.bot.send_message.assert_called_once_with(
            chat_id=123456789,
            text="🎉 Тебе пришла валентинка!  💞 💞 💞"
        )
        context.bot.send_photo.assert_called_once_with(
            chat_id=123456789,
            photo="AgACAgIAAxkBAAIJT2QY...",
            caption="Это моя валентинка!"
        )
        mock_save_valentine.assert_called_once_with(
            645723579,
            123456789,
            "Это моя валентинка!",
            "attached",
            "resources/user_images/AgACAgIAAxkBAAIJT2QY....jpg"
        )
        mock_info.assert_called_once_with("Valentine saved with attached image: resources/user_images/AgACAgIAAxkBAAIJT2QY....jpg")
        mock_error.assert_not_called()
        context.bot.send_message.assert_called_with(
            chat_id=update.effective_chat.id,
            text="Получатель: user1"
        )
        context.bot.send_photo.assert_called_with(
            chat_id=update.effective_chat.id,
            photo="AgACAgIAAxkBAAIJT2QY...",
            caption="Это моя валентинка!"
        )
        update.message.reply_text.assert_called_with("Ты булочка 🐶", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Дело сделано, босс!", callback_data="cancel")]
        ]))
        self.assertEqual(result, ConversationHandler.END)

    @patch('database.save_valentine')
    @patch('database.get_username_by_id')
    @patch('logging.Logger.info')
    @patch('logging.Logger.error')
    async def test_handle_attached_image_exception(self, mock_error, mock_info, mock_get_username_by_id, mock_save_valentine):
        # Подготовка моков
        mock_save_valentine.return_value = None
        mock_get_username_by_id.return_value = "user1"

        # Подготовка объектов Update и CallbackContext
        update = MagicMock(spec=Update)
        update.message = MagicMock(spec=Update.message)
        update.message.photo = [MagicMock()]
        update.message.photo[-1].file_id = "AgACAgIAAxkBAAIJT2QY..."
        update.message.reply_text = MagicMock()

        context = MagicMock(spec=CallbackContext)
        context.user_data = {
            'receiver_id': 123456789,
            'message': "Это моя валентинка!"
        }
        context.effective_user.id = 645723579
        context.bot = MagicMock(spec=CallbackContext.bot)
        context.bot.send_message = MagicMock(side_effect=Exception("Test Exception"))
        context.bot.send_photo = MagicMock()

        # Вызов функции
        result = await handle_attached_image(update, context)

        # Проверки
        update.message.reply_text.assert_has_calls([
            unittest.call("💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖  Твое послание доставлено получателю! 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖 💖"),
            unittest.call("Чекай что получилось:"),
            unittest.call("Ты булочка 🐶", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Дело сделано, босс!", callback_data="cancel")]
            ]))
        ])
        mock_save_valentine.assert_called_once_with(
            645723579,
            123456789,
            "Это моя валентинка!",
            "attached",
            "resources/user_images/AgACAgIAAxkBAAIJT2QY....jpg"
        )
        mock_info.assert_called_once_with("Valentine saved with attached image: resources/user_images/AgACAgIAAxkBAAIJT2QY....jpg")
        mock_error.assert_called_once_with("Не удалось отправить сообщение получателю: Test Exception")
        context.bot.send_message.assert_called_once_with(
            chat_id=123456789,
            text="🎉 Тебе пришла валентинка!  💞 💞 💞"
        )
        context.bot.send_photo.assert_not_called()
        context.bot.send_message.assert_called_with(
            chat_id=update.effective_chat.id,
            text="Получатель: user1"
        )
        context.bot.send_photo.assert_not_called()
        self.assertEqual(result, ConversationHandler.END)

if __name__ == "__main__":
    unittest.main()