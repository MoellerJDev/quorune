from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class AbilityKeywordFragmentLowering:
    handlers: tuple[Mapping[str, Any], ...] = ()
    residual_kind: str | None = None
    residual_reason: str | None = None
    residual_blockers: tuple[str, ...] = ()


__all__ = ["AbilityKeywordFragmentLowering"]
