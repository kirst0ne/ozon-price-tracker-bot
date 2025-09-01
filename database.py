import sqlite3
import logging
from config import DB_NAME

logger = logging.getLogger(__name__)


def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Таблица отслеживаемых товаров
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tracked_products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        article TEXT,
        target_percent INTEGER,
        current_price REAL,
        original_price REAL,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')

    conn.commit()
    conn.close()
    logger.info("Database initialized")


def add_user(user_id, username, first_name, last_name):
    """Добавление пользователя в БД"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
    VALUES (?, ?, ?, ?)
    ''', (user_id, username, first_name, last_name))

    conn.commit()
    conn.close()


def add_tracked_product(user_id, article, target_percent):
    """Добавление товара для отслеживания"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO tracked_products (user_id, article, target_percent)
    VALUES (?, ?, ?)
    ''', (user_id, article, target_percent))

    conn.commit()
    conn.close()
