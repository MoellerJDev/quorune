from __future__ import annotations

from typing import Iterable

from ..rules.capabilities import CapabilityRegistry
from .declaration_nodes import declaration_static_node
from .intrinsic_counter_nodes import intrinsic_counter_prohibition_node
from .ir_model import OracleNode, OracleResidual, SourceSpan
from .kicker_nodes import fixed_kicked_entry_node
from .static_runtime_nodes import static_runtime_node


def closed_static_or_replacement_node(
    *,
    node_id: str,
    line: str,
    material_line: str,
    span: SourceSpan,
    source_name: str,
    card_types: Iterable[str],
    permanent_card_types: set[str],
    source_is_class: bool,
    capability_registry: CapabilityRegistry | None,
    capability_profile: str,
    residuals: list[OracleResidual],
) -> OracleNode | None:
    """Dispatch closed nontriggered static and replacement line owners."""

    counter_prohibition = intrinsic_counter_prohibition_node(
        node_id=node_id,
        line=line,
        material_line=material_line,
        span=span,
        capability_registry=capability_registry,
        capability_profile=capability_profile,
        residuals=residuals,
    )
    if counter_prohibition is not None:
        return counter_prohibition
    kicked_entry = fixed_kicked_entry_node(
        node_id=node_id,
        line=line,
        material_line=material_line,
        span=span,
        capability_registry=capability_registry,
        capability_profile=capability_profile,
        residuals=residuals,
    )
    if kicked_entry is not None:
        return kicked_entry
    declaration = declaration_static_node(
        node_id=node_id,
        line=line,
        card_name=source_name,
        span=span,
        residuals=residuals,
        capability_registry=capability_registry,
        capability_profile=capability_profile,
    )
    if declaration is not None:
        return declaration
    return static_runtime_node(
        node_id=node_id,
        line=line,
        material_line=material_line,
        span=span,
        source_name=source_name,
        card_types=card_types,
        permanent_card_types=permanent_card_types,
        source_is_class=source_is_class,
        capability_registry=capability_registry,
        capability_profile=capability_profile,
        residuals=residuals,
    )


__all__ = ["closed_static_or_replacement_node"]
