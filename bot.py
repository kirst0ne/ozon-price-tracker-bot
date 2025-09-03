import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

from config import BOT_TOKEN
from database import init_db, add_user, add_tracked_product
from ozon_api import get_product_price

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния диалога
ARTICLE, PERCENT = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user

    # Добавляем пользователя в БД
    add_user(user.id, user.username, user.first_name, user.last_name)

    await update.message.reply_text(
        "👋 Привет! Я бот для отслеживания цен на Ozon!\n\n"
        "📦 Пришли мне артикул товара (только цифры)"
    )
    return ARTICLE


async def get_article(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение артикула от пользователя"""
    user_input = update.message.text.strip()

    if not user_input.isdigit():
        await update.message.reply_text("❌ Пожалуйста, пришлите только цифры артикула")
        return ARTICLE

    context.user_data['article'] = user_input
    logger.info(f"User {update.effective_user.id} entered article: {user_input}")

    keyboard = [['5%', '10%', '15%', '20%+']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text(
        f"✅ Артикул {user_input} принят!\n\n"
        "📉 На сколько процентов должен подешеветь товар?",
        reply_markup=reply_markup
    )
    return PERCENT


async def get_percent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение процента скидки"""
    percent_choice = update.message.text
    article = context.user_data.get('article', 'unknown')
    user_id = update.effective_user.id
    product_info = get_product_price(article)

    if product_info['status'] != 'success':
        error_messages = {
            'blocked': "❌ Ozon временно ограничил доступ. Попробуйте позже",
            'not_found': f"❌ Товар с артикулом {article} не найден",
            'error': "❌ Ошибка при получении цены",
            'mock': "⚠️ Используем демо-цену (режим тестирования)"
        }

        status = product_info['status']
        message = error_messages.get(status, "❌ Неизвестная ошибка")

        if status == 'mock':
            # Для mock режима все равно показываем "цену"
            message += f"\n💰 Демо-цена: {product_info['price']} руб"

        await update.message.reply_text(
            f"{message}\n🔗 Ссылка: {product_info['url']}",
            reply_markup=None
        )

        # Для mock режима продолжаем работу
        if status != 'mock':
            return ConversationHandler.END

    if percent_choice == '20%+':
        percent = 20
    else:
        percent = int(percent_choice.replace('%', ''))

    # Получаем текущую цену (заглушка)
    product_info = get_product_price(article)

    # Добавляем в БД
    add_tracked_product(user_id, article, percent)

    await update.message.reply_text(
        f"🎯 Отслеживаю товар {article}\n"
        f"💰 Текущая цена: {product_info['price']} руб\n"
        f"📉 Жду снижение на: {percent}%\n"
        f"🔔 Уведомлю при достижении цели!\n\n"
        f"🔗 Ссылка: {product_info['url']}",
        reply_markup=None
    )

    return ConversationHandler.END


def main():
    """Основная функция"""
    # Инициализация БД
    init_db()

    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ARTICLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_article)],
            PERCENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_percent)],
        },
        fallbacks=[CommandHandler('cancel', lambda u, c: u.message.reply_text('❌ Отменено'))],
    )

    application.add_handler(conv_handler)

    print("Бот запущен...")
    application.run_polling()


if __name__ == '__main__':
    main()
