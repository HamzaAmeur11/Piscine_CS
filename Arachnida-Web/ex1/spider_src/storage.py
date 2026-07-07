"""
storage.py - Storage and path management.
Creates output directory, generates safe filenames,
and avoids overwriting existing files.
"""

import os
import re
from urllib.parse import urlparse


# Maximum filename length (most filesystems allow 255 bytes)
_MAX_FILENAME = 200


def ensure_directory(path: str) -> None:
    """
    Create the output directory (and any parents) if it does not exist.
    Raises OSError / PermissionError if creation fails.
    """
    os.makedirs(path, exist_ok=True)


def safe_filename(url: str) -> str:
    """
    Derive a filesystem-safe filename from an image URL.

    Strategy:
    1. Take the path component of the URL.
    2. Extract the basename (last path segment).
    3. Replace unsafe characters with underscores.
    4. Truncate to _MAX_FILENAME characters while keeping the extension.
    """
    parsed = urlparse(url)
    # Use the URL path basename as starting point
    basename = os.path.basename(parsed.path) or "image"

    # Separate name and extension
    name, ext = os.path.splitext(basename)

    # Sanitize: keep alphanumeric, dots (except leading), hyphens, underscores
    name = re.sub(r"[^\w\-]", "_", name)
    ext = re.sub(r"[^\w\.]", "_", ext).lower()

    # Remove leading dots/underscores from name
    name = name.lstrip("._") or "image"

    # Reassemble and truncate
    filename = name + ext
    if len(filename) > _MAX_FILENAME:
        keep = _MAX_FILENAME - len(ext)
        filename = name[:keep] + ext

    return filename


def unique_path(directory: str, filename: str) -> str:
    """
    Return a path inside *directory* for *filename* that does not already exist.
    If filename is taken, append _1, _2, … before the extension.
    """
    candidate = os.path.join(directory, filename)
    if not os.path.exists(candidate):
        return candidate

    name, ext = os.path.splitext(filename)
    counter = 1
    while True:
        new_name = f"{name}_{counter}{ext}"
        candidate = os.path.join(directory, new_name)
        if not os.path.exists(candidate):
            return candidate
        counter += 1


def save_image(data: bytes, directory: str, filename: str) -> str:
    """
    Save *data* bytes to *directory*/*filename*, avoiding overwrites.
    Returns the final path where the file was written.
    Raises OSError on write failure.
    """
    ensure_directory(directory)
    path = unique_path(directory, filename)
    with open(path, "wb") as f:
        f.write(data)
    return path
