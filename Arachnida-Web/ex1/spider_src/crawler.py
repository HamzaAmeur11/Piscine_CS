"""
crawler.py - Web crawler.
BFS crawl: fetches HTML pages, extracts links/images,
manages recursion depth, and avoids revisiting pages.
"""
from .config import Config
import urllib.error

import urllib.request
from collections import deque
from typing import Optional
from .html_parser import extract_urls
from .url_utils import normalize_url, is_http_url, same_domain
from .downloader import ImageDownloader
from .errors import warn, info

_REQUEST_TIMEOUT = 10
_USER_AGENT = "spider/1.0 (42 cybersecurity project)"
_HTML_CONTENT_TYPES = {"text/html", "application/xhtml+xml"}


class Crawler:
    """
    BFS web crawler.

    - Stays on the same domain as the start URL (for page crawling).
    - Downloads images from any domain.
    - Respects max_depth when recursive=True.
    """

    def __init__(self, config: Config):
        self._config = config
        self._downloader = ImageDownloader(config.output_path)
        self._visited_pages: set = set()

    def run(self) -> None:
        """Start the crawl from config.start_url."""
        start = self._config.start_url
        info(f"Starting crawl: {start}")

        # Queue items: (url, depth)
        queue: deque = deque()
        queue.append((start, 0))

        while queue:
            current_url, depth = queue.popleft()

            norm = normalize_url(current_url)
            if norm in self._visited_pages:
                continue
            self._visited_pages.add(norm)

            # --- Fetch page ---
            html_content = self._fetch_html(current_url)
            if html_content is None:
                continue  # non-HTML or network error — skip

            # --- Parse ---
            page_links, image_links = extract_urls(html_content, current_url)

            # --- Download images found on this page ---
            for img_url in image_links:
                self._downloader.download(img_url)

            # --- Recurse if enabled ---
            if self._config.recursive and depth < self._config.max_depth:
                for link in page_links:
                    if not is_http_url(link):
                        continue
                    # Only follow links on the same domain
                    if not same_domain(link, start):
                        continue
                    norm_link = normalize_url(link)
                    if norm_link not in self._visited_pages:
                        queue.append((link, depth + 1))

        info("Crawl finished.")

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------

    def _fetch_html(self, url: str) -> Optional[str]:
        """
        Fetch a URL and return its HTML text if the response is HTML.
        Returns None for non-HTML responses, network errors, etc.
        """
        try:
            req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
            with urllib.request.urlopen(req, timeout=_REQUEST_TIMEOUT) as resp:
                content_type = resp.headers.get("Content-Type", "")
                base_ct = content_type.split(";")[0].strip().lower()
                if base_ct not in _HTML_CONTENT_TYPES:
                    return None
                # Read and decode; ignore errors for broken pages
                raw = resp.read()
                # Try to detect encoding from Content-Type header
                charset = _parse_charset(content_type) or "utf-8"
                try:
                    return raw.decode(charset, errors="replace")
                except (LookupError, UnicodeDecodeError):
                    return raw.decode("utf-8", errors="replace")
        except Exception as exc:
            warn(f"Could not fetch {url}: {exc}")
            return None


def _parse_charset(content_type: str) -> Optional[str]:
    """Extract charset from Content-Type header, e.g. 'text/html; charset=utf-8'."""
    for part in content_type.split(";"):
        part = part.strip()
        if part.lower().startswith("charset="):
            return part[len("charset="):].strip().strip('"')
    return None
