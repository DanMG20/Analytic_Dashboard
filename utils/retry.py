import functools
import logging
from typing import Any, Callable, TypeVar

from googleapiclient.errors import HttpError
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=Callable[..., Any])


def api_retry(func: T) -> T:
    @functools.wraps(func)
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=20),
        retry=retry_if_exception_type((HttpError, ConnectionError, IOError)),
        before_sleep=before_sleep_log(logger, logging.INFO),
        reraise=True,
    )
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)

    return wrapper
