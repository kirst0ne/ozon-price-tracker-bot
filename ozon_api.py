import logging
import requests
import time
import random
import re
from bs4 import BeautifulSoup
from config import OZON_URL

logger = logging.getLogger(__name__)


def get_ozon_price(article):
    """
    Парсим цену товара с Ozon с соблюдением правил
    """
    try:
        url = f"{OZON_URL}{article}/"

        # Вежливые заголовки (имитируем реальный браузер)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }

        # Случайная задержка (1-3 секунды)
        time.sleep(random.uniform(1.0, 3.0))

        # Отправляем запрос
        response = requests.get(url, headers=headers, timeout=15)
        # Проверяем 403 ошибку явно
        if response.status_code == 403:
            logger.warning(f"Ozon заблокировал доступ для артикула {article} (403 Forbidden)")
            return {
                'price': None,
                'url': url,
                'article': article,
                'status': 'blocked'
            }
        # raise_for_status - это метод объекта Response из библиотеки requests;
        # он проверяет HTTP-статус ответа и выбрасывает исключение HTTPError, если статус —
        # ошибка (4xx или 5xx). Если статус успешный (2xx), он ничего не делает.
        response.raise_for_status()

        # Проверяем что это не капча или блокировка
        if "captcha" in response.text.lower() or "доступ ограничен" in response.text.lower():
            logger.warning(f"Обнаружена капча или блокировка для артикула {article}")
            return {
                'price': None,
                'url': url,
                'article': article,
                'status': 'blocked'
            }

        soup = BeautifulSoup(response.text, 'html.parser')

        # Метод 1: Ищем в JSON-LD данных (самый надежный)
        price = parse_json_ld_price(soup, article)
        if price:
            return build_success_response(price, url, article)

        # Метод 2: Ищем в meta-тегах
        price = parse_meta_price(soup, article)
        if price:
            return build_success_response(price, url, article)

        # Метод 3: Ищем по CSS-селекторам
        price = parse_css_price(soup, article)
        if price:
            return build_success_response(price, url, article)

        # Метод 4: Ищем регулярными выражениями
        price = parse_regex_price(response.text, article)
        if price:
            return build_success_response(price, url, article)

        logger.warning(f"Цена не найдена для артикула {article}")
        return {
            'price': None,
            'url': url,
            'article': article,
            'status': 'not_found'
        }

    except Exception as e:
        logger.error(f"Ошибка парсинга артикула {article}: {str(e)}")
        return {
            'price': None,
            'url': f"{OZON_URL}{article}/",
            'article': article,
            'status': 'error'
        }


def parse_json_ld_price(soup, article):
    """Парсим цену из JSON-LD данных"""
    try:
        script = soup.find('script', type='application/ld+json')
        if script:
            import json
            data = json.loads(script.string)
            # Ищем цену в различных структурах JSON-LD
            if data.get('offers') and data['offers'].get('price'):
                return data['offers']['price']
            elif data.get('price'):
                return data['price']
    except:
        pass
    return None


def parse_meta_price(soup, article):
    """Парсим цену из meta-тегов"""
    meta_selectors = [
        'meta[property="product:price:amount"]',
        'meta[itemprop="price"]',
        'meta[name="price"]'
    ]

    for selector in meta_selectors:
        meta = soup.select_one(selector)
        if meta and meta.get('content'):
            price = meta['content'].replace('₽', '').replace(' ', '').strip()
            if price.isdigit():
                return int(price)
    return None


def parse_css_price(soup, article):
    """Парсим цену по CSS-селекторам"""
    # Селекторы для поиска цены
    css_selectors = [
        '[data-widget="webPrice"]',
        '.yo6', '.y9o',  # Ozon селекторы
        '.price', '.product-price', '.item-price',
        '.c3118-a0', '.ui9',  # Другие возможные селекторы Ozon
        '[data-price]',  # Элементы с data-price атрибутом
        '.a3l9-a0',  # Еще один возможный селектор
        '.tsHeadline500Large'  # Селектор для крупного текста (может быть ценой)
    ]

    # Также проверяем атрибуты data-price у различных элементов
    data_price_selectors = [
        'div[data-price]',
        'span[data-price]',
        'p[data-price]',
        '[itemprop="price"]'
    ]

    # Проверяем обычные селекторы
    for selector in css_selectors:
        try:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                price = re.sub(r'[^\d]', '', price_text)
                if price and price.isdigit():
                    return int(price)
        except:
            continue

    # Проверяем элементы с data-price атрибутами
    for selector in data_price_selectors:
        try:
            element = soup.select_one(selector)
            if element and element.get('data-price'):
                price = element.get('data-price').replace(' ', '')
                if price.isdigit():
                    return int(price)
        except:
            continue

    return None


def parse_regex_price(html, article):
    """Парсим цену регулярными выражениями"""
    patterns = [
        r'"price":["\']?(\d+)["\']?',
        r'price["\']?\s*:\s*["\']?(\d+)["\']?',
        r'₽\s*(\d[\d\s]*)',  # Рубли с пробелами
        r'priceAmount["\']?\s*:\s*["\']?(\d+)["\']?',
    ]

    for pattern in patterns:
        matches = re.search(pattern, html)
        if matches:
            price = matches.group(1).replace(' ', '')
            if price.isdigit():
                return int(price)
    return None


def build_success_response(price, url, article):
    """Строим успешный ответ"""
    logger.info(f"Успешно получили цену для артикула {article}: {price} руб")
    return {
        'price': price,
        'url': url,
        'article': article,
        'status': 'success'
    }


def get_product_price(article):
    """
    Основная функция для получения цены
    С fallback на mock если парсинг не работает
    """
    # Пробуем спарсить реальную цену
    result = get_ozon_price(article)

    # Если не получилось - используем реалистичную заглушку
    if result['status'] != 'success':
        result = get_product_price_mock(article)

    return result


def get_product_price_mock(article):
    """
    Реалистичная заглушка для демонстрации
    """
    base_price = 1000 + (hash(article) % 9000)
    price = base_price - (base_price % 100)  # Округляем до сотен

    logger.info(f"Используем mock цену для артикула {article}: {price} руб")

    return {
        'price': price,
        'url': f"{OZON_URL}{article}/",
        'article': article,
        'status': 'mock'
    }
