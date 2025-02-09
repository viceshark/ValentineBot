import sqlite3
import unittest
from unittest.mock import MagicMock, patch
from handlers.start import start, send_start_menu
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from states import MessageState
import database

class TestStartHandlers(unittest.TestCase):

    @patch('database.register_user')
    @patch('logging.Logger.info')
    @patch('logging.Logger.error')
    async def test_start_with_new_user(self, mock_error, mock_info, mock_register_user):
        # Подготовка моков
        mock_register_user.return_value = None  # Успешная регистрация

        # Подготовка объектов Update и CallbackContext
        update = MagicMock(spec=Update)
        update.message = MagicMock(spec=Update.message)
        update.message.from_user = MagicMock(spec=Update.message.from_user)
        update.message.from_user.first_name = "Kobe"
        update.message.from_user.id = 645723579
        update.message.from_user.username = "kobe1"
        update.message.reply_text = MagicMock()

        context = MagicMock(spec=CallbackContext)
        context.user_data = {'some_key': 'some_value'}

        # Вызов функции
        result = await start(update, context)

        # Проверки
        context.user_data.clear.assert_called_once()
        update.message.reply_text.assert_has_calls([
            unittest.call("Здарова, Kobe! Я Вики - бот для отправки валентинок команды Pegasus 🦄🪽"),
            unittest.call("✅ Вы успешно зарегистрированы!")
        ])
        mock_register_user.assert_called_once_with(645723579, "kobe1")
        mock_info.assert_not_called()
        mock_error.assert_not_called()
        update.message.reply_text.assert_called_with("Выбери действие:", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💌 Отправить валентинку", callback_data="send_valentine")],
            [InlineKeyboardButton("🌈 Получить валентинку от команды", callback_data="random_valentine")]
        ]))
        self.assertEqual(result, MessageState.WAITING_FOR_RECEIVER)

    @patch('database.register_user')
    @patch('logging.Logger.info')
    @patch('logging.Logger.error')
    async def test_start_with_existing_user(self, mock_error, mock_info, mock_register_user):
        # Подготовка моков
        mock_register_user.side_effect = sqlite3.IntegrityError("User already exists")

        # Подготовка объектов Update и CallbackContext
        update = MagicMock(spec=Update)
        update.message = MagicMock(spec=Update.message)
        update.message.from_user = MagicMock(spec=Update.message.from_user)
        update.message.from_user.first_name = "Kobe"
        update.message.from_user.id = 645723579
        update.message.from_user.username = "kobe1"
        update.message.reply_text = MagicMock()

        context = MagicMock(spec=CallbackContext)
        context.user_data = {'some_key': 'some_value'}

        # Вызов функции
        result = await start(update, context)

        # Проверки
        context.user_data.clear.assert_called_once()
        update.message.reply_text.assert_has_calls([
            unittest.call("Здарова, Kobe! Я Вики - бот для отправки валентинок команды Pegasus 🦄🪽"),
        ])
        mock_register_user.assert_called_once_with(645723579, "kobe1")
        mock_info.assert_called_once_with("Пользователь kobe1 уже зарегистрирован (IntegrityError).")
        mock_error.assert_not_called()
        update.message.reply_text.assert_called_with("Выбери действие:", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💌 Отправить валентинку", callback_data="send_valentine")],
            [InlineKeyboardButton("🌈 Получить валентинку от команды", callback_data="random_valentine")]
        ]))
        self.assertEqual(result, MessageState.WAITING_FOR_RECEIVER)

    @patch('database.register_user')
    @patch('logging.Logger.info')
    @patch('logging.Logger.error')
    async def test_start_with_exception(self, mock_error, mock_info, mock_register_user):
        # Подготовка моков
        mock_register_user.side_effect = Exception("Test Exception")

        # Подготовка объектов Update и CallbackContext
        update = MagicMock(spec=Update)
        update.message = MagicMock(spec=Update.message)
        update.message.from_user = MagicMock(spec=Update.message.from_user)
        update.message.from_user.first_name = "Kobe"
        update.message.from_user.id = 645723579
        update.message.from_user.username = "kobe1"
        update.message.reply_text = MagicMock()

        context = MagicMock(spec=CallbackContext)
        context.user_data = {'some_key': 'some_value'}

        # Вызов функции
        result = await start(update, context)

        # Проверки
        context.user_data.clear.assert_called_once()
        update.message.reply_text.assert_has_calls([
            unittest.call("Здарова, Kobe! Я Вики - бот для отправки валентинок команды Pegasus 🦄🪽"),
            unittest.call("🚫 Произошла ошибка. Попробуйте позже через /start")
        ])
        mock_register_user.assert_called_once_with(645723579, "kobe1")
        mock_info.assert_not_called()
        mock_error.assert_called_once_with("Критическая ошибка в /start: Test Exception")
        self.assertEqual(result, ConversationHandler.END)

    @patch('database.register_user')
    @patch('logging.Logger.info')
    @patch('logging.Logger.error')
    async def test_start_with_callback_query(self, mock_error, mock_info, mock_register_user):
        # Подготовка моков
        mock_register_user.return_value = None  # Успешная регистрация

        # Подготовка объектов Update и CallbackContext
        update = MagicMock(spec=Update)
        update.callback_query = MagicMock(spec=Update.callback_query)
        update.callback_query.message = MagicMock(spec=Update.callback_query.message)
        update.callback_query.message.from_user = MagicMock(spec=Update.callback_query.message.from_user)
        update.callback_query.message.from_user.first_name = "Kobe"
        update.callback_query.message.from_user.id = 645723579
        update.callback_query.message.from_user.username = "kobe1"
        update.callback_query.message.reply_text = MagicMock()
        update.callback_query.answer = MagicMock()

        context = MagicMock(spec=CallbackContext)
        context.user_data = {'some_key': 'some_value'}

        # Вызов функции
        result = await start(update, context)

        # Проверки
        context.user_data.clear.assert_called_once()
        update.callback_query.message.reply_text.assert_has_calls([
            unittest.call("Здарова, Kobe! Я Вики - бот для отправки валентинок команды Pegasus 🦄🪽"),
            unittest.call("✅ Вы успешно зарегистрированы!")
        ])
        mock_register_user.assert_called_once_with(645723579, "kobe1")
        mock_info.assert_not_called()
        mock_error.assert_not_called()
        update.callback_query.message.reply_text.assert_called_with("Выбери действие:", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💌 Отправить валентинку", callback_data="send_valentine")],
            [InlineKeyboardButton("🌈 Получить валентинку от команды", callback_data="random_valentine")]
        ]))
        update.callback_query.answer.assert_called_once()
        self.assertEqual(result, MessageState.WAITING_FOR_RECEIVER)

    @patch('database.register_user')
    @patch('logging.Logger.info')
    @patch('logging.Logger.error')
    async def test_start_without_message_or_callback_query(self, mock_error, mock_info, mock_register_user):
        # Подготовка объектов Update и CallbackContext
        update = MagicMock(spec=Update)
        update.message = None
        update.callback_query = None

        context = MagicMock(spec=CallbackContext)
        context.user_data = {'some_key': 'some_value'}

        # Вызов функции
        result = await start(update, context)

        # Проверки
        context.user_data.clear.assert_not_called()
        mock_register_user.assert_not_called()
        mock_info.assert_not_called()
        mock_error.assert_called_once_with("Не удалось получить сообщение или callback_query")
        self.assertIsNone(result)