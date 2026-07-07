"""
downloader.py - Image downloader.
Makes HTTP requests, validates content, and passes bytes to storage.
"""

import urllib.request
import urllib.error
from typing import Optional

from .url_utils import is_supported_image_url, normalize_url
from .storage import safe_filename, save_image
from .errors import warn, info

# Supported MIME types (loose check — some servers misconfigure headers)
_SUPPORTED_CONTENT_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/gif",
    "image/bmp",
    "image/x-bmp",
    "image/x-ms-bmp",
    "application/octet-stream",  # generic binary — accept and rely on extension
}

_REQUEST_TIMEOUT = 10  # seconds
_USER_AGENT = "spider/1.0 (42 cybersecurity project)"


class ImageDownloader:
    """
    Downloads images from URLs and saves them to a directory.
    Tracks already-downloaded URLs to avoid duplicates.
    """

    def __init__(self, output_path: str):
        self._output_path = output_path
        self._downloaded_urls: set = set()  # normalized URL dedup (Level 1)

    def download(self, url: str) -> Optional[str]:
        """
        Download the image at *url* and save it to the output directory.

        Returns the saved file path on success, or None if skipped/failed.
        """
        # --- Level 1 duplicate check: same normalized URL ---
        norm = normalize_url(url)
        if norm in self._downloaded_urls:
            return None

        # --- Pre-filter: extension check before making a request ---
        if not is_supported_image_url(url):
            return None

        # --- Fetch ---
        try:
            data, content_type = _fetch(url)
        except Exception as exc:
            warn(f"Failed to download {url}: {exc}")
            return None

        # --- Content-type sanity check (loose) ---
        base_ct = content_type.split(";")[0].strip().lower() if content_type else ""
        if base_ct and base_ct not in _SUPPORTED_CONTENT_TYPES:
            warn(f"Skipping {url}: unexpected content-type {content_type!r}")
            return None

        # --- Save ---
        filename = safe_filename(url)
        try:
            saved_path = save_image(data, self._output_path, filename)
        except OSError as exc:
            warn(f"Could not save {url}: {exc}")
            return None

        self._downloaded_urls.add(norm)
        info(f"Saved: {saved_path}")
        return saved_path


# ---------------------------------------------------------------------------
# internal helpers
# ---------------------------------------------------------------------------

def _fetch(url: str):
    """
    Fetch URL bytes and return (data, content_type).
    Raises urllib.error.URLError / http.client.HTTPException on failure.
    """
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    with urllib.request.urlopen(req, timeout=_REQUEST_TIMEOUT) as resp:
        content_type = resp.headers.get("Content-Type", "")
        data = resp.read()
    return data, content_type
