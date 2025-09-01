# Ozon Price Tracker Bot

Telegram бот для отслеживания снижения цен на товары Ozon. Бот уведомляет пользователей, когда цена товара падает на заданный процент.

## 🚀 Возможности

- 📦 Отслеживание товаров по артикулу Ozon
- 🔔 Уведомления о снижении цены на заданный процент
- ⏰ Автоматическая проверка цен 2 раза в день
- 💾 Сохранение данных в SQLite базе данных
- 🎯 Простой и интуитивный интерфейс

## 🛠️ Технологии

- Python 3.9+
- python-telegram-bot - работа с Telegram API
- APScheduler - планировщик задач
- Requests - работа с HTTP запросами
- SQLite3 - база данных

## 📦 Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/kirst0ne/ozon-price-tracker-bot.git
cd ozon-price-tracker-bot
```

2. Создайте виртуальное окружение:
python -m venv .venv

3. Активируйте окружение
.\.venv\Scripts\activate

4. Установите зависимости:
pip install -r requirements.txt

5. Настройте бота:
Получите токен у @BotFather
Отредактируйте config.py:
BOT_TOKEN = "ВАШ_ТОКЕН_ЗДЕСЬ"

🚀 Запуск
python bot.py

📋 Использование:
1. Начните общение с ботом командой /start
2. Отправьте артикул товара с Ozon (только цифры)
3. Выберите желаемый процент снижения цены (5%, 10%, 15%, 20%+)
4. Бот будет проверять цену 2 раза в день и уведомит вас при достижении цели

🗂️ Структура проекта

ozon-price-tracker-bot/
├── bot.py              # Основной код бота
├── config.py           # Конфигурационные параметры
├── database.py         # Работа с базой данных
├── ozon_api.py         # API Ozon (парсинг)
├── scheduler.py        # Планировщик задач
├── requirements.txt    # Зависимости
├── .gitignore         # Игнорируемые файлы
└── README.md          # Документация


🤝 Contributing:

1. Форкните репозиторий 
2. Cоздайте ветку для вашей функции (git checkout -b feature/amazing-feature)
3. Закоммитьте изменения (git commit -m 'Add amazing feature')
4. Запушьте в ветку (git push origin feature/amazing-feature)
5. Откройте Pull Request

📝 Лицензия
Этот проект распространяется под лицензией MIT. См. файл LICENSE для подробностей.

📞 Контакты
Кирилл Селезнев - @Kirst0ne

Проект на GitHub: https://github.com/kirst0ne/ozon-price-tracker-bot
