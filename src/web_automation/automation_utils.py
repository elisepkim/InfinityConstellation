

import re
import asyncio
import logging
from typing import Callable, Awaitable

logger = logging.getLogger(__name__)


def is_valid_url(url: str) -> bool:
    """Simple URL validator."""
    regex = re.compile(
        r"^(https?:\/\/)?"  # http:// or https://
        r"([\da-z\.-]+)\.([a-z\.]{2,6})"  # domain
        r"([\/\w\.-]*)*\/?$",  # path
        re.IGNORECASE,
    )
    return re.match(regex, url) is not None


async def retry_async(
    func: Callable[[], Awaitable],
    retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """
    Retry an async function with exponential backoff.
    """
    attempt = 0
    while True:
        try:
            return await func()
        except exceptions as e:
            attempt += 1
            if attempt > retries:
                logger.error(f"Max retries reached. Last error: {e}")
                raise
            sleep_time = delay * (backoff ** (attempt - 1))
            logger.warning(f"Retry {attempt}/{retries} after error: {e}. Sleeping {sleep_time:.1f}s")
            await asyncio.sleep(sleep_time)


class AsyncRateLimiter:
    """
    Simple async rate limiter.
    Example: limiter = AsyncRateLimiter(max_rate=5, per_seconds=1)
    """
    def __init__(self, max_rate: int, per_seconds: float):
        self.max_rate = max_rate
        self.per_seconds = per_seconds
        self._tokens = max_rate
        self._lock = asyncio.Lock()
        self._last = asyncio.get_event_loop().time()

    async def acquire(self):
        async with self._lock:
            now = asyncio.get_event_loop().time()
            elapsed = now - self._last
            self._last = now
            self._tokens += elapsed * (self.max_rate / self.per_seconds)
            if self._tokens > self.max_rate:
                self._tokens = self.max_rate
            if self._tokens < 1:
                sleep_time = (1 - self._tokens) * (self.per_seconds / self.max_rate)
                await asyncio.sleep(sleep_time)
                self._tokens = 0
            else:
                self._tokens -= 1
