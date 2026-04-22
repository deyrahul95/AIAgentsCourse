from __future__ import annotations
import asyncio
import time
from typing import Set, List, Tuple, Dict
from urllib.parse import urlparse, urljoin
import aiohttp
import async_timeout
from aiohttp import ClientResponseError
from bs4 import BeautifulSoup
from readability import Document  # type: ignore
import urllib.robotparser

DEFAULT_USER_AGENT = "my-async-scraper/1.0 (+https://example.com)"
DEFAULT_TIMEOUT = 10
DEFAULT_RETRIES = 3
DEFAULT_BACKOFF = 0.5
MIN_REQUEST_INTERVAL = 1.0
MAX_PAGES = 5

_last_request_time_by_host: Dict[str, float] = {}


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


def _clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(
        [
            "script",
            "style",
            "noscript",
            "iframe",
            "header",
            "footer",
            "nav",
            "form",
            "aside",
        ]
    ):
        tag.decompose()
    return str(soup)


def _extract_main_text(html: str) -> str:
    doc = Document(html)
    content_html = doc.summary()  # type: ignore
    soup = BeautifulSoup(content_html, "lxml")  # type: ignore
    text = soup.get_text("\n", strip=True)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return "\n".join(lines)


def _find_internal_links(base_url: str, html: str) -> List[str]:
    base = urlparse(base_url)
    host = base.netloc.lower()
    soup = BeautifulSoup(html, "lxml")
    links: List[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()  # type: ignore
        if href.startswith("#") or href.lower().startswith(("mailto:", "javascript:")):  # type: ignore
            continue
        joined = urljoin(base_url, href)  # type: ignore
        parsed = urlparse(joined)
        if parsed.scheme in ("http", "https") and parsed.netloc.lower() == host:
            normalized = parsed._replace(fragment="").geturl()
            links.append(normalized)
    return links


async def _fetch_once(
    session: aiohttp.ClientSession, url: str, timeout: int
) -> Tuple[str, str]:
    async with async_timeout.timeout(timeout):
        async with session.get(url) as resp:
            resp.raise_for_status()
            content_type = resp.headers.get("Content-Type", "") or ""
            body = await resp.text(errors="ignore")
    return content_type, body


async def fetch_page_content(
    url: str,
    *,
    max_pages: int = MAX_PAGES,
    user_agent: str = DEFAULT_USER_AGENT,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
    backoff: float = DEFAULT_BACKOFF,
    respect_robots: bool = True,
) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("Invalid URL")

    if respect_robots and not _is_allowed_by_robots(url, user_agent):
        raise PermissionError("Disallowed by robots.txt")

    host = _get_host(url)
    await _respect_rate_limit(host)

    headers = {"User-Agent": user_agent, "Accept": "text/html"}
    async with aiohttp.ClientSession(headers=headers) as session:
        to_visit: List[str] = [url]
        visited: Set[str] = set()
        main_texts: List[str] = []

        while to_visit and len(visited) < max_pages:
            url = to_visit.pop(0)
            if url in visited:
                continue
            if respect_robots and not _is_allowed_by_robots(url, user_agent):
                visited.add(url)
                continue
            await _respect_rate_limit(_get_host(url))

            attempt = 0
            content_type = ""
            body = ""
            while True:
                try:
                    attempt += 1
                    content_type, body = await _fetch_once(session, url, timeout)
                    break
                except (asyncio.TimeoutError, ClientResponseError, aiohttp.ClientError):
                    if attempt >= max(1, retries):
                        break
                    await asyncio.sleep(backoff * (2 ** (attempt - 1)))

            visited.add(url)
            if not body or "html" not in (content_type or "").lower():
                continue

            cleaned = _clean_html(body)
            try:
                text = _extract_main_text(cleaned)
            except Exception:
                soup = BeautifulSoup(cleaned, "lxml")
                text = "\n".join(
                    [
                        ln.strip()
                        for ln in soup.get_text("\n", strip=True).splitlines()
                        if ln.strip()
                    ]
                )

            if text:
                main_texts.append(text)

            if len(visited) + len(to_visit) < max_pages:
                for link in _find_internal_links(url, body):
                    if link not in visited and link not in to_visit:
                        to_visit.append(link)
                        if len(visited) + len(to_visit) >= max_pages:
                            break

        return "\n".join(main_texts)


# Example usage
if __name__ == "__main__":

    async def main() -> None:
        webpage = await fetch_page_content(url="https://cnn.com")
        print(webpage)

    asyncio.run(main())
