import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class OzonParser:
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        """Упрощенная настройка драйвера без неподдерживаемых опций"""
        try:
            options = uc.ChromeOptions()
            if self.headless:
                options.add_argument("--headless")

            # ✅ ТОЛЬКО БАЗОВЫЕ НАСТРОЙКИ которые поддерживает undetected-chromedriver
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")

            # ✅ Только основные stealth настройки
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-popup-blocking")

            # User-Agent
            options.add_argument(
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

            # ✅ ПРОСТОЙ запуск
            self.driver = uc.Chrome(options=options)

            # ✅ Настройки после запуска
            self.driver.set_window_size(1920, 1080)

            # Убираем признаки WebDriver
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            print("✅ Драйвер запущен с базовыми настройками!")

        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}")
            raise

    def accept_all_permissions(self):
        """Улучшенное принятие разрешений"""
        try:
            # Даем время на загрузку
            time.sleep(3)

            # Пробуем разные селекторы куки
            cookie_selectors = [
                "[data-widget='acceptCookie']",
                "button[aria-label*='cookie']",
                "button[aria-label*='Cookie']",
                ".cookie-button",
                ".accept-cookies",
                "button:contains('Принять')",
                "button:contains('принять')"
            ]

            for selector in cookie_selectors:
                try:
                    cookie_button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    if cookie_button.is_displayed():
                        cookie_button.click()
                        print("✅ Куки приняты")
                        time.sleep(1)
                        break
                except:
                    continue

        except Exception as e:
            print(f"ℹ️ Не нашли всплывающих окон: {e}")

    def get_product_price(self, article):
        """Парсит цену по конкретному классу"""
        try:
            url = f"https://www.ozon.ru/product/{article}/"
            print(f"🌐 Парсим товар: {article}")

            self.driver.get(url)

            # Сначала принимаем все разрешения
            self.accept_all_permissions()

            # Ждем загрузки страницы
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # ✅ Ищем ЦЕНУ по КОНКРЕТНОМУ КЛАССУ
            price_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".pdp_bf2.tsHeadline500Medium"))
            )

            price = price_element.text.strip()
            print(f"✅ Цена найдена: {price}")

            return {
                'price': price,
                'url': url,
                'article': article,
                'status': 'success'
            }

        except Exception as e:
            print(f"❌ Ошибка парсинга: {e}")

            # Сохраняем скриншот для анализа
            self.driver.save_screenshot(f"error_{article}.png")
            print(f"📸 Скриншот сохранен: error_{article}.png")

            return {
                'price': None,
                'url': url,
                'article': article,
                'status': 'error',
                'error': str(e)
            }

    def close(self):
        """Закрывает браузер"""
        if self.driver:
            self.driver.quit()
            print("✅ Браузер закрыт")
