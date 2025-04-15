"""
Основной модуль Telegram-бота для обработки Excel-файлов.
Обеспечивает прием файлов, их валидацию и возврат структурированных данных.
"""

import os
import logging
import telebot
from dotenv import load_dotenv
from handlers.handler_document import handler_excel_document
from logs.logging_config import setup_logging


logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("TOKEN_BOT")

if not TOKEN:
    logger.critical("Токен бота не найден! Проверьте .env файл")
    raise ValueError("Токен бота не найден в переменных окружения")

bot = telebot.TeleBot(TOKEN)


def main() -> None:
    """Основная функция запуска бота."""
    try:
        logger.info("Запуск бота")
        handler_excel_document(bot)
        logger.info("Бот успешно запущен")
        bot.polling(none_stop=True, interval=2)
    except Exception as e:
        logger.critical(f"Критическая ошибка: {str(e)}", exc_info=True)
    finally:
        logger.info("Работа бота завершена")


if __name__ == '__main__':
    setup_logging()
    main()
