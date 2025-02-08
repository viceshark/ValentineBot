import sqlite3
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    try:
        conn = sqlite3.connect("valentine_bot.db")
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                        (user_id INTEGER PRIMARY KEY, username TEXT, registration_date TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS valentines 
                        (valentine_id INTEGER PRIMARY KEY, sender_id INTEGER, receiver_id INTEGER, 
                        message TEXT, image_type TEXT, image_path TEXT, sent_at TEXT)''')
        conn.commit()
        conn.close()
        logger.info("База данных успешно инициализирована.")
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")

def register_user(user_id, username):
    try:
        conn = sqlite3.connect("valentine_bot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        existing_user = cursor.fetchone()
        #TODO: не выводить юзеру, писать только в лог
        if existing_user:
            raise ValueError("Вы уже зарегистрированы!")
        cursor.execute("INSERT INTO users (user_id, username, registration_date) VALUES (?, ?, ?)",
                       (user_id, username, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        logger.info(f"Пользователь {username} успешно зарегистрирован.")
    except Exception as e:
        logger.error(f"Ошибка при регистрации пользователя: {e}")
        raise

def get_users():
    try:
        conn = sqlite3.connect("valentine_bot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, username FROM users")
        users = cursor.fetchall()
        conn.close()
        return users
    except Exception as e:
        logger.error(f"Ошибка при получении пользователей: {e}")
        return []

def save_valentine(sender_id, receiver_id, message, image_type, image_path):
    try:
        conn = sqlite3.connect("valentine_bot.db")
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO valentines 
                        (sender_id, receiver_id, message, image_type, image_path, sent_at)
                        VALUES (?, ?, ?, ?, ?, datetime('now'))''',
                       (sender_id, receiver_id, message, image_type, image_path))
        conn.commit()
        conn.close()
        logger.info("Валентинка успешно сохранена.")
    except Exception as e:
        logger.error(f"Ошибка при сохранении валентинки: {e}")

def get_username_by_id(user_id):
    try:
        conn = sqlite3.connect("valentine_bot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        if user:
            return user[0]
        else:
            return "Неизвестный пользователь"
    except Exception as e:
        logger.error(f"Ошибка при получении имени пользователя: {e}")
        return "Неизвестный пользователь"