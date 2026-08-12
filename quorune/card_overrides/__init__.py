"""Explicitly classified card overrides and historical compatibility adapters."""

from .game_record_v3 import (
    normalize_game_record_v3_effect,
    normalize_game_record_v3_runtime_handler,
)

__all__ = [
    "normalize_game_record_v3_effect",
    "normalize_game_record_v3_runtime_handler",
]
