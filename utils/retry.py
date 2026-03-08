import functools
from typing import Any, Callable, TypeVar
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
from googleapiclient.errors import HttpError
from utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=Callable[..., Any])


def api_retry(func: T) -> T:
    """
    Decorator to provide exponential backoff for YouTube API calls.

    It retries up to 5 times with delays of 1s, 2s, 4s, 8s, and 16s.
    It specifically targets HttpErrors and network-related issues.

    Args:
        func: The API calling function to wrap.

    Returns:
        The decorated function with retry logic.
    """
    @functools.wraps(func)
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=20),
        retry=retry_if_exception_type((HttpError, ConnectionError, IOError)),
        before_sleep=before_sleep_log(logger, "INFO"),
        reraise=True
    )
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)

    return wrapper