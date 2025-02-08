# Описание
 Бот позволяет пользователям анонимно отправлять валентинки зарегестрированным в боте пользователям.
 Валентинка = картинка + текст. Можно выбрать дефолтную картинку(in progress) или приложить свою.

# Создание venv
- python -m venv .venv
- .venv\Scripts\activate

# Установка зависимостей
- pip install -r requirements.txt
- pip install pytest pytest-asyncio

# Указать токен бота
- в .env в BOT_TOKEN указать токен бота в телеграм

# Инициализация БД
- python database.py

# Запуск бота
- python main.py

# Запуск тестов
- pytest tests/