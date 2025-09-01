import os

# Токен бота (замените на свой)
BOT_TOKEN = os.getenv("BOT_TOKEN", "8374939362:AAE2KNN21V02MuTo4UukLOGhPmuek-40dV0")

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
