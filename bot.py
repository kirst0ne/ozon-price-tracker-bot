import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

from config import BOT_TOKEN
from database import init_db, add_user, add_tracked_product
from ozon_parser import OzonParser
import atexit

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния диалога
ARTICLE, PERCENT = range(2)

# ✅ СОЗДАЕМ ГЛОБАЛЬНЫЙ ЭКЗЕМПЛЯР ПАРСЕРА
parser = OzonParser(headless=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
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


async def process_product_info(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Сообщение о начале загрузки
    loading_message = await update.message.reply_text(
        "⏳ Ищу товар и его актуальную стоимость, пожалуйста подождите..."
    )

    """Получение процента скидки с парсингом цены"""
    percent_choice = update.message.text
    article = context.user_data.get('article', 'unknown')
    user_id = update.effective_user.id

    if percent_choice == '20%+':
        percent = 20
    else:
        percent = int(percent_choice.replace('%', ''))

    # ✅ ИСПОЛЬЗУЕМ ПАРСЕР ДЛЯ ПОЛУЧЕНИЯ ЦЕНЫ
    product_info = parser.get_product_price(article)

    # Обрабатываем результат парсинга
    if product_info['status'] != 'success':
        error_messages = {
            'error': f"❌ Не удалось получить цену для товара {article}",
            'not_found': f"❌ Товар {article} не найден"
        }

        message = error_messages.get(product_info['status'],
                                     f"❌ Ошибка при получении цены")

        await update.message.reply_text(
            f"{message}\n🔗 Проверьте ссылку: {product_info['url']}",
            reply_markup=None
        )
        return ConversationHandler.END

    # Извлекаем цену и чистим ее
    price_text = product_info['price']
    clean_price = price_text.replace('₽', '').replace(' ', '').strip()

    # Добавляем в БД
    add_tracked_product(
        user_id=user_id,
        article=article,
        target_percent=percent,
        current_price=clean_price,
        original_price=clean_price
    )

    # Отправляем подтверждение с РЕАЛЬНОЙ ценой
    await update.message.reply_text(
        f"🎯 Отслеживаю товар {article}\n"
        f"💰 Текущая цена: {product_info['price']}\n"
        f"📉 Жду снижение на: {percent}%\n"
        f"🔔 Уведомлю при достижении цели!\n\n"
        f"🔗 Ссылка: {product_info['url']}",
        reply_markup=None
    )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена диалога"""
    await update.message.reply_text('❌ Отменено')
    return ConversationHandler.END


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Ошибка: {context.error}")
    if update and update.message:
        await update.message.reply_text("😕 Произошла ошибка. Попробуйте позже.")


def main():
    """Основная функция"""
    # Инициализация БД
    init_db()

    application = Application.builder().token(BOT_TOKEN).build()

    # Настройка диалога
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ARTICLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_article)],
            PERCENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_product_info)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)

    print("Бот запущен...")
    application.run_polling()


if __name__ == '__main__':
    main()

# Регистрируем закрытие парсера при выходе
@atexit.register
def cleanup():
    print("🔄 Завершаем работу...")
    parser.close()
