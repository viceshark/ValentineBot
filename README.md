# Описание
 Бот позволяет пользователям анонимно отправлять валентинки зарегистрированным в боте пользователям.
 Валентинка = картинка + текст.
 Можно создать свою и отправить, либо можно получить готовую от бота.

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