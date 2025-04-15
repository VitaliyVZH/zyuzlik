import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException, TimeoutException
from bs4 import BeautifulSoup
import random
import time

from logs.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def get_realistic_user_agent():
    """Генерация рандомного User-Agent"""
    chrome_versions = [120, 121, 122, 123]
    return (
        f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        f"AppleWebKit/537.36 (KHTML, like Gecko) "
        f"Chrome/{random.choice(chrome_versions)}.0.0.0 Safari/537.36"
    )


def human_like_delay(min_d=0.5, max_d=3.0):
    """Случайная задержка с логированием"""
    delay = random.uniform(min_d, max_d)
    logger.debug(f"Задержка: {delay:.2f} сек")
    time.sleep(delay)


def configure_chrome_options(headless=True):
    """Конфигурация браузера с антидетектом"""
    chrome_options = Options()

    try:
        chrome_options.add_argument(f"user-agent={get_realistic_user_agent()}")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--lang=ru-RU")

        if headless:
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-gpu")

        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        return chrome_options
    except Exception as e:
        logger.error(f"Ошибка конфигурации: {str(e)}")
        raise


def human_like_interaction(driver):
    """Упрощенная имитация поведения"""
    try:
        # Плавная прокрутка
        for _ in range(2):
            driver.execute_script("window.scrollBy(0, window.innerHeight/2)")
            human_like_delay(0.5, 1.5)
            driver.execute_script("window.scrollBy(0, -window.innerHeight/4)")
            human_like_delay(0.3, 0.7)

        # Клик по телу страницы
        body = driver.find_element(By.TAG_NAME, 'body')
        ActionChains(driver).move_to_element(body).click().perform()
        human_like_delay(0.2, 0.5)

    except Exception as e:
        logger.warning(f"Ошибка взаимодействия: {str(e)}")


def get_bs4_with_selenium(url: str) -> BeautifulSoup:
    """
    Загружает веб-страницу по указанному URL с помощью Selenium, ожидает исчезновения спиннера и загрузки основного контента,
    имитирует поведение пользователя (скроллинг), и возвращает объект BeautifulSoup для дальнейшего парсинга.

    Параметры:
       url (str): URL страницы для загрузки и парсинга.

    Возвращает:
       BeautifulSoup: Объект BeautifulSoup, содержащий HTML-код загруженной страницы.

    Исключения:
       WebDriverException: Если основной контейнер контента не найден.
       TimeoutException: Если спиннер не исчезает в течение заданного времени.
       Exception: При других критических ошибках во время загрузки или парсинга.
    """

    driver = None
    try:
        # 1. Инициализация драйвера с ручным управлением параметрами
        chrome_options = configure_chrome_options()
        chrome_options.add_argument("--disable-site-isolation-trials")  # Добавляем экспериментальный параметр
        driver = webdriver.Chrome(options=chrome_options)

        # 2. Улучшенная маскировка WebDriver
        driver.execute_cdp_cmd("Network.setUserAgentOverride", {
            "userAgent": get_realistic_user_agent() + " " + str(random.randint(1000, 9999))
        })

        # 3. Загрузка страницы с обработкой таймаутов
        driver.set_page_load_timeout(45)
        try:
            driver.get(url)
        except TimeoutException:
            logger.warning("Частичная загрузка страницы - продолжаем обработку")

        # 4. Комбинированное ожидание спиннера
        try:
            WebDriverWait(driver, 30).until(
                lambda d: not d.find_elements(By.CSS_SELECTOR, ".spinner, .load, [class*='loading'], [id*='loader']")
            )
            logger.info("Спиннер/лоадер успешно скрыт")
        except TimeoutException:
            logger.error("Спиннер не исчез в течение 30 секунд")
            raise

        # 5. Явная проверка загрузки контента
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".indexGoods__item"))
        )
        logger.info("Основной контент подтвержден")

        # 6. Оптимизированная имитация поведения
        for _ in range(2):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight*0.7)")
            time.sleep(random.uniform(0.5, 1.2))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight*0.3)")
            time.sleep(random.uniform(0.3, 0.7))

        # 7. Финальная проверка
        if "container" not in driver.page_source:
            raise WebDriverException("Контейнер контента не обнаружен")

        return BeautifulSoup(driver.page_source, 'lxml')

    except Exception as e:
        driver.save_screenshot(f'error_{datetime.now().strftime("%H%M%S")}.png')
        logger.error(f"Критическая ошибка: {str(e)}")
        raise
    finally:
        if driver:
            driver.quit()
