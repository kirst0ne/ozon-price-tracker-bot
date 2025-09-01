import logging
import random
from config import OZON_URL

logger = logging.getLogger(__name__)


def get_product_price(article):
    """
    Заглушка для получения цены товара
    Позже заменим на реальный API Ozon
    """
    # Имитация получения цены
    price = random.randint(1000, 10000)
    product_url = f"{OZON_URL}{article}/"

    logger.info(f"Got price for article {article}: {price} rub")

    return {
        'price': price,
        'url': product_url,
        'article': article
    }
