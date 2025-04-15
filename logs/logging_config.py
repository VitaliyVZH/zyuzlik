import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logging():
    """Конфигурация системы логирования"""

    # Получаем путь к директории текущего файла
    base_dir = Path(__file__).parent.parent

    # Создаем путь к папке logs относительно расположения этого файла
    log_dir = base_dir / "logs"
    log_file = log_dir / "bot.log"

    # Создаем директорию если не существует
    log_dir.mkdir(exist_ok=True, parents=True)

    # Настраиваем обработчики
    handlers = [
        RotatingFileHandler(
            filename=log_file,
            maxBytes=5*1024*1024,  # 5 MB
            backupCount=3,
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ]

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
