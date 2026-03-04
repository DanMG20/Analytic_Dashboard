import logging
from pathlib import Path
from utils.paths import data_path



LOG_FILE = data_path("dashboard.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%H:%M",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"), logging.StreamHandler()],
)


def get_logger(name: str):
    return logging.getLogger(name)