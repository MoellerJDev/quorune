from __future__ import annotations

"""Typed controller-wide permissions discovered from active CardPrograms."""

from dataclasses import dataclass
from enum import StrEnum
from functools import lru_cache
from typing import Any, Mapping, Protocol, Sequence

from ..card_program_faces import program_matches_face
from ..rules.capabilities import load_default_capability_registry
from .component_registry import RuntimeComponentRegistry, exact_fields
from .context import SemanticNodeError


ACTION_PERMISSION_EVENT = "action.permission"
LAND_PLAY_FROM_OWN_GRAVEYARD_HANDLER_ID = (
    "permission.action.land-play-own-graveyard.v1"
)
ACTIVATE_CONTROLLED_CREATURE_AS_HASTE_HANDLER_ID = (
    "permission.action.activate-controlled-creature-as-haste.v1"
)


class ActionPermissionKind(StrEnum):
    LAND_PLAY_FROM_OWN_GRAVEYARD = "land_play_from_own_graveyard"
    ACTIVATE_CONTROLLED_CREATURE_AS_HASTE = (
        "activate_controlled_creature_as_haste"
    )


@dataclass(frozen=True, slots=True)
class ActionPermissionSourceContext:
    source_ref: str
    source_controller: str


@dataclass(frozen=True, slots=True)
class StaticActionPermission:
    kind: ActionPermissionKind
    player: str
    source_ref: str


@dataclass(frozen=True, slots=True)
class StaticActionPermissionHandler:
    handler_id: str
    permission: ActionPermissionKind
    rule_references: tuple[str, ...]
    capability_dependencies: tuple[str, ...]
    schema_version: int = 1
    family: str = "permission.action.static"
    event: str = ACTION_PERMISSION_EVENT

    def validate(
        self,
        descriptor: Mapping[str, Any],
    ) -> ActionPermissionKind:
        exact_fields(
            descriptor,
            {"handler_id", "schema_version", "event", "permission"},
            field="Static action-permission handler",
        )
        if descriptor["handler_id"] != self.handler_id:
            raise SemanticNodeError(
                "Static action-permission handler ID mismatch"
            )
        if (
            type(descriptor["schema_version"]) is not int
            or descriptor["schema_version"] != self.schema_version
        ):
            raise SemanticNodeError(
                "Unsupported static action-permission schema version"
            )
        if descriptor["event"] != self.event:
            raise SemanticNodeError(
                f"Static action-permission handler must use {self.event}"
            )
        if descriptor["permission"] != self.permission.value:
            raise SemanticNodeError(
                "Static action-permission kind does not match its handler"
            )
        return self.permission

    def lower(
        self,
        descriptor: Mapping[str, Any],
        context: ActionPermissionSourceContext,
    ) -> tuple[StaticActionPermission, ...]:
        permission = self.validate(descriptor)
        return (
            StaticActionPermission(
                kind=permission,
                player=context.source_controller,
                source_ref=context.source_ref,
            ),
        )


class ActionPermissionRegistry(
    RuntimeComponentRegistry[
        ActionPermissionSourceContext,
        StaticActionPermission,
    ]
):
    pass


@lru_cache(maxsize=1)
def default_action_permission_registry() -> ActionPermissionRegistry:
    registry = ActionPermissionRegistry(
        (
            StaticActionPermissionHandler(
                handler_id=LAND_PLAY_FROM_OWN_GRAVEYARD_HANDLER_ID,
                permission=(
                    ActionPermissionKind.LAND_PLAY_FROM_OWN_GRAVEYARD
                ),
                rule_references=("116.2a", "305.2", "305.2a"),
                capability_dependencies=(
                    "land.play.from_own_graveyard",
                ),
            ),
            StaticActionPermissionHandler(
                handler_id=(
                    ACTIVATE_CONTROLLED_CREATURE_AS_HASTE_HANDLER_ID
                ),
                permission=(
                    ActionPermissionKind.ACTIVATE_CONTROLLED_CREATURE_AS_HASTE
                ),
                rule_references=("302.6", "602.5b", "702.10c"),
                capability_dependencies=(
                    "activation.permission.controlled_creature_as_haste",
                ),
            ),
        )
    )
    registry.require_registered_capabilities(
        load_default_capability_registry()
    )
    return registry.freeze()


class ActionPermissionHost(Protocol):
    active_seats: Sequence[str]
    semantics: Any

    def _semantic_event_sources(
        self,
        *,
        zones: set[str] | None = None,
    ) -> Sequence[Any]: ...

    def card_record(self, card: Any) -> Any: ...

    def semantic_program_is_current_trusted(self, program: Any) -> bool: ...


def controller_action_permissions(
    host: ActionPermissionHost,
    player: str,
) -> tuple[StaticActionPermission, ...]:
    """Collect active, face-pinned permissions controlled by one player."""

    if player not in host.active_seats:
        return ()
    registry = default_action_permission_registry()
    permissions: list[StaticActionPermission] = []
    for source in host._semantic_event_sources(zones={"battlefield"}):
        if (
            source.zone != "battlefield"
            or source.controller != player
            or source.phased_out
        ):
            continue
        record = host.card_record(source)
        if record is None:
            continue
        programs = host.semantics.runtime_handler_programs_for_oracle(
            source.oracle_id,
            active_zone="battlefield",
            event=ACTION_PERMISSION_EVENT,
        )
        for program in programs:
            if (
                not host.semantic_program_is_current_trusted(program)
                or not program_matches_face(record, program, source)
            ):
                continue
            context = ActionPermissionSourceContext(
                source_ref=source.ref,
                source_controller=source.controller,
            )
            for descriptor in program.handlers:
                if registry.describe(
                    str(descriptor.get("handler_id") or "")
                ) is not None:
                    permissions.extend(registry.lower(descriptor, context))
    return tuple(
        sorted(
            permissions,
            key=lambda permission: (
                permission.kind.value,
                permission.source_ref,
            ),
        )
    )


def controller_has_action_permission(
    host: ActionPermissionHost,
    player: str,
    kind: ActionPermissionKind,
) -> bool:
    return any(
        permission.kind is kind and permission.player == player
        for permission in controller_action_permissions(host, player)
    )


__all__ = [
    "ACTION_PERMISSION_EVENT",
    "ACTIVATE_CONTROLLED_CREATURE_AS_HASTE_HANDLER_ID",
    "LAND_PLAY_FROM_OWN_GRAVEYARD_HANDLER_ID",
    "ActionPermissionKind",
    "ActionPermissionRegistry",
    "ActionPermissionSourceContext",
    "StaticActionPermission",
    "StaticActionPermissionHandler",
    "controller_action_permissions",
    "controller_has_action_permission",
    "default_action_permission_registry",
]
