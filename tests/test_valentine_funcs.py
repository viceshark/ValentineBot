import unittest
from unittest.mock import MagicMock, patch

from main import send_valentine_menu, handle_attached_image

class TestValentineSending(unittest.TestCase):
    def setUp(self):
        self.update = MagicMock()
        self.context = MagicMock()
        self.update.effective_user = MagicMock()
        self.update.effective_user.id = 123
        self.update.callback_query = MagicMock()
        self.update.callback_query.answer = MagicMock()
        self.update.callback_query.edit_message_text = MagicMock()
        self.update.message = MagicMock()
        self.update.message.reply_text = MagicMock()

    @patch('main.database.get_users')
    async def test_send_valentine_menu(self, mock_get_users):
        mock_get_users.return_value = [(456, "user1"), (789, "user2")]

        await send_valentine_menu(self.update, self.context)

        self.update.callback_query.edit_message_text.assert_called_with("Выбери получателя:")

    @patch('main.database.save_valentine')
    async def test_handle_attached_image(self, mock_save_valentine):
        photo = MagicMock()
        photo.file_id = "photo_id"
        self.update.message.photo = [photo]
        self.context.user_data = {'receiver_id': 456, 'message': "Тестовое сообщение"}

        await handle_attached_image(self.update, self.context)

        mock_save_valentine.assert_called_with(123, 456, "Тестовое сообщение", "attached", "user_images/photo_id.jpg")

if __name__ == "__main__":
    unittest.main()