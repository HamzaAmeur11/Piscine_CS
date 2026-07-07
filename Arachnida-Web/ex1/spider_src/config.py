"""
config.py - Configuration data structure.
Stores validated settings; does NOT parse arguments itself.
"""

from dataclasses import dataclass


@dataclass
class Config:
    start_url: str
    recursive: bool = False
    max_depth: int = 5
    output_path: str = "./data/"
