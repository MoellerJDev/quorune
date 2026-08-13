from __future__ import annotations

import ast
import json
from types import SimpleNamespace
import unittest

from scripts.architecture_identity_flow import (
    PROHIBITED_CLASSIFICATION,
    analyze_identity_flows,
    analyze_identity_source,
)
from scripts.architecture_observability import (
    _declared_runtime_text_subsystems,
    classify_state_writes,
    runtime_text_accesses,
    runtime_text_growth,
)
from scripts.update_architecture_audit import ROOT, analyze_production
from scripts.validate_architecture import (
    _card_identity_failures,
    _game_state_imports,
    evaluate_architecture,
    forbidden_import_violations,
    mutation_ownership_violations,
)


class ArchitectureGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = json.loads(
            (ROOT / "platform" / "architecture-policy.json").read_text(
                encoding="utf-8"
            )
        )
        cls.audit_source = json.loads(
            (ROOT / "platform" / "architecture-audit-source.json").read_text(
                encoding="utf-8"
            )
        )

    def test_current_repository_passes_every_architecture_guard(self):
        result = evaluate_architecture()
        self.assertEqual(result["status"], "pass", result["failures"])
        self.assertEqual(result["failures"], [])

    def test_forbidden_rules_import_is_rejected(self):
        protected = self.policy["protected_rules_modules"][0]
        analyses = {protected: SimpleNamespace(imports=("fastapi",))}
        self.assertEqual(
            forbidden_import_violations(analyses, self.policy),
            [{"file": protected, "import": "fastapi"}],
        )

    def test_typed_handler_cannot_import_authoritative_engine(self):
        relative = "quorune/semantic_runtime/generic.py"
        analyses = {
            relative: SimpleNamespace(imports=("quorune.engine",))
        }
        self.assertEqual(
            forbidden_import_violations(analyses, self.policy),
            [{"file": relative, "import": "quorune.engine"}],
        )

    def test_general_life_owner_cannot_depend_on_damage_results(self):
        relative = "quorune/effect_runtime/life_effects.py"
        imported = "quorune.semantic_runtime.damage_results"
        analyses = {relative: SimpleNamespace(imports=(imported,))}
        self.assertEqual(
            forbidden_import_violations(analyses, self.policy),
            [{"file": relative, "import": imported}],
        )

    def test_game_state_access_and_nonowner_mutation_are_rejected(self):
        tree = ast.parse("from quorune.model import GameState\n")
        self.assertTrue(_game_state_imports(tree))
        location = {
            "file": "quorune/rules/zones.py",
            "symbol": "move",
            "line": 10,
        }
        self.assertEqual(
            mutation_ownership_violations(
                [location], self.policy["game_state_access"]["mutable_owners"]
            ),
            [location],
        )

    def test_direct_writes_are_classified_by_actual_owner(self):
        records = [
            {
                "file": "quorune/engine.py",
                "symbol": "_begin_turn",
                "kind": "assignment",
                "state_path": "active_player",
            },
            {
                "file": "quorune/damage.py",
                "symbol": "commit",
                "kind": "assignment",
                "state_path": "players.life",
            },
            {
                "file": "quorune/trigger_processing.py",
                "symbol": "schedule_delayed_trigger",
                "kind": "mutating_call:append",
                "state_path": "delayed_triggers",
            },
            {
                "file": "quorune/zone_transitions.py",
                "symbol": "move_card",
                "kind": "assignment",
                "state_path": "cards.*.zone",
            },
            {
                "file": "quorune/unowned_fixture.py",
                "symbol": "commit",
                "kind": "assignment",
                "state_path": "players.life",
            },
        ]
        inventory = classify_state_writes(
            records,
            source=self.audit_source,
            policy=self.policy,
            baseline={},
            module_classifications={"modules": []},
        )
        self.assertEqual(inventory["writes_in_commander_engine"], 1)
        self.assertEqual(inventory["writes_in_canonical_owners"], 3)
        self.assertEqual(inventory["unowned_writes"], 1)
        self.assertEqual(
            {
                (row["file"], row["symbol"]): row["classification"]
                for row in inventory["locations"]
            },
            {
                ("quorune/engine.py", "_begin_turn"): (
                    "grandfathered_engine_debt"
                ),
                ("quorune/damage.py", "commit"): (
                    "canonical_mutation_owner_write"
                ),
                (
                    "quorune/trigger_processing.py",
                    "schedule_delayed_trigger",
                ): "canonical_mutation_owner_write",
                ("quorune/zone_transitions.py", "move_card"): (
                    "canonical_mutation_owner_write"
                ),
                ("quorune/unowned_fixture.py", "commit"): "unowned_write",
            },
        )

    def test_runtime_oracle_text_inventory_is_structural_and_non_growing(self):
        analyses = {
            "quorune/compiler/lowering.py": SimpleNamespace(
                tree=ast.parse("def lower(card):\n return card.oracle_text\n")
            ),
            "quorune/engine.py": SimpleNamespace(
                tree=ast.parse(
                    "def interpret(card):\n return card.get('oracle_text', '')\n"
                )
            ),
        }
        inventory = runtime_text_accesses(analyses)
        self.assertEqual(
            inventory["by_classification"],
            {"compiler_input": 1, "prohibited_runtime_interpretation": 1},
        )
        prohibited = inventory["prohibited_runtime_interpretation"][0]
        baseline = {
            "runtime_oracle_text_access_identities": [
                {
                    key: prohibited[key]
                    for key in ("file", "symbol", "access_kind", "member")
                }
            ]
        }
        self.assertEqual(runtime_text_growth(inventory, baseline), [])
        self.assertEqual(
            runtime_text_growth(
                inventory, {"runtime_oracle_text_access_identities": []}
            ),
            [
                {
                    "file": "quorune/engine.py",
                    "symbol": "interpret",
                    "access_kind": "mapping_get",
                    "member": "oracle_text",
                }
            ],
        )

    def test_every_prohibited_runtime_text_symbol_has_one_subsystem(self):
        source, _, analyses = analyze_production()
        inventory = runtime_text_accesses(analyses)
        assignments = _declared_runtime_text_subsystems(source, inventory)
        expected = {
            (str(row["file"]), str(row["symbol"]))
            for row in inventory["prohibited_runtime_interpretation"]
        }
        self.assertEqual(expected, set(assignments))
        declared_with_debt = {
            str(owner["id"])
            for owner in source["subsystem_ownership"]
            if owner.get("context", {}).get(
                "prohibited_runtime_oracle_text_symbols"
            )
        }
        self.assertEqual(
            declared_with_debt,
            set(assignments.values()),
        )

    def test_runtime_text_subsystem_attribution_rejects_drift(self):
        inventory = {
            "prohibited_runtime_interpretation": [
                {"file": "quorune/example.py", "symbol": "interpret"}
            ]
        }
        duplicate = {
            "subsystem_ownership": [
                {
                    "id": subsystem,
                    "context": {
                        "prohibited_runtime_oracle_text_symbols": [
                            {
                                "file": "quorune/example.py",
                                "symbol": "interpret",
                            }
                        ]
                    },
                }
                for subsystem in ("first", "second")
            ]
        }
        with self.assertRaisesRegex(ValueError, "multiple subsystems"):
            _declared_runtime_text_subsystems(duplicate, inventory)

        stale = {
            "subsystem_ownership": [
                {
                    "id": "example",
                    "context": {
                        "prohibited_runtime_oracle_text_symbols": [
                            {
                                "file": "quorune/example.py",
                                "symbol": "removed_interpreter",
                            }
                        ]
                    },
                }
            ]
        }
        with self.assertRaisesRegex(ValueError, "stale or not prohibited"):
            _declared_runtime_text_subsystems(stale, inventory)

    def test_raw_oracle_id_literal_ratchet_remains_independent(self):
        baseline = json.loads(
            (ROOT / "platform" / "architecture-guard-baseline.json").read_text(
                encoding="utf-8"
            )
        )
        relative = "quorune/engine.py"
        analyses = {
            relative: SimpleNamespace(
                tree=ast.parse("EXAMPLE = '11111111-1111-1111-1111-111111111111'"),
                functions=[],
            )
        }
        failures, metrics = _card_identity_failures(
            self.policy,
            baseline,
            {
                "card_specific_semantic_operations": [],
                "card_named_helpers": [],
            },
            analyses,
            {
                "oracle_id_literals": {
                    "locations": [
                        {
                            "file": relative,
                            "symbol": None,
                            "value": "11111111-1111-1111-1111-111111111111",
                            "oracle_id": "11111111-1111-1111-1111-111111111111",
                            "in_condition": False,
                        }
                    ]
                }
            },
            {
                "modules": [
                    {
                        "file": relative,
                        "owning_subsystem": "fixture",
                        "card_specificity_policy": "generic_no_growth",
                    }
                ]
            },
        )
        self.assertIn("oracle_id_literals", {row["guard"] for row in failures})
        self.assertEqual(0, metrics["prohibited_identity_dispatch_count"])


class CardIdentityFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = json.loads(
            (ROOT / "platform" / "architecture-policy.json").read_text(
                encoding="utf-8"
            )
        )

    def analyze(
        self,
        source: str,
        *,
        relative: str = "quorune/fixture.py",
        classification: dict[str, str] | None = None,
    ) -> dict[str, object]:
        return analyze_identity_source(
            source,
            relative=relative,
            architecture_policy=self.policy,
            module_classification=classification,
        )

    def assert_prohibited(self, source: str, *, minimum: int = 1) -> None:
        report = self.analyze(source)
        self.assertGreaterEqual(
            report["counts"]["prohibited_identity_dispatch_count"],
            minimum,
            report,
        )
        self.assertTrue(
            all(
                row["classification"] == PROHIBITED_CLASSIFICATION
                for row in report["prohibited_locations"]
            )
        )

    def assert_allowed(self, source: str, **kwargs: object) -> dict[str, object]:
        report = self.analyze(source, **kwargs)
        self.assertEqual(
            0,
            report["counts"]["prohibited_identity_dispatch_count"],
            report,
        )
        return report

    def test_ordinary_domain_and_arbitrary_card_name_literals_are_allowed(self):
        words = (
            "life",
            "stun",
            "vigilance",
            "reason",
            "exile",
            "sacrifice",
            "vehicle",
            "food",
            "map",
            "library",
            "hand",
            "counters",
        )
        source = "\n".join(
            [f"value_{index} = {word!r}" for index, word in enumerate(words)]
            + ["message = 'Black Lotus'"]
        )
        report = self.assert_allowed(source)
        self.assertEqual(0, report["counts"]["classified_flow_count"])

    def test_direct_reversed_and_stable_identity_dispatch_are_rejected(self):
        source = """
def direct(card):
    return card.printed_name == "Black Lotus"
def reversed(card):
    return "A Future Card Not Yet Printed" == card.printed_name
def oracle(card):
    return card.oracle_id == "00000000-0000-0000-0000-000000000000"
def collector(card):
    return card.collector_number == "123"
def edition(card):
    return card.set_code == "abc"
"""
        self.assert_prohibited(source, minimum=5)

    def test_alias_normalization_and_imported_static_identity_are_rejected(self):
        source = """
from fixture import FUTURE_NAME
SPECIAL_IDS = ("00000000-0000-0000-0000-000000000000",)
def alias(card):
    name = card.printed_name
    return name == "Black Lotus"
def normalized(card):
    name = card.printed_name.casefold().strip()
    return name == "black lotus"
def member(card):
    identity = card.oracle_id
    return identity in SPECIAL_IDS
def imported(card):
    return card.printed_name == FUTURE_NAME
"""
        self.assert_prohibited(source, minimum=4)

    def test_static_collections_match_and_concatenation_are_rejected(self):
        source = """
SPECIAL = ("Black Lotus",)
def collection(card):
    return card.printed_name in {"Black Lotus", "Ancestral Recall"}
def named(card):
    return card.printed_name in SPECIAL
def match_name(card):
    match card.printed_name:
        case "Black Lotus":
            return True
    return False
def concatenated(card):
    return card.printed_name == "Black " + "Lotus"
"""
        self.assert_prohibited(source, minimum=4)

    def test_static_implementation_maps_and_local_aliases_are_rejected(self):
        source = """
def by_name(card, state):
    HANDLERS[card.printed_name](state)
def aliased(card, state):
    table = HANDLERS
    handler = table.get(card.printed_name)
    handler(state)
def by_oracle(card):
    operation = OPERATIONS_BY_ORACLE_ID[card.oracle_id]
    execute(operation)
def capability(card):
    capability = CAPABILITIES_BY_NAME.get(card.printed_name)
    require(capability)
"""
        report = self.analyze(source)
        self.assertGreaterEqual(
            report["counts"]["prohibited_identity_dispatch_count"], 4, report
        )
        self.assertEqual(
            {"implementation_map_lookup"},
            {row["sink_kind"] for row in report["prohibited_locations"]},
        )

    def test_dynamic_typed_rules_name_data_is_allowed(self):
        source = """
def rules(candidate, predicate, descriptor):
    checks = (
        candidate.effective_name == predicate.exact_name,
        matches_name_predicate(candidate, predicate),
        NamePredicate(exact_name=descriptor["name"]),
        PartnerWithSpec(partner_name=descriptor.partner_name),
        MeldRelationship(other_face_name=descriptor.name),
    )
    return checks
"""
        self.assert_allowed(source)

    def test_compiler_self_reference_is_compiler_binding(self):
        source = """
def lower_self_reference(record: CardRecord, oracle_text: str):
    source_span = (0, len(oracle_text))
    lowered = oracle_text.replace(record.name, "this object")
    return {"source_ref": "self", "span": source_span, "text": lowered}
"""
        report = self.assert_allowed(
            source, relative="quorune/compiler/self_reference_fixture.py"
        )
        self.assertIn(
            "compiler_binding", report["counts"]["by_classification"]
        )

    def test_compiler_fixed_card_dispatch_is_rejected_but_face_binding_is_allowed(self):
        prohibited = self.analyze(
            "def lower(card):\n return card.printed_name == 'Black Lotus'\n",
            relative="quorune/compiler/fixture.py",
        )
        self.assertEqual(
            1, prohibited["counts"]["prohibited_identity_dispatch_count"]
        )
        face = self.assert_allowed(
            "def lower(card):\n return card.active_face in {'front', 'back'}\n",
            relative="quorune/compiler/fixture.py",
        )
        self.assertIn("compiler_binding", face["counts"]["by_classification"])

    def test_flow_identity_does_not_depend_on_line_numbers(self):
        source = "def dispatch(card):\n return card.oracle_id == 'fixed-id'\n"
        compact = self.analyze(source)
        spaced = self.analyze("\n\n" + source.replace("\n ", "\n\n "))
        with_unrelated_flow = self.analyze(
            "def dispatch(card):\n projected = card.set_code\n"
            " return card.oracle_id == 'fixed-id'\n"
        )
        self.assertEqual(
            compact["prohibited_locations"][0]["flow_id"],
            spaced["prohibited_locations"][0]["flow_id"],
        )
        self.assertEqual(
            compact["prohibited_locations"][0]["flow_id"],
            with_unrelated_flow["prohibited_locations"][0]["flow_id"],
        )

    def test_display_and_generated_provenance_identity_are_allowed(self):
        projection = self.assert_allowed(
            "def project(card):\n return {'name': card.printed_name}\n",
            relative="quorune/projection.py",
        )
        self.assertIn(
            "display_metadata", projection["counts"]["by_classification"]
        )
        provenance = self.assert_allowed(
            "def build_inventory(card):\n return {'oracle_id': card.oracle_id}\n",
            relative="quorune/reporting_fixture.py",
        )
        self.assertIn(
            "generated_provenance", provenance["counts"]["by_classification"]
        )

    def test_historical_compatibility_is_exactly_classified(self):
        source = "def adapt(card):\n return card.oracle_id == 'legacy-id'\n"
        historical = self.assert_allowed(
            source,
            relative="quorune/card_overrides/game_record_v3_fixture.py",
            classification={
                "owning_subsystem": "game_record_compatibility",
                "card_specificity_policy": "explicit_card_override",
            },
        )
        self.assertIn(
            "reviewed_historical_compatibility",
            historical["counts"]["by_classification"],
        )
        self.assert_prohibited(source)

    def test_reviewed_override_is_exactly_classified(self):
        source = "def dispatch(card):\n return card.printed_name == 'Black Lotus'\n"
        override = self.assert_allowed(
            source,
            relative="quorune/card_overrides/fixture.py",
            classification={
                "owning_subsystem": "reviewed_card_overrides",
                "card_specificity_policy": "explicit_card_override",
            },
        )
        self.assertIn("reviewed_override", override["counts"]["by_classification"])
        self.assert_prohibited(source)

    def test_analyzer_has_no_database_or_lexical_artifact_dependency(self):
        report = self.assert_allowed("message = 'Black Lotus'\n")
        self.assertEqual(
            {
                "card_database": False,
                "card_name_index": False,
                "specificity_baseline": False,
            },
            report["external_dependencies"],
        )
        module_source = (
            ROOT / "scripts" / "architecture_identity_flow.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("sqlite3", module_source)
        self.assertNotIn("card-name-hash-index", module_source)
        self.assertNotIn("card-specificity-baseline", module_source)

    def test_current_production_tree_has_zero_prohibited_dispatches(self):
        _source, _paths, analyses = analyze_production()
        classifications = json.loads(
            (ROOT / "platform" / "module-classifications.json").read_text(
                encoding="utf-8"
            )
        )
        report = analyze_identity_flows(
            analyses, self.policy, classifications
        )
        self.assertEqual([], report["prohibited_locations"])
        self.assertEqual(
            0, report["counts"]["prohibited_identity_dispatch_count"]
        )


if __name__ == "__main__":
    unittest.main()
