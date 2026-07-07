"""
url_utils.py - URL utilities.
Handles normalization, resolution, scheme checks, and image detection.
"""

from urllib.parse import urlparse, urlunparse, urljoin

# Extensions the spider must download (lowercase, with dot)
SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}


def normalize_url(url: str) -> str:
    """
    Normalize a URL for consistent deduplication:
    - Lowercase scheme and host
    - Remove default ports (80 for http, 443 for https)
    - Remove fragment
    - Keep path, query as-is
    """
    parsed = urlparse(url)

    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()

    # Strip default ports
    if ":" in netloc:
        host, port_str = netloc.rsplit(":", 1)
        try:
            port = int(port_str)
            if (scheme == "http" and port == 80) or (scheme == "https" and port == 443):
                netloc = host
        except ValueError:
            pass  # port_str wasn't a number; leave netloc alone

    # Remove fragment
    normalized = urlunparse((scheme, netloc, parsed.path, parsed.params, parsed.query, ""))
    return normalized


def resolve_url(base_url: str, link: str) -> str:
    """
    Resolve a (possibly relative) link against a base URL.
    Equivalent to: urljoin(base_url, link)
    """
    return urljoin(base_url, link)


def is_http_url(url: str) -> bool:
    """Return True if url uses http or https scheme."""
    scheme = urlparse(url).scheme.lower()
    return scheme in ("http", "https")


def is_supported_image_url(url: str) -> bool:
    """
    Return True if the URL path ends with a supported image extension.
    Query strings and fragments are ignored for extension detection.
    The check is case-insensitive.
    """
    path = urlparse(url).path.lower()
    for ext in SUPPORTED_IMAGE_EXTENSIONS:
        if path.endswith(ext):
            return True
    return False


def same_domain(url_a: str, url_b: str) -> bool:
    """Return True if both URLs share the same netloc (host[:port])."""
    return urlparse(url_a).netloc.lower() == urlparse(url_b).netloc.lower()


def strip_fragment(url: str) -> str:
    """Remove the #fragment part of a URL."""
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, ""))
