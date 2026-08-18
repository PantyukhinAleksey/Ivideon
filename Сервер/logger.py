import logging
import logging.handlers
import sys


class AppLogger:
    """Настраивает вывод логов в консоль и во вращаемый файл, оба в UTF-8.

    На Windows консоль по умолчанию не в UTF-8, из-за чего кириллица
    в логах отображается искажённой - поэтому кодировка потоков
    переключается явно.
    """

    def __init__(self, name, log_path, max_bytes=1_000_000, backup_count=3):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')

        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        file_handler = logging.handlers.RotatingFileHandler(
            log_path, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8'
        )
        file_handler.setFormatter(formatter)

        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.INFO)
        self._logger.addHandler(console_handler)
        self._logger.addHandler(file_handler)

    def get(self):
        return self._logger
