
import asyncio
import logging
from typing import Optional, Dict, Any

from bs4 import BeautifulSoup

from src.web_automation.automation_utils import is_valid_url, retry_async, AsyncRateLimiter

logger = logging.getLogger(__name__)

# Optional: Playwright support if installed
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    import httpx
    PLAYWRIGHT_AVAILABLE = False


rate_limiter = AsyncRateLimiter(max_rate=5, per_seconds=1)


async def scrape_page(url: str, selector: Optional[str] = None, timeout: int = 10000) -> Dict[str, Any]:
    """
    Scrape a webpage. If Playwright is available, render JS. Otherwise, fallback to httpx.
    """
    if not is_valid_url(url):
        raise ValueError(f"Invalid URL: {url}")

    await rate_limiter.acquire()

    async def _scrape_playwright():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=timeout)
            html = await page.content()
            text = await page.inner_text(selector) if selector else None
            await browser.close()
            return {"url": url, "html": html, "text": text}

    async def _scrape_httpx():
        async with httpx.AsyncClient(timeout=timeout / 1000) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            html = resp.text
            soup = BeautifulSoup(html, "html.parser")
            text = None
            if selector:
                el = soup.select_one(selector)
                text = el.get_text(strip=True) if el else None
            return {"url": url, "html": html, "text": text}

    if PLAYWRIGHT_AVAILABLE:
        return await retry_async(_scrape_playwright, retries=2)
    else:
        return await retry_async(_scrape_httpx, retries=2)