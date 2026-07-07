"""
errors.py - Error/reporting layer.
Custom exceptions and helper functions for warning output.
"""

import sys


class SpiderError(Exception):
    """Base exception for fatal spider errors."""


class ConfigError(SpiderError):
    """Invalid CLI configuration."""


def warn(message: str) -> None:
    """Print a non-fatal warning to stderr."""
    print(f"[WARNING] {message}", file=sys.stderr)


def info(message: str) -> None:
    """Print an informational message to stderr."""
    print(f"[INFO] {message}", file=sys.stderr)
