from core.constant import BASE_DIR
import os
import sys
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(app_name: str = "app"):

    _logger = logging.getLogger(app_name)
    _logger.setLevel(logging.DEBUG)
    _logger.propagate = False

    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(console_format)
    _logger.addHandler(console_handler)

    # Create a file handler
    dir_log = os.path.join(BASE_DIR, "logs")

    if not os.path.exists(dir_log):
        os.makedirs(dir_log)

    file_handler = RotatingFileHandler(os.path.join(dir_log, f"{app_name}.log"), maxBytes=1024 * 1024 * 20, backupCount=3, encoding='utf-8', mode="a")
    file_handler.setLevel(logging.ERROR)
    file_format = logging.Formatter('%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(file_format)
    _logger.addHandler(file_handler)

    return _logger


logger = setup_logger(app_name="Ads-Browser-View")