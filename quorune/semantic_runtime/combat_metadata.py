from __future__ import annotations

"""Typed runtime metadata for bounded combat rules."""

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Mapping, Protocol, Sequence

from ..card_program_faces import program_matches_face
from ..rules.capabilities import load_default_capability_registry
from .component_registry import RuntimeComponentRegistry, exact_fields
from .context import SemanticNodeError


GOAD_PROHIBITION_EVENT = "combat.goad.prohibition"
GOAD_PROHIBITION_HANDLER_ID = (
    "prohibition.combat.goad.controller-creatures.v1"
)


@dataclass(frozen=True, slots=True)
class GoadProhibition:
    source_ref: str
    source_controller: str


@dataclass(frozen=True, slots=True)
class GoadProhibitionSourceContext:
    source_ref: str
    source_controller: str


@dataclass(frozen=True, slots=True)
class GoadProhibitionHandler:
    handler_id: str = GOAD_PROHIBITION_HANDLER_ID
    schema_version: int = 1
    family: str = "prohibition.combat.goad"
    event: str = GOAD_PROHIBITION_EVENT
    rule_references: tuple[str, ...] = ("101.2", "604.1", "701.15")
    capability_dependencies: tuple[str, ...] = (
        "combat.goad.prohibition.controller_creatures",
    )

    def validate(
        self,
        descriptor: Mapping[str, Any],
    ) -> None:
        exact_fields(
            descriptor,
            {
                "handler_id",
                "schema_version",
                "event",
                "affected_controller",
                "affected_card_type",
            },
            field="Goad-prohibition handler",
        )
        if descriptor["handler_id"] != self.handler_id:
            raise SemanticNodeError("Goad-prohibition handler ID mismatch")
        if (
            type(descriptor["schema_version"]) is not int
            or descriptor["schema_version"] != self.schema_version
        ):
            raise SemanticNodeError(
                "Unsupported goad-prohibition schema version"
            )
        if descriptor["event"] != self.event:
            raise SemanticNodeError(
                f"Goad-prohibition handler must use {self.event}"
            )
        if descriptor["affected_controller"] != "source_controller":
            raise SemanticNodeError(
                "Goad prohibition supports only the source controller"
            )
        if descriptor["affected_card_type"] != "creature":
            raise SemanticNodeError(
                "Goad prohibition supports only creature permanents"
            )

    def lower(
        self,
        descriptor: Mapping[str, Any],
        context: GoadProhibitionSourceContext,
    ) -> tuple[GoadProhibition, ...]:
        self.validate(descriptor)
        return (
            GoadProhibition(
                source_ref=context.source_ref,
                source_controller=context.source_controller,
            ),
        )


class GoadProhibitionRegistry(
    RuntimeComponentRegistry[GoadProhibitionSourceContext, GoadProhibition]
):
    pass


@lru_cache(maxsize=1)
def default_goad_prohibition_registry() -> GoadProhibitionRegistry:
    registry = GoadProhibitionRegistry((GoadProhibitionHandler(),))
    registry.require_registered_capabilities(load_default_capability_registry())
    return registry.freeze()


class CombatMetadataHost(Protocol):
    semantics: Any

    def _semantic_event_sources(
        self,
        *,
        zones: set[str] | None = None,
    ) -> Sequence[Any]: ...

    def card_record(self, card: Any) -> Any: ...

    def semantic_program_is_current_trusted(self, program: Any) -> bool: ...


def active_goad_prohibitions(
    host: CombatMetadataHost,
) -> tuple[GoadProhibition, ...]:
    """Collect current trusted goad prohibitions without reading prose."""

    registry = default_goad_prohibition_registry()
    prohibitions: list[GoadProhibition] = []
    for source in host._semantic_event_sources(zones={"battlefield"}):
        if source.zone != "battlefield" or source.phased_out:
            continue
        record = host.card_record(source)
        if record is None:
            continue
        for program in host.semantics.runtime_handler_programs_for_oracle(
            record.oracle_id,
            active_zone="battlefield",
            event=GOAD_PROHIBITION_EVENT,
        ):
            if (
                not host.semantic_program_is_current_trusted(program)
                or not program_matches_face(record, program, source)
            ):
                continue
            context = GoadProhibitionSourceContext(
                source_ref=source.ref,
                source_controller=source.controller,
            )
            for descriptor in program.handlers:
                if registry.describe(str(descriptor.get("handler_id") or "")):
                    prohibitions.extend(registry.lower(descriptor, context))
    return tuple(
        sorted(
            prohibitions,
            key=lambda value: (value.source_ref, value.source_controller),
        )
    )


__all__ = [
    "GOAD_PROHIBITION_EVENT",
    "GOAD_PROHIBITION_HANDLER_ID",
    "GoadProhibition",
    "GoadProhibitionHandler",
    "GoadProhibitionRegistry",
    "active_goad_prohibitions",
    "default_goad_prohibition_registry",
]
