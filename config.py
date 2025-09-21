import os
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup

# Токен бота

# Загружаем переменные из .env
load_dotenv()

# Теперь получаем токен из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Настройки базы данных
DB_NAME = "prices.db"

# Настройки Ozon
OZON_URL = "https://www.ozon.ru/product/"

# Интервалы проверки (в секундах)
CHECK_INTERVALS = {
    'morning': 32400,  # 9:00 (9*3600)
    'evening': 64800   # 18:00 (18*3600)
}

# Логирование
LOG_LEVEL = "INFO"

# Клавиатура для главного меню
MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [['📦 Добавить еще товар']],
    resize_keyboard=True,
    one_time_keyboard=False  # Постоянно отображается
)

# Клавиатура для отмены
CANCEL_KEYBOARD = ReplyKeyboardMarkup(
    [['❌ Отменить']],
    resize_keyboard=True,
    one_time_keyboard=True
)
