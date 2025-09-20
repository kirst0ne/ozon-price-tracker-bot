# test_debug.py
from ozon_parser import OzonParser
import time


def debug_parsing():
    """Дебаг парсинга"""
    parser = OzonParser(headless=False)

    try:
        article = "1831449152"
        print(f"🔍 Дебаг артикула: {article}")

        # Получаем страницу
        url = f"https://www.ozon.ru/product/{article}/"
        parser.driver.get(url)

        # Ждем и делаем скриншот
        time.sleep(5)
        parser.driver.save_screenshot("debug_page.png")
        print("📸 Скриншот сохранен: debug_page.png")

        # Сохраняем HTML
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(parser.driver.page_source)
        print("📄 HTML сохранен: debug_page.html")

        # Смотрим что на странице
        print("🔍 Анализируем страницу...")
        print(f"Заголовок: {parser.driver.title}")
        print(f"URL: {parser.driver.current_url}")

    finally:
        parser.close()


if __name__ == "__main__":
    debug_parsing()
