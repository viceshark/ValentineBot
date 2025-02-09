import os
import unittest
from unittest.mock import MagicMock, patch
from handlers.random_valentine import send_random_valentine
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import CallbackContext, ConversationHandler

class TestRandomValentine(unittest.TestCase):

    @patch('os.listdir')
    @patch('random.choice')
    @patch('logging.Logger.info')
    @patch('logging.Logger.error')
    @patch('handlers.random_valentine.open', new_callable=MagicMock)
    async def test_send_random_valentine_with_images(self, mock_open, mock_error, mock_info, mock_random_choice, mock_os_listdir):
        # Подготовка моков
        mock_os_listdir.return_value = ['image_1.jpg', 'image_2.jpg', 'image_3.jpg']
        mock_random_choice.side_effect = ['image_1.jpg', 'С любовью!']
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Подготовка объектов Update и CallbackContext
        update = MagicMock(spec=Update)
        update.callback_query = MagicMock(spec=Update.callback_query)
        update.callback_query.message = MagicMock(spec=Update.callback_query.message)
        update.callback_query.message.reply_photo = MagicMock()
        update.callback_query.message.reply_text = MagicMock()
        update.callback_query.answer = MagicMock()

        context = MagicMock(spec=CallbackContext)
        context.bot = MagicMock(spec=CallbackContext.bot)

        # Вызов функции
        result = await send_random_valentine(update, context)

        # Проверки
        update.callback_query.answer.assert_called_once()
        mock_os_listdir.assert_called_once_with('images')
        mock_random_choice.assert_has_calls([
            unittest.call(['image_1.jpg', 'image_2.jpg', 'image_3.jpg']),
            unittest.call(['С любовью!', 'С праздником!', 'Дарю тебе лучшие пожелания!', 'Ты лучший!', 'Валентинки - это не просто слова...'])
        ])
        mock_open.assert_called_once_with(os.path.join('images', 'image_1.jpg'), 'rb')
        update.callback_query.message.reply_photo.assert_called_once_with(photo=InputFile(mock_file), caption='С любовью!')
        update.callback_query.message.reply_text.assert_called_once_with("Что дальше?", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Вернуться в меню", callback_data="start")],
            [InlineKeyboardButton("Сдаться", callback_data="cancel")]
        ]))
        self.assertEqual(result, ConversationHandler.END)

    @patch('os.listdir')
    @patch('logging.Logger.info')
    @patch('logging.Logger.error')
    async def test_send_random_valentine_no_images(self, mock_error, mock_info, mock_os_listdir):
        # Подготовка моков
        mock_os_listdir.return_value = []

        # Подготовка объектов Update и CallbackContext
        update = MagicMock(spec=Update)
        update.callback_query = MagicMock(spec=Update.callback_query)
        update.callback_query.message = MagicMock(spec=Update.callback_query.message)
        update.callback_query.message.reply_photo = MagicMock()
        update.callback_query.message.reply_text = MagicMock()
        update.callback_query.answer = MagicMock()

        context = MagicMock(spec=CallbackContext)
        context.bot = MagicMock(spec=CallbackContext.bot)

        # Вызов функции
        result = await send_random_valentine(update, context)

        # Проверки
        update.callback_query.answer.assert_called_once()
        mock_os_listdir.assert_called_once_with('images')
        update.callback_query.message.reply_text.assert_called_once_with("Изображения не найдены 😢")
        update.callback_query.message.reply_photo.assert_not_called()
        self.assertEqual(result, ConversationHandler.END)

    @patch('os.listdir')
    @patch('random.choice')
    @patch('logging.Logger.info')
    @patch('logging.Logger.error')
    @patch('handlers.random_valentine.open', side_effect=Exception("Test Exception"))
    async def test_send_random_valentine_exception(self, mock_open, mock_error, mock_info, mock_random_choice, mock_os_listdir):
        # Подготовка моков
        mock_os_listdir.return_value = ['image_1.jpg', 'image_2.jpg', 'image_3.jpg']
        mock_random_choice.side_effect = ['image_1.jpg', 'С любовью!']

        # Подготовка объектов Update и CallbackContext
        update = MagicMock(spec=Update)
        update.callback_query = MagicMock(spec=Update.callback_query)
        update.callback_query.message = MagicMock(spec=Update.callback_query.message)
        update.callback_query.message.reply_photo = MagicMock()
        update.callback_query.message.reply_text = MagicMock()
        update.callback_query.answer = MagicMock()

        context = MagicMock(spec=CallbackContext)
        context.bot = MagicMock(spec=CallbackContext.bot)

        # Вызов функции
        result = await send_random_valentine(update, context)

        # Проверки
        update.callback_query.answer.assert_called_once()
        mock_os_listdir.assert_called_once_with('images')
        mock_random_choice.assert_has_calls([
            unittest.call(['image_1.jpg', 'image_2.jpg', 'image_3.jpg']),
            unittest.call(['С любовью!', 'С праздником!', 'Дарю тебе лучшие пожелания!', 'Ты лучший!', 'Валентинки - это не просто слова...'])
        ])
        mock_open.assert_called_once_with(os.path.join('images', 'image_1.jpg'), 'rb')
        update.callback_query.message.reply_photo.assert_not_called()
        update.callback_query.message.reply_text.assert_called_once_with("Произошла ошибка 😢")
        mock_error.assert_called_once_with("Ошибка: Test Exception")
        self.assertEqual(result, ConversationHandler.END)

if __name__ == "__main__":
    unittest.main()