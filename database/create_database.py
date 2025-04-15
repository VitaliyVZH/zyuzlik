"""В модуле создаются таблицы."""
import sqlite3
from database.db_manager import Database
from logs.logging_config import setup_logging
import logging

logger = logging.getLogger(__name__)


def create_tables():
    """Создание всех таблиц."""
    try:
        with Database() as db:
            # Создаем таблицу через контекстный менеджер
            with db.connection:
                db.connection.execute('''
                    CREATE TABLE IF NOT EXISTS zyuzlik (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        url TEXT,
                        xpath TEXT
                    )''')

            logger.info("Все таблицы успешно созданы")

    except sqlite3.Error as e:
        logger.error(f"Ошибка базы данных: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.critical(f"Фатальная ошибка: {e}", exc_info=True)
        raise
