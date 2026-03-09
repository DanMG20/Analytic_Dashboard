import logging
from utils.paths import data_path
from config import LOG_FILE

log_path = data_path(LOG_FILE)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%H:%M",
    handlers=[logging.FileHandler(log_path, encoding="utf-8"), logging.StreamHandler()],
)


def get_logger(name: str):
    return logging.getLogger(name)