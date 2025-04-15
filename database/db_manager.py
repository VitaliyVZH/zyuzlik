import sqlite3
import logging
import os

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_name="task.db"):
        """Инициализация объекта базы данных."""
        self.db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            db_name
        )
        self.connection = None
        logger.debug(f"Инициализирован экземпляр Database. Путь к БД: {self.db_path}")

    def connect(self):
        """Установка соединения с базой данных."""
        try:
            # Закрываем предыдущее соединение, если оно есть
            if self.connection:
                self.close()

            logger.info(f"Попытка подключения к БД: {self.db_path}")
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            logger.info("Подключение успешно установлено")

            # Проверяем, была ли создана новая БД
            if not os.path.exists(self.db_path):
                logger.info("Создана новая база данных")
                os.sync()  # Гарантируем запись на диск

            return self

        except sqlite3.Error as e:
            logger.critical("Ошибка подключения", exc_info=True)
            raise RuntimeError(f"Connection error: {str(e)}") from e

    def close(self):
        """Безопасное закрытие соединения."""
        if self.connection:
            try:
                self.connection.close()
                logger.debug("Соединение закрыто")
                self.connection = None
            except sqlite3.Error as e:
                logger.error("Ошибка закрытия", exc_info=True)
                raise
        else:
            logger.debug("Соединение уже закрыто")

    def __enter__(self):
        """Контекстный менеджер должен возвращать self"""
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Гарантированное закрытие соединения"""
        self.close()
        if exc_type:
            logger.error("Ошибка в контексте", exc_info=True)
        return False  # Не подавлять исключения

    @property
    def cursor(self):
        """Получение курсора с проверкой соединения"""
        if not self.connection:
            raise RuntimeError("Соединение не установлено")
        return self.connection.cursor()

    def execute(self, query, params=None):
        """Упрощенный метод выполнения запросов"""
        with self.connection:
            return self.cursor.execute(query, params or ())
