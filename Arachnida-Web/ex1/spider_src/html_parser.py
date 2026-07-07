"""
html_parser.py - HTML parsing.
Extracts page links and image URLs from HTML content.
Uses only stdlib html.parser (no external dependencies).
"""

from html.parser import HTMLParser
from typing import Tuple, List

from .url_utils import resolve_url, is_http_url, is_supported_image_url


class _LinkImageParser(HTMLParser):
    """Internal HTMLParser subclass that collects hrefs and img srcs."""

    def __init__(self, base_url: str):
        super().__init__()
        self._base_url = base_url
        self.page_links: List[str] = []
        self.image_links: List[str] = []

    def handle_starttag(self, tag: str, attrs):
        attr_dict = dict(attrs)

        if tag == "a":
            href = attr_dict.get("href", "")
            if href:
                resolved = resolve_url(self._base_url, href)
                if is_http_url(resolved):
                    # If the href itself points to an image, collect as image too
                    if is_supported_image_url(resolved):
                        self.image_links.append(resolved)
                    else:
                        self.page_links.append(resolved)

        elif tag == "img":
            src = attr_dict.get("src", "")
            if src:
                resolved = resolve_url(self._base_url, src)
                if is_http_url(resolved):
                    self.image_links.append(resolved)


def extract_urls(html_content: str, base_url: str) -> Tuple[List[str], List[str]]:
    """
    Parse HTML and return (page_links, image_links).

    page_links  - absolute HTTP(S) URLs found in <a href="..."> that are NOT images
    image_links - absolute HTTP(S) image URLs (from <img src="..."> and image hrefs)

    Does not download anything. Does not decide recursion depth.
    """
    parser = _LinkImageParser(base_url)
    try:
        parser.feed(html_content)
    except Exception:
        # Malformed HTML should not crash the crawl
        pass

    return parser.page_links, parser.image_links
