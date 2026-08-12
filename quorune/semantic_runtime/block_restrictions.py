from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Mapping, Protocol, Sequence

from ..rules.capabilities import load_default_capability_registry
from ..replacement.immutable import FrozenMap
from .component_registry import RuntimeComponentRegistry, exact_fields
from .context import SemanticNodeError


_SELF_COUNTER_HANDLER_ID = "combat.block.self-counter-prohibition.v1"
_COUNTERS_FIELD = "counters"


def _normalized_counter_name(value: Any) -> str:
    if type(value) is not str:
        raise SemanticNodeError("Block-restriction counter name must be a string")
    name = " ".join(value.casefold().split())
    if not name:
        raise SemanticNodeError("Block-restriction counter name must be nonempty")
    return name


@dataclass(frozen=True, slots=True)
class SelfCounterBlockRestrictionNode:
    counter_name: str
    minimum: int
    rule_id: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "counter_name", _normalized_counter_name(self.counter_name)
        )
        if type(self.minimum) is not int or self.minimum < 1:
            raise SemanticNodeError(
                "Block-restriction counter minimum must be a positive integer"
            )
        if type(self.rule_id) is not str or not self.rule_id.strip():
            raise SemanticNodeError("Block restriction requires a rule identity")


@dataclass(frozen=True, slots=True)
class BlockRestrictionContext:
    source_ref: str
    counters: Mapping[str, int]

    def __post_init__(self) -> None:
        if type(self.source_ref) is not str or not self.source_ref:
            raise SemanticNodeError("Block restriction requires source identity")
        normalized: dict[str, int] = {}
        if not isinstance(self.counters, Mapping):
            raise SemanticNodeError("Block-restriction counters must be a mapping")
        for raw_name, amount in self.counters.items():
            name = _normalized_counter_name(raw_name)
            if type(amount) is not int or amount < 0:
                raise SemanticNodeError(
                    "Block-restriction counter amounts must be nonnegative integers"
                )
            if amount:
                normalized[name] = amount
        object.__setattr__(self, _COUNTERS_FIELD, FrozenMap(normalized))


@dataclass(frozen=True, slots=True)
class BlockProhibition:
    source_ref: str
    handler_id: str
    rule_id: str
    counter_name: str


@dataclass(frozen=True, slots=True)
class SelfCounterBlockRestrictionHandler:
    handler_id: str = _SELF_COUNTER_HANDLER_ID
    schema_version: int = 1
    family: str = "combat.block.self-counter-prohibition"
    event: str = "combat.block"
    rule_references: tuple[str, ...] = ("509.1b", "702.98a")
    capability_dependencies: tuple[str, ...] = (
        "combat.block.self_counter_prohibition",
    )

    def validate(
        self, descriptor: Mapping[str, Any]
    ) -> SelfCounterBlockRestrictionNode:
        exact_fields(
            descriptor,
            {
                "handler_id",
                "schema_version",
                "event",
                "counter_name",
                "minimum",
                "rule_id",
            },
            field="self-counter block restriction",
        )
        if descriptor["handler_id"] != self.handler_id:
            raise SemanticNodeError("Block-restriction handler identity changed")
        if descriptor["schema_version"] != self.schema_version:
            raise SemanticNodeError("Unsupported block-restriction schema version")
        if descriptor["event"] != self.event:
            raise SemanticNodeError("Self-counter restriction must handle blocking")
        return SelfCounterBlockRestrictionNode(
            counter_name=descriptor["counter_name"],
            minimum=descriptor["minimum"],
            rule_id=descriptor["rule_id"],
        )

    def lower(
        self,
        descriptor: Mapping[str, Any],
        context: BlockRestrictionContext,
    ) -> tuple[BlockProhibition, ...]:
        node = self.validate(descriptor)
        if int(context.counters.get(node.counter_name, 0)) < node.minimum:
            return ()
        return (
            BlockProhibition(
                source_ref=context.source_ref,
                handler_id=self.handler_id,
                rule_id=node.rule_id,
                counter_name=node.counter_name,
            ),
        )


class BlockRestrictionHost(Protocol):
    semantics: Any

    def semantic_program_is_current_trusted(self, program: Any) -> bool: ...


@lru_cache(maxsize=1)
def default_block_restriction_registry(
) -> RuntimeComponentRegistry[BlockRestrictionContext, BlockProhibition]:
    registry = RuntimeComponentRegistry((SelfCounterBlockRestrictionHandler(),))
    registry.require_registered_capabilities(load_default_capability_registry())
    return registry.freeze()


def current_self_block_prohibitions(
    host: BlockRestrictionHost,
    blocker: Any,
) -> tuple[BlockProhibition, ...]:
    registry = default_block_restriction_registry()
    context = BlockRestrictionContext(
        source_ref=blocker.ref,
        counters=blocker.counters,
    )
    prohibitions: list[BlockProhibition] = []
    programs: Sequence[Any] = host.semantics.runtime_handler_programs_for_oracle(
        blocker.oracle_id,
        active_zone="battlefield",
        event="combat.block",
    )
    for program in programs:
        if not host.semantic_program_is_current_trusted(program):
            continue
        for descriptor in program.handlers:
            prohibitions.extend(registry.lower(descriptor, context))
    return tuple(
        sorted(
            prohibitions,
            key=lambda value: (
                value.source_ref,
                value.handler_id,
                value.rule_id,
                value.counter_name,
            ),
        )
    )


__all__ = [
    "BlockProhibition",
    "BlockRestrictionContext",
    "SelfCounterBlockRestrictionHandler",
    "SelfCounterBlockRestrictionNode",
    "current_self_block_prohibitions",
    "default_block_restriction_registry",
]
