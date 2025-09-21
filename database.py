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


def add_tracked_product(user_id, article, target_percent, current_price, original_price):
    """Добавляет товар для отслеживания с ценами"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO tracked_products (user_id, article, target_percent, current_price, original_price)
    VALUES (?, ?, ?, ?, ?)
    ''', (user_id, article, target_percent, current_price, original_price))

    conn.commit()
    conn.close()
    logger.info(f"Added tracked product: {article} for user {user_id}")


def update_product_price(article, new_price):
    """Обновляет текущую цену товара"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE tracked_products 
    SET current_price = ?
    WHERE article = ? AND is_active = TRUE
    ''', (new_price, article))

    conn.commit()
    conn.close()
    logger.info(f"Updated price for {article}: {new_price}")


def get_tracked_products():
    """Получает все активные отслеживаемые товары"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, user_id, article, target_percent, current_price, original_price
    FROM tracked_products 
    WHERE is_active = TRUE
    ''')

    products = cursor.fetchall()
    conn.close()
    return products


def check_price_drop(article, new_price):
    """Проверяет достигнуто ли целевое снижение цены"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT original_price, target_percent 
    FROM tracked_products 
    WHERE article = ? AND is_active = TRUE
    ''', (article,))

    result = cursor.fetchone()
    conn.close()

    if result:
        original_price, target_percent = result
        if original_price and new_price:
            # Конвертируем в числа для вычислений
            original = float(original_price)
            current = float(new_price)

            # Вычисляем процент снижения
            price_drop = ((original - current) / original) * 100
            logger.info(f"Price drop for {article}: {price_drop:.2f}% (target: {target_percent}%)")

            return price_drop >= target_percent

    return False


def user_exists(user_id):
    """Проверяет существует ли пользователь в БД"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
    exists = cursor.fetchone() is not None

    conn.close()
    return exists
