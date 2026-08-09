from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import sys
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "platform" / "generated-artifacts.json"
_WRITE_POLICIES = {"automatic", "database", "manual"}


class GeneratedArtifactManifestError(ValueError):
    """Raised when generated-artifact ownership or ordering is invalid."""


@dataclass(frozen=True)
class GeneratorSpec:
    id: str
    depends_on: tuple[str, ...]
    outputs: tuple[str, ...]
    check: tuple[str, ...]
    write: tuple[str, ...] | None
    write_with_database: tuple[str, ...] | None
    write_policy: str


def _string_list(value: object, *, field: str, allow_empty: bool = False) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item for item in value
    ):
        raise GeneratedArtifactManifestError(
            f"{field} must be a list of nonempty strings"
        )
    if not allow_empty and not value:
        raise GeneratedArtifactManifestError(f"{field} must not be empty")
    return tuple(value)


def _optional_command(value: object, *, field: str) -> tuple[str, ...] | None:
    if value is None:
        return None
    return _string_list(value, field=field)


def parse_manifest(value: Mapping[str, Any]) -> tuple[GeneratorSpec, ...]:
    if set(value) != {"schema_version", "generators"}:
        raise GeneratedArtifactManifestError(
            "generated-artifact manifest has unknown or missing top-level fields"
        )
    if value.get("schema_version") != 1:
        raise GeneratedArtifactManifestError(
            "unsupported generated-artifact manifest schema_version"
        )
    rows = value.get("generators")
    if not isinstance(rows, list) or not rows:
        raise GeneratedArtifactManifestError("generators must be a nonempty list")

    expected_fields = {
        "id",
        "depends_on",
        "outputs",
        "check",
        "write",
        "write_with_database",
        "write_policy",
    }
    specs: list[GeneratorSpec] = []
    seen_ids: set[str] = set()
    output_owners: dict[str, str] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping) or set(row) != expected_fields:
            raise GeneratedArtifactManifestError(
                f"generators[{index}] has unknown or missing fields"
            )
        generator_id = row.get("id")
        if (
            not isinstance(generator_id, str)
            or not generator_id
            or generator_id in seen_ids
        ):
            raise GeneratedArtifactManifestError(
                f"generators[{index}].id must be unique and nonempty"
            )
        seen_ids.add(generator_id)
        policy = row.get("write_policy")
        if policy not in _WRITE_POLICIES:
            raise GeneratedArtifactManifestError(
                f"generator {generator_id} has unsupported write_policy"
            )
        outputs = _string_list(
            row.get("outputs"), field=f"generator {generator_id} outputs"
        )
        if len(outputs) != len(set(outputs)):
            raise GeneratedArtifactManifestError(
                f"generator {generator_id} declares a duplicate output"
            )
        for output in outputs:
            canonical = PurePosixPath(output)
            if (
                "\\" in output
                or canonical.is_absolute()
                or PureWindowsPath(output).is_absolute()
                or ".." in canonical.parts
                or canonical.as_posix() != output
            ):
                raise GeneratedArtifactManifestError(
                    f"generator {generator_id} output must be a canonical "
                    f"repository-relative POSIX path: {output}"
                )
            owner = output_owners.get(output)
            if owner is not None:
                raise GeneratedArtifactManifestError(
                    f"generated output {output} has multiple owners: "
                    f"{owner}, {generator_id}"
                )
            output_owners[output] = generator_id
        write = _optional_command(
            row.get("write"), field=f"generator {generator_id} write"
        )
        write_with_database = _optional_command(
            row.get("write_with_database"),
            field=f"generator {generator_id} write_with_database",
        )
        if policy == "automatic" and write is None:
            raise GeneratedArtifactManifestError(
                f"automatic generator {generator_id} requires a write command"
            )
        if policy == "database" and write_with_database is None:
            raise GeneratedArtifactManifestError(
                f"database generator {generator_id} requires write_with_database"
            )
        if write_with_database is not None and "{db}" not in write_with_database:
            raise GeneratedArtifactManifestError(
                f"generator {generator_id} database command must contain {{db}}"
            )
        depends_on = _string_list(
            row.get("depends_on"),
            field=f"generator {generator_id} depends_on",
            allow_empty=True,
        )
        if len(depends_on) != len(set(depends_on)):
            raise GeneratedArtifactManifestError(
                f"generator {generator_id} declares a duplicate dependency"
            )
        specs.append(
            GeneratorSpec(
                id=generator_id,
                depends_on=depends_on,
                outputs=outputs,
                check=_string_list(
                    row.get("check"), field=f"generator {generator_id} check"
                ),
                write=write,
                write_with_database=write_with_database,
                write_policy=str(policy),
            )
        )

    known = {spec.id for spec in specs}
    for spec in specs:
        unknown = set(spec.depends_on) - known
        if unknown:
            raise GeneratedArtifactManifestError(
                f"generator {spec.id} has unknown dependencies: "
                + ", ".join(sorted(unknown))
            )
        if spec.id in spec.depends_on:
            raise GeneratedArtifactManifestError(
                f"generator {spec.id} cannot depend on itself"
            )
    topological_order(specs)
    return tuple(specs)


def load_manifest(path: Path = MANIFEST_PATH) -> tuple[GeneratorSpec, ...]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise GeneratedArtifactManifestError(
            "generated-artifact manifest must contain a JSON object"
        )
    return parse_manifest(value)


def topological_order(
    specs: Sequence[GeneratorSpec],
) -> tuple[GeneratorSpec, ...]:
    by_id = {spec.id: spec for spec in specs}
    order_index = {spec.id: index for index, spec in enumerate(specs)}
    pending = {spec.id: set(spec.depends_on) for spec in specs}
    ordered: list[GeneratorSpec] = []
    while pending:
        ready = sorted(
            (generator_id for generator_id, dependencies in pending.items() if not dependencies),
            key=order_index.__getitem__,
        )
        if not ready:
            cycle = ", ".join(sorted(pending))
            raise GeneratedArtifactManifestError(
                f"generated-artifact dependency graph contains a cycle: {cycle}"
            )
        for generator_id in ready:
            ordered.append(by_id[generator_id])
            pending.pop(generator_id)
            for dependencies in pending.values():
                dependencies.discard(generator_id)
    return tuple(ordered)


def all_outputs(specs: Sequence[GeneratorSpec]) -> tuple[str, ...]:
    return tuple(output for spec in specs for output in spec.outputs)


def python_command(arguments: Sequence[str]) -> tuple[str, ...]:
    return (str(Path(sys.executable).resolve()), *arguments)


def check_command(spec: GeneratorSpec) -> tuple[str, ...]:
    return python_command(spec.check)


def write_command(
    spec: GeneratorSpec,
    *,
    database: Path | None,
    include_manual: bool,
) -> tuple[str, ...] | None:
    arguments: tuple[str, ...] | None
    if spec.write_policy == "manual" and not include_manual:
        return None
    if database is not None and spec.write_with_database is not None:
        arguments = tuple(
            str(database) if item == "{db}" else item
            for item in spec.write_with_database
        )
    else:
        arguments = spec.write
    return python_command(arguments) if arguments is not None else None


__all__ = [
    "GeneratedArtifactManifestError",
    "GeneratorSpec",
    "MANIFEST_PATH",
    "ROOT",
    "all_outputs",
    "check_command",
    "load_manifest",
    "parse_manifest",
    "topological_order",
    "write_command",
]
