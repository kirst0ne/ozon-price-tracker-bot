from ozon_parser import OzonParser
import time


def interactive_test():
    """Интерактивное тестирование парсера"""

    print("🎮 ИНТЕРАКТИВНЫЙ ТЕСТ Ozon ПАРСЕРА")
    print("=" * 50)
    print("Вводи артикулы товаров для проверки")
    print("Для выхода введите 'exit' или 'quit'")
    print("=" * 50)

    # Создаем парсер
    parser = OzonParser(headless=False)

    try:
        while True:
            # Запрашиваем артикул у пользователя
            article = input("\n🔍 Введите артикул товара: ").strip()

            # Проверяем на выход
            if article.lower() in ['exit', 'quit', 'q']:
                print("👋 Выход из теста...")
                break

            # Проверяем что введены цифры
            if not article.isdigit():
                print("❌ Артикул должен содержать только цифры!")
                continue

            print(f"\n🧪 Тестируем артикул: {article}")
            print("-" * 40)

            # Парсим цену
            start_time = time.time()
            result = parser.get_product_price(article)
            end_time = time.time()

            execution_time = end_time - start_time
            print(f"⏱️  Время выполнения: {execution_time:.2f} сек")
            print(f"🏷️  Статус: {result['status']}")

            if result['status'] == 'success':
                print(f"💰 Цена: {result['price']}")
                print(f"🔗 URL: {result['url']}")
                print("✅ УСПЕХ: Цена найдена!")

            elif result['status'] == 'not_found':
                print("❓ Цена не найдена на странице")
                print(f"🔗 URL: {result['url']}")

                # Предлагаем открыть для проверки
                open_browser = input("🌐 Открыть страницу для проверки? (y/n): ").strip().lower()
                if open_browser == 'y':
                    import webbrowser
                    webbrowser.open(result['url'])

            else:
                print(f"❌ ОШИБКА: {result.get('error', 'Unknown error')}")
                print(f"🔗 URL: {result['url']}")

            print("-" * 40)
            print("Готов к следующему артикулу...")

    except KeyboardInterrupt:
        print("\n\n👋 Прервано пользователем")
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")

    finally:
        # Закрываем браузер
        parser.close()
        print("\n✅ Парсер закрыт")


def quick_test():
    """Быстрый тест на примерах"""
    print("🚀 Быстрый тест на примерах")
    print("=" * 40)

    test_articles = [
        "187741885",  # Смартфон
        "293550246",  # Наушники
        "168367032",  # Книга
    ]

    parser = OzonParser(headless=False)

    try:
        for article in test_articles:
            print(f"\n🔍 Тестируем: {article}")
            result = parser.get_product_price(article)

            if result['status'] == 'success':
                print(f"✅ {result['price']}")
            else:
                print(f"❌ Ошибка: {result.get('error', 'Unknown')}")

            time.sleep(2)

    finally:
        parser.close()


if __name__ == "__main__":
    print("Выберите режим тестирования:")
    print("1 - Интерактивный режим (ввод артикулов)")
    print("2 - Быстрый тест (готовые примеры)")
    print("3 - Выход")

    choice = input("Ваш выбор (1-3): ").strip()

    if choice == "1":
        interactive_test()
    elif choice == "2":
        quick_test()
    elif choice == "3":
        print("👋 До свидания!")
    else:
        print("❌ Неверный выбор")
