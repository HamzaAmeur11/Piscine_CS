"""
cli.py - CLI argument parsing.
Parses ./spider [-rlp] URL, validates, and returns a Config.
"""

import argparse
import sys

from .config import Config


def parse_args(argv=None) -> Config:
    parser = argparse.ArgumentParser(
        prog="spider",
        description="Extract and download images from a website.",
        add_help=True,
    )

    parser.add_argument(
        "-r",
        action="store_true",
        dest="recursive",
        help="Recursively download images from linked pages.",
    )

    parser.add_argument(
        "-l",
        type=_positive_int,
        metavar="N",
        dest="max_depth",
        default=5,
        help="Maximum recursion depth (requires -r). Default: 5.",
    )

    parser.add_argument(
        "-p",
        metavar="PATH",
        dest="output_path",
        default="./data/",
        help="Directory to save downloaded images. Default: ./data/",
    )

    parser.add_argument(
        "url",
        metavar="URL",
        help="URL to start crawling from.",
    )

    args = parser.parse_args(argv)

    # Validate URL scheme
    if not (args.url.startswith("http://") or args.url.startswith("https://")):
        parser.error(
            f"URL must start with http:// or https://. Got: {args.url!r}"
        )

    # -l without -r is silently accepted but has no effect (as wget does).
    # We keep max_depth stored regardless; crawler only uses it when recursive=True.

    return Config(
        start_url=args.url,
        recursive=args.recursive,
        max_depth=args.max_depth,
        output_path=args.output_path,
    )


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _positive_int(value: str) -> int:
    """argparse type helper: ensure depth is a non-negative integer."""
    try:
        ivalue = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Depth must be an integer, got: {value!r}"
        )
    if ivalue < 0:
        raise argparse.ArgumentTypeError(
            f"Depth must be >= 0, got: {ivalue}"
        )
    return ivalue
