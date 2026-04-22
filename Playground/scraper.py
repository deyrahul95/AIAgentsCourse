import asyncio
import time
from typing import Optional
from urllib.parse import urlparse
import aiohttp
import async_timeout
from aiohttp import ClientResponseError
from bs4 import BeautifulSoup
import urllib.robotparser

DEFAULT_USER_AGENT = "my-async-scraper/1.0 (+https://example.com)"
DEFAULT_TIMEOUT = 10
DEFAULT_RETRIES = 3
DEFAULT_BACKOFF = 0.5
MIN_REQUEST_INTERVAL = 1.0  # seconds per host

_last_request_time_by_host: dict[str, float] = {}

def _get_host(url: str) -> str:
    return urlparse(url).netloc.lower()

async def _respect_rate_limit(host: str) -> None:
    last = _last_request_time_by_host.get(host)
    if last:
        elapsed = time.time() - last
        if elapsed < MIN_REQUEST_INTERVAL:
            await asyncio.sleep(MIN_REQUEST_INTERVAL - elapsed)
    _last_request_time_by_host[host] = time.time()

def _is_allowed_by_robots(url: str, user_agent: str) -> bool:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception:
        return True

def _extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "iframe"]):
        tag.decompose()
    lines = [line.strip() for line in soup.get_text("\n", strip=True).splitlines() if line.strip()]
    return "\n".join(lines)

async def fetch_page_content(
    url: str,
    *,
    user_agent: str = DEFAULT_USER_AGENT,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
    backoff: float = DEFAULT_BACKOFF,
    parse_html: bool = True,
    respect_robots: bool = True,
    session: Optional[aiohttp.ClientSession] = None,
) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("Invalid URL: must be absolute http(s) URL")

    if respect_robots and not _is_allowed_by_robots(url, user_agent):
        raise PermissionError("Disallowed by robots.txt")

    host = _get_host(url)
    await _respect_rate_limit(host)

    own_session = False
    if session is None:
        session = aiohttp.ClientSession(headers={"User-Agent": user_agent, "Accept": "text/html"})
        own_session = True

    try:
        attempt = 0
        while True:
            try:
                attempt += 1
                async with async_timeout.timeout(timeout):
                    async with session.get(url) as resp:
                        resp.raise_for_status()
                        content_type = resp.headers.get("Content-Type", "")
                        body = await resp.text()
                break
            except (asyncio.TimeoutError, ClientResponseError, aiohttp.ClientError):
                if attempt >= max(1, retries):
                    raise
                await asyncio.sleep(backoff * (2 ** (attempt - 1)))
        if parse_html and "html" in (content_type or "").lower():
            return _extract_text(body)
        return body
    finally:
        if own_session:
            await session.close()

# Example usage
if __name__ == "__main__":
    async def main():
        url = "https://github.com/deyrahul95"
        text = await fetch_page_content(url)
        print(text)
    asyncio.run(main())
