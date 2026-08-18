import logging
import logging.handlers
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from logger import AppLogger


def test_app_logger_writes_to_console_and_file(tmp_path):
    log_path = tmp_path / 'client.log'

    logger = AppLogger('test.lantern.client', str(log_path)).get()
    logger.info('привет')

    for handler in logger.handlers:
        handler.flush()

    assert log_path.exists()
    assert 'привет' in log_path.read_text(encoding='utf-8')
    assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
    assert any(isinstance(h, logging.handlers.RotatingFileHandler) for h in logger.handlers)
