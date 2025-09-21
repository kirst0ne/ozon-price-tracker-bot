import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, \
    ConversationHandler
from config import BOT_TOKEN, MAIN_KEYBOARD
from database import init_db, add_user, update_user, add_tracked_product, user_exists
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
    """Персонализированный обработчик команды /start"""
    user = update.effective_user

    # Проверяем, что юзер возвращающийся
    is_new_user = not user_exists(user.id)

    if is_new_user:
        # Добавляем нового пользователя
        add_user(user.id, user.username, user.first_name, user.last_name)
        greeting = (
            f"👋 Привет, {user.first_name}! Я бот для отслеживания цен на Ozon!\n\n"
            "📦 Я помогу тебе следить за снижением цен на товары.\n"
            "Просто пришли мне артикул товара (только цифры)"
        )
    else:
        # Персонализированное приветствие для возвращающегося
        update_user(user.id, user.username, user.first_name, user.last_name)
        greeting = (
            f"📦 Снова хотите добавить товар, {user.first_name}?\n\n"
            "Пришлите артикул товара (только цифры)"
        )

    await update.message.reply_text(
        greeting,
        reply_markup=MAIN_KEYBOARD
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


async def process_product_tracking(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Сообщение о начале загрузки
    loading_message = await update.message.reply_text(
        "⏳ Ищу товар и его актуальную стоимость, пожалуйста подождите...",
    )
    reply_markup = ReplyKeyboardRemove()

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

    # Редактируем сообщение с REPLAY клавиатурой
    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=loading_message.message_id,
        text=(
            f"✅ Товар успешно добавлен для отслеживания!\n\n"
            f"🎯 Отслеживаю товар {article}\n"
            f"💰 Текущая цена: {product_info['price']}\n"
            f"📉 Жду снижение на: {percent}%\n"
            f"🔔 Уведомлю при достижении цели!\n\n"
            f"🔗 Ссылка: {product_info['url']}"
        )
    )

    await update.message.reply_text(
        f"🚀 Сообщим Вам, как только товар подешевеет на {percent}%",
        reply_markup=MAIN_KEYBOARD
    )

    return ConversationHandler.END


async def add_another_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки 'Добавить еще товар'"""
    user = update.effective_user

    await update.message.reply_text(
        f"📦 Отлично, {user.first_name}! Пришлите артикул нового товара (только цифры)",
        reply_markup=ReplyKeyboardRemove()  # Убираем клавиатуру для ввода
    )
    return ARTICLE


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена диалога с возвратом к главной клавиатуре"""
    await update.message.reply_text(
        '❌ Отменено. Что хотите сделать?',
        reply_markup=MAIN_KEYBOARD  # ✅ Возвращаем главную клавиатуру
    )
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
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(filters.Text(['📦 Добавить еще товар']), add_another_product)
        ],
        states={
            ARTICLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_article)],
            PERCENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_product_tracking)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )

    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)

    print("Бот запущен с интерактивной клавиатурой...")
    application.run_polling()


if __name__ == '__main__':
    main()

# Регистрируем закрытие парсера при выходе
@atexit.register
def cleanup():
    print("🔄 Завершаем работу...")
    parser.close()
