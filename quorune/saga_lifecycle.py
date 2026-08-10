from __future__ import annotations

"""Immutable facts for the represented ordinary Saga final-chapter SBA."""

from dataclasses import dataclass


class SagaLifecycleError(ValueError):
    """A Saga final-chapter snapshot is malformed or contradictory."""


@dataclass(frozen=True, slots=True)
class SagaFinalChapterSnapshot:
    """The complete represented CR 704.5s/714.4 state for one Saga.

    ``chapter_trigger_pending`` is true only for a chapter ability from this
    exact logical incarnation.  Keeping physical and logical identity in the
    immutable value prevents an older incarnation's trigger from protecting a
    Saga that left the battlefield and returned.
    """

    object_id: str
    logical_object_id: str
    controller: str
    lore_counters: int
    chapter_numbers: tuple[int, ...]
    chapter_trigger_pending: bool

    def __post_init__(self) -> None:
        for field in ("object_id", "logical_object_id", "controller"):
            value = getattr(self, field)
            if type(value) is not str or not value or value != value.strip():
                raise SagaLifecycleError(
                    f"Saga lifecycle {field} must be a canonical identity"
                )
        if type(self.lore_counters) is not int or self.lore_counters < 0:
            raise SagaLifecycleError(
                "Saga lifecycle lore counters must be a nonnegative integer"
            )
        chapters = tuple(self.chapter_numbers)
        if (
            not chapters
            or any(type(value) is not int or value < 1 for value in chapters)
            or chapters != tuple(sorted(set(chapters)))
        ):
            raise SagaLifecycleError(
                "Saga lifecycle chapters must be unique positive integers "
                "in canonical order"
            )
        if type(self.chapter_trigger_pending) is not bool:
            raise SagaLifecycleError(
                "Saga lifecycle pending-trigger state must be boolean"
            )
        object.__setattr__(self, "chapter_numbers", chapters)

    @property
    def final_chapter_number(self) -> int:
        return self.chapter_numbers[-1]

    @property
    def requires_sacrifice(self) -> bool:
        return (
            self.lore_counters >= self.final_chapter_number
            and not self.chapter_trigger_pending
        )


__all__ = [
    "SagaFinalChapterSnapshot",
    "SagaLifecycleError",
]
