import unittest
from unittest.mock import MagicMock, patch
from handlers import start

class TestStartCommand(unittest.TestCase):
    def setUp(self):
        self.update = MagicMock()
        self.context = MagicMock()
        self.update.effective_user = MagicMock()
        self.update.effective_user.id = 123
        self.update.effective_user.first_name = "Иван"
        self.update.effective_user.username = "ivan"
        self.update.message = MagicMock()
        self.update.message.reply_text = MagicMock()

    @patch('main.database.register_user')
    async def test_start_command(self, mock_register_user):
        await start(self.update, self.context)

        self.update.message.reply_text.assert_called_with("🎉 Привет, Иван! Я Вики - бот для отправки валентинок команды Pegasus.")

        mock_register_user.assert_called_with(123, "ivan")

if __name__ == "__main__":
    unittest.main()