from selenium import webdriver
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
        try:
            options = webdriver.ChromeOptions()
            if self.headless:
                options.add_argument("--headless=new")

            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-popup-blocking")
            options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")

            # ✅ САМЫЙ ПРОСТОЙ ВАРИАНТ - webdriver_manager сам всё сделает
            self.driver = webdriver.Chrome(options=options)

            print("✅ Драйвер запущен!")

        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}")
            raise

    # Остальные методы (get_product_price, accept_all_permissions) остаются те же!

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
        """Парсит цену товара"""
        try:
            url = f"https://www.ozon.ru/product/{article}/"
            print(f"🌐 Парсим товар: {article}")

            self.driver.get(url)
            self.accept_all_permissions()

            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Список приоритетных селекторов
            price_selectors = [
                (".pdp_bf2.tsHeadline500Medium", "Основной селектор"),
                (".pdp_bf2.tsHeadline600Large", "Альтернативный селектор"),
            ]

            price = None
            used_selector = None

            for selector, description in price_selectors:
                try:
                    # Пробуем найти элемент
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed():
                        candidate_price = element.text.strip()
                        # Проверяем что это похоже на цену (содержит цифры)
                        if candidate_price and any(c.isdigit() for c in candidate_price):
                            price = candidate_price
                            used_selector = description
                            print(f"✅ Цена найдена через {description}: {price}")
                            break
                except:
                    continue

            if not price:
                print("❌ Цена не найдена ни одним методом")
                return {
                    'price': None,
                    'url': url,
                    'article': article,
                    'status': 'not_found'
                }

            return {
                'price': price,
                'url': url,
                'article': article,
                'status': 'success',
                'selector': used_selector  # Для отладки
            }

        except Exception as e:
            print(f"❌ Общая ошибка парсинга: {e}")
            return {
                'price': None,
                'url': f"https://www.ozon.ru/product/{article}/",
                'article': article,
                'status': 'error',
                'error': str(e)
            }

    def close(self):
        """Закрывает браузер"""
        if self.driver:
            self.driver.quit()
            print("✅ Браузер закрыт")
