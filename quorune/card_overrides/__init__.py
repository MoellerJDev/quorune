"""Explicitly reviewed compatibility for historical card-specific records."""

from .game_record_v3 import (
    normalize_game_record_v3_effect,
    normalize_game_record_v3_runtime_handler,
)

__all__ = [
    "normalize_game_record_v3_effect",
    "normalize_game_record_v3_runtime_handler",
]
