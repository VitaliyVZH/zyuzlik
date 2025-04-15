import logging
import os
from pathlib import Path

import telebot
from telebot import types

from database.create_database import create_tables
from database.insert_data import insert_data_bd
from logs.logging_config import setup_logging
from pandas_dir.panda_file_riter import get_data_file
from parsers.parser_onlinetrade import parser_online_trade
from text_handler import get_text

logger = logging.getLogger(__name__)
setup_logging()


def handler_excel_document(bot):
    @bot.message_handler(content_types=['document'])
    def get_dokument(message: types.Message):
        """Обработка загруженных Excel-файлов."""
        # Проверка расширения файла
        if not message.document.file_name.endswith(('.xlsx',)):
            bot.send_message(
                message.chat.id,
                "Неправильный формат файла. Требуется .xlsx"
            )
            return  # Прерываем выполнение

        # Скачивание файла
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Сохранение файла
        download_dir = os.path.join(Path(__file__).parent.parent.parent, 'downloads')
        os.makedirs(download_dir, exist_ok=True)
        file_path = os.path.join(download_dir, message.document.file_name)

        try:
            with open(file_path, 'wb') as new_file:
                new_file.write(downloaded_file)
            logger.info(f"Файл успешно сохранен: {file_path}")

            # Обработка данных
            data = get_data_file(file_path)  # Используйте file_path для получения данных
            text = get_text(data)
            insert_data_bd(data)
            bot.reply_to(message, f"Файл сохранен!\n\n{text}")
            bot.send_message(message.chat.id, "Сейчас проанализирую стоимость телефонов на www.onlinetrade.ru\n"
                                              "Подождите немного")
            data_parser_online_trade = parser_online_trade()
            average_cost_phone = round(data_parser_online_trade['total_price'] / data_parser_online_trade['total_products'], 2)
            bot.send_message(message.chat.id,
                             f"Данные с парсинга страницы:\n"
                             f"Общее кол-во телефонов этой марки: {data_parser_online_trade['total_products']}\n"
                             f"Средняя стоимость телефона {average_cost_phone}")
        except Exception as e:
            logger.error(f"Ошибка: {str(e)}")
            bot.reply_to(message, f"Ошибка: {str(e)}")

    @bot.message_handler(content_types=["text"])
    def handler_some_text(message: types.Message):
        """Обработка текстовых сообщений."""
        bot.send_message(
            message.chat.id,
            "Пожалуйста, загрузите файл в формате Excel (.xlsx)"
        )

    @bot.message_handler(commands=['start'])
    def handler_start(message: telebot.types.Message) -> None:
        """
        Обработчик команды /start.
        Отправляет приветственное сообщение и инструкции.
        """

        try:
            logger.info(f"Новый пользователь: {message.from_user.id}")
            bot.send_message(
                message.chat.id,
                "Загрузите Excel-файл в формате .xlsx\n"
                "Убедитесь, что файл содержит колонки:\n"
                "- title\n- url\n- xpath"
            )
        except Exception as exp:
            logger.error(f"Ошибка в обработчике /start: {str(exp)}", exc_info=True)
            bot.send_message(
                message.chat.id,
                "Произошла внутренняя ошибка. Попробуйте позже."
            )