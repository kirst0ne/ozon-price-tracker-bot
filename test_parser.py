import random
from ozon_api import get_product_price


def generate_random_article(length=9):
    """Генерирует случайный артикул из цифр"""
    return ''.join(random.choice('0123456789') for _ in range(length))


def test_parser():
    """Тестируем парсер на случайных артикулах"""
    # Генерируем 5 случайных артикулов
    test_articles = [generate_random_article() for _ in range(5)]

    print("🔍 Тестируем парсер Ozon на случайных артикулах")
    print("=" * 60)

    for i, article in enumerate(test_articles, 1):
        result = get_product_price(article)

        print(f"{i}. Артикул: {article}")
        print(f"   Цена: {result['price']} руб")
        print(f"   Статус: {result['status']}")
        print(f"   Ссылка: {result['url']}")

        if result['status'] == 'success':
            print("   ✅ Успешный парсинг!")
        elif result['status'] == 'mock':
            print("   ⚠️ Демо-режим (парсинг заблокирован)")
        else:
            print(f"   ❌ Ошибка: {result['status']}")

        print("-" * 40)


if __name__ == "__main__":
    test_parser()
