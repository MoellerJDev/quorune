from __future__ import annotations

import copy
from dataclasses import FrozenInstanceError, replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from common import ROOT, keep_all, make_session
from quorune.carddb import CardDatabase
from quorune import damage_results, tap_state
from quorune.compiler.regeneration_templates import (
    self_regeneration_effect_template,
)
from quorune.deck import DeckLoader
from quorune.destruction import (
    commit_destruction_plan,
    DestructionCause,
    DestructionDisposition,
    DestructionError,
    destroy_permanent_refs,
    prepare_destructions,
    request_for_card,
)
from quorune.model import CardInstance
from quorune.oracle_ir import (
    compile_oracle_card,
    generated_programs,
    register_generated_programs,
)
from quorune.permanent_exile import exile_permanent
from quorune.record import (
    authoritative_state_hash,
    checkpoint_envelope,
    replay_record,
)
from quorune.regeneration import create_regeneration_shield
from quorune.rules.capabilities import (
    CapabilityRegistry,
    load_default_capability_registry,
)
from quorune.rules.node_capability_shapes import (
    self_regeneration_node_capabilities,
)
from quorune.semantic_runtime.context import (
    ReadOnlyHandlerContext,
    ReadOnlyRulesQuery,
    SemanticNodeError,
    SemanticSourceContext,
)
from quorune.semantic_runtime.intents import CreateRegenerationShieldIntent
from quorune.semantic_runtime.regeneration_handlers import (
    CreateRegenerationShieldHandler,
)
from scripts.build_test_database import build_fixture_database


REGISTRY_PATH = ROOT / "quorune" / "rules" / "capability-registry.json"


def focused_card_database(directory: str) -> CardDatabase:
    database = Path(directory) / "regeneration-rules.sqlite3"
    build_fixture_database(
        [
            ROOT / "tests" / "fixtures" / "scryfall-exact-lists.json",
            ROOT / "tests" / "fixtures" / "regeneration-cards.json",
        ],
        database,
    )
    return CardDatabase(database)


class RegenerationCompilerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.capabilities = load_default_capability_registry()
        cls.registry_value = json.loads(
            REGISTRY_PATH.read_text(encoding="utf-8")
        )
        cls.temporary = tempfile.TemporaryDirectory()
        cls.db = focused_card_database(cls.temporary.name)
        cls.record = cls.db.lookup("Drudge Skeletons")

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        cls.temporary.cleanup()

    def test_exact_self_regeneration_compiles_and_harvests_frontier(self):
        ir = compile_oracle_card(
            self.record,
            capability_registry=self.capabilities,
            capability_profile="commander_review",
        )
        node = next(
            node
            for face in ir.faces
            for node in face.nodes
            if node.template_id == "regenerate-this-creature-v1"
        )
        self.assertEqual("exact", ir.status)
        self.assertEqual("activated_ability", node.kind)
        self.assertEqual(1, node.span.line)
        self.assertEqual(
            node.text,
            self.record.oracle_text[node.span.start : node.span.end],
        )
        self.assertEqual(
            ({"op": "regenerate", "card": "$source.zone_object"},),
            node.effects,
        )
        self.assertEqual(
            ("permanent.regeneration.self_activation",),
            node.capability_dependencies,
        )
        self.assertEqual(1, node.cost["mana"]["B"])
        program = next(
            program
            for program in generated_programs(
                self.db,
                self.record,
                trust_level="trusted",
                capability_registry=self.capabilities,
                capability_profile="commander_review",
            )
            if program.provenance.get("template_id")
            == "regenerate-this-creature-v1"
        )
        self.assertTrue(program.capability_closure["trusted"])
        self.assertFalse(program.requires_arbiter)

    def test_handler_is_versioned_immutable_source_pinned_and_strict(self):
        context = ReadOnlyHandlerContext(
            actor="A",
            default_reason="regeneration fixture",
            query=ReadOnlyRulesQuery(
                seats=("A", "B", "C", "D"),
                active_seats=("A", "B", "C", "D"),
                apnap_order=("B", "C", "D", "A"),
            ),
            source=SemanticSourceContext(
                stack_ref="S-regenerate",
                object_id="fixture:regenerator",
                logical_object_id="logical:regenerator:1",
                card_ref="A-regenerator",
            ),
        )
        handler = CreateRegenerationShieldHandler()
        plan = handler.lower(
            {"op": "regenerate", "card": "A-regenerator"},
            context,
        )
        self.assertEqual(1, handler.schema_version)
        self.assertEqual("generic.create-regeneration-shield.v1", plan.handler_id)
        self.assertEqual(
            (
                CreateRegenerationShieldIntent(
                    actor="A",
                    object_ref="A-regenerator",
                    logical_object_id="logical:regenerator:1",
                    reason="regeneration fixture",
                ),
            ),
            plan.intents,
        )
        with self.assertRaises(FrozenInstanceError):
            plan.intents[0].reason = "mutated"  # type: ignore[misc]
        for malformed in (
            {"op": "regenerate", "card": ""},
            {"op": "regenerate", "card": "A-regenerator", "reason": 4},
            {"op": "regenerate", "card": "A-regenerator", "future": True},
            {
                "op": "regenerate",
                "card": "A-regenerator",
                "_replacement_selections": ["replacement-a"],
            },
        ):
            with self.subTest(effect=malformed):
                with self.assertRaises(SemanticNodeError):
                    handler.lower(malformed, context)
        mismatched = replace(
            context,
            source=replace(context.source, card_ref="A-other"),
        )
        with self.assertRaisesRegex(SemanticNodeError, "current source"):
            handler.lower(
                {"op": "regenerate", "card": "A-regenerator"},
                mismatched,
            )

    def test_unsupported_regeneration_grammar_remains_residual(self):
        variants = (
            "{B}: Regenerate this creature",
            "{B}: Regenerate target creature.",
            "{B}: Regenerate this permanent.",
            "{B}: Regenerate another creature.",
            "{B}: Regenerate this creature twice.",
            "{B}: Regenerate this creature only if it attacked this turn.",
        )
        for text in variants:
            with self.subTest(text=text):
                effect = text.split(":", 1)[-1].strip()
                self.assertIsNone(self_regeneration_effect_template(effect))
                ir = compile_oracle_card(
                    replace(self.record, oracle_text=text),
                    capability_registry=self.capabilities,
                    capability_profile="commander_review",
                )
                self.assertNotEqual("exact", ir.status)
                self.assertTrue(ir.material_residuals)

        static_ir = compile_oracle_card(
            replace(self.record, oracle_text="Regenerate this creature."),
            capability_registry=self.capabilities,
            capability_profile="commander_review",
        )
        self.assertNotEqual("exact", static_ir.status)
        self.assertTrue(static_ir.material_residuals)

    def test_regeneration_shape_and_dependency_mutants_fail_closed(self):
        effect = ({"op": "regenerate", "card": "$source.zone_object"},)
        self.assertEqual(
            ("permanent.regeneration.self_activation",),
            self_regeneration_node_capabilities(
                effects=effect,
                target_schema=None,
                mechanic_ids=("regenerate",),
            ),
        )
        for effects, target_schema, mechanics in (
            (({**effect[0], "future": True},), None, ("regenerate",)),
            (({"op": "regenerate", "card": "$source"},), None, ("regenerate",)),
            (effect, {"count": 1}, ("regenerate",)),
            (effect, None, ("regenerate", "destroy")),
        ):
            with self.subTest(effects=effects):
                self.assertEqual(
                    (),
                    self_regeneration_node_capabilities(
                        effects=effects,
                        target_schema=target_schema,
                        mechanic_ids=mechanics,
                    ),
                )

        def assert_exact(registry):
            result = compile_oracle_card(
                self.record,
                capability_registry=registry,
                capability_profile="commander_review",
            )
            self.assertEqual("exact", result.status)

        assert_exact(self.capabilities)
        with patch(
            "quorune.compiler.activated_mana_nodes."
            "self_regeneration_effect_template",
            return_value=None,
        ):
            with self.assertRaises(AssertionError):
                assert_exact(self.capabilities)

        value = json.loads(json.dumps(self.registry_value))
        dependency = next(
            row
            for row in value["capabilities"]
            if row["id"] == "permanent.destroy.effect"
        )
        dependency["status"] = "blocked"
        dependency["blockers"] = ["test mutation"]
        blocked = compile_oracle_card(
            self.record,
            capability_registry=CapabilityRegistry(value),
            capability_profile="commander_review",
        )
        self.assertNotEqual("exact", blocked.status)
        self.assertTrue(
            any(
                "permanent.destroy.effect" in blocker
                for residual in blocked.material_residuals
                for blocker in residual.blockers
            )
        )


class RegenerationRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.capabilities = load_default_capability_registry()
        cls.temporary = tempfile.TemporaryDirectory()
        cls.db = focused_card_database(cls.temporary.name)
        loader = DeckLoader(cls.db)
        cls.mishra = loader.load(
            ROOT / "examples" / "mishra-eminent-one.txt",
            commander="Mishra, Eminent One",
            deck_name="Mishra",
        )
        cls.zimone = loader.load(
            ROOT / "examples" / "zimone-and-dina.txt",
            commander="Zimone and Dina",
            deck_name="Zimone",
        )

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        cls.temporary.cleanup()

    def session(self, seed: int, *, players: int = 2):
        session = make_session(
            self.db,
            copy.deepcopy(self.mishra),
            copy.deepcopy(self.zimone),
            players=players,
            seed=seed,
            auto_pass_empty=False,
        )
        keep_all(session)
        engine = session.engine
        engine.permissions.invalidate_current()
        engine.state.pending_decision = None
        engine.state.priority_player = None
        engine.state.priority_passes = []
        session.commands.clear()
        session.decisions.clear()
        return session

    def add_skeleton(self, session, *, ref: str = "A-regenerator"):
        engine = session.engine
        record = self.db.lookup("Drudge Skeletons")
        card = CardInstance(
            object_id=f"fixture:{ref}",
            ref=ref,
            oracle_id=record.oracle_id,
            printed_name=record.name,
            owner="A",
            controller="A",
            zone="battlefield",
            zone_timestamp=engine.state.event_sequence + 1,
            acquired_control_turn_count=-1,
            known_to=list(engine.seats),
            revealed_to=list(engine.seats),
        )
        engine.state.cards[card.object_id] = card
        engine.state.players["A"].zones["battlefield"].append(card.object_id)
        register_generated_programs(
            self.db,
            engine.semantics,
            (record,),
            trust_level="provisional",
            capability_registry=self.capabilities,
            capability_profile=engine.state.config.review_profile,
            promote_exact_runtime_handlers=True,
            promote_exact_effect_programs=True,
        )
        return card

    @staticmethod
    def prepare_priority(session):
        engine = session.engine
        engine.state.active_player = "A"
        engine.state.started = True
        engine.state.phase = "precombat_main"
        engine.state.step = "main"
        engine.state.stack.clear()
        engine.state.priority_passes = []
        engine.state.pending_decision = None
        engine.state.priority_player = None
        engine.permissions.invalidate_current()
        engine._grant_priority("A")
        engine.pump()

    @staticmethod
    def pass_until_resolved(session):
        for _ in range(24):
            if not session.state.stack:
                return
            principals = session.pending_principals()
            if not principals:
                raise AssertionError("Resolution stopped without a decision")
            result = session.act(principals[0], {"action_id": "pass"})
            if not result.ok:
                raise AssertionError(result.summary)
        raise AssertionError("Regeneration activation did not resolve")

    def assert_replays(self, session):
        expected_hash = authoritative_state_hash(session.state)
        with tempfile.TemporaryDirectory() as temporary:
            record_dir = Path(temporary) / "regeneration-record"
            session.save(record_dir)
            replay = replay_record(record_dir, self.db, verify=True)
        self.assertTrue(replay["ok"], replay)
        self.assertEqual(expected_hash, replay["final_state_hash"])

    def test_activation_creates_public_shield_and_replays(self):
        unpayable = self.session(7011900, players=4)
        unpayable_source = self.add_skeleton(unpayable)
        self.prepare_priority(unpayable)
        unpayable_action = f"activate:{unpayable_source.ref}:ab1"
        unpayable_offers = {
            action["id"]
            for action in unpayable.packet("pilot:A", full=True)["decision"][
                "ctx"
            ]["legal"]["actions"]
        }
        self.assertNotIn(unpayable_action, unpayable_offers)
        before_unpayable = authoritative_state_hash(unpayable.state)
        rejected = unpayable.act(
            "pilot:A",
            {"action_id": unpayable_action},
        )
        self.assertFalse(rejected.ok)
        self.assertEqual(
            before_unpayable,
            authoritative_state_hash(unpayable.state),
        )

        session = self.session(7011901, players=4)
        source = self.add_skeleton(session)
        session.state.players["A"].mana_pool["B"] = 1
        self.prepare_priority(session)
        action_id = f"activate:{source.ref}:ab1"
        offered = {
            action["id"]
            for action in session.packet("pilot:A", full=True)["decision"][
                "ctx"
            ]["legal"]["actions"]
        }
        self.assertIn(action_id, offered)
        session.initial_checkpoint = checkpoint_envelope(session.state)
        session.commands.clear()
        session.decisions.clear()

        result = session.act("pilot:A", {"action_id": action_id})
        self.assertTrue(result.ok, result.summary)
        self.assertEqual(1, len(session.state.stack))
        self.assertEqual(source.object_id, session.state.stack[-1].source_object_id)
        self.pass_until_resolved(session)

        self.assertEqual(1, source.regeneration_shields)
        self.assertEqual(0, session.state.players["A"].mana_pool["B"])
        for principal in ("pilot:A", "pilot:B", "pilot:C", "pilot:D"):
            projected = session.packet(principal, full=True)["state"]
            public = next(
                card
                for card in projected["players"]["A"]["bf"]
                if card["id"] == source.ref
            )
            self.assertEqual(1, public["regen"])
        self.assert_replays(session)

    def test_regeneration_replaces_effect_and_state_based_destruction(self):
        session = self.session(7011902, players=3)
        engine = session.engine
        source = self.add_skeleton(session)
        create_regeneration_shield(
            engine,
            source.ref,
            actor="A",
            reason="effect witness",
            logical_object_id=source.logical_object_id,
        )
        create_regeneration_shield(
            engine,
            source.ref,
            actor="A",
            reason="second effect witness",
            logical_object_id=source.logical_object_id,
        )
        engine.change_control(
            source.object_id,
            "C",
            reason="regeneration control-change witness",
        )

        effect = destroy_permanent_refs(
            engine,
            (source.ref,),
            actor="B",
            reason="effect destruction witness",
        )
        self.assertEqual((source.object_id,), effect.regenerated_object_ids)
        self.assertEqual("battlefield", source.zone)
        self.assertEqual("C", source.controller)
        self.assertEqual(1, source.regeneration_shields)

        source.marked_damage = 1
        source.deathtouch_damage = True
        plan = prepare_destructions(
            engine,
            (request_for_card(source),),
            cause=DestructionCause.STATE_BASED_ACTION,
            actor=None,
            reason="lethal damage state-based action",
        )
        self.assertEqual(
            DestructionDisposition.REGENERATION,
            plan.entries[0].disposition,
        )
        state_based = commit_destruction_plan(engine, plan)
        self.assertEqual(
            (source.object_id,), state_based.regenerated_object_ids
        )
        self.assertEqual("battlefield", source.zone)
        self.assertEqual(0, source.marked_damage)
        self.assertFalse(source.deathtouch_damage)

    def test_regeneration_taps_clears_damage_and_removes_from_combat(self):
        session = self.session(7011903, players=4)
        engine = session.engine
        source = self.add_skeleton(session)
        source.marked_damage = 8
        source.deathtouch_damage = True
        source.attacking = "C"
        engine.state.combat.attackers[source.object_id] = "C"
        engine.state.combat.attack_target_context[source.object_id] = {
            "defender": "C",
            "target_kind": "player",
        }
        create_regeneration_shield(
            engine,
            source.ref,
            actor="A",
            reason="combat witness",
            logical_object_id=source.logical_object_id,
        )

        with (
            patch(
                "quorune.regeneration.tap_state.set_permanent_tapped",
                wraps=tap_state.set_permanent_tapped,
            ) as tap_owner,
            patch(
                "quorune.regeneration.damage_results.clear_permanent_damage",
                wraps=damage_results.clear_permanent_damage,
            ) as damage_owner,
            patch.object(
                engine,
                "_remove_object_from_combat",
                wraps=engine._remove_object_from_combat,
            ) as combat_owner,
        ):
            result = destroy_permanent_refs(
                engine,
                (source.ref,),
                actor="D",
                reason="combat destruction witness",
            )

        tap_owner.assert_called_once()
        damage_owner.assert_called_once()
        combat_owner.assert_called_once()

        self.assertEqual((source.object_id,), result.regenerated_object_ids)
        self.assertTrue(source.tapped)
        self.assertEqual(0, source.marked_damage)
        self.assertFalse(source.deathtouch_damage)
        self.assertIsNone(source.attacking)
        self.assertNotIn(source.object_id, engine.state.combat.attackers)
        self.assertIn(
            "combat.remove", [event.code for event in engine.state.events]
        )

    def test_regeneration_shields_expire_at_cleanup_and_zone_change(self):
        session = self.session(7011904)
        engine = session.engine
        source = self.add_skeleton(session)
        for _ in range(2):
            create_regeneration_shield(
                engine,
                source.ref,
                actor="A",
                reason="cleanup witness",
                logical_object_id=source.logical_object_id,
            )
        self.assertEqual(2, source.regeneration_shields)

        engine._finish_cleanup()
        self.assertEqual(0, source.regeneration_shields)

        create_regeneration_shield(
            engine,
            source.ref,
            actor="A",
            reason="zone-change witness",
            logical_object_id=source.logical_object_id,
        )
        engine.move_card(source.object_id, "graveyard", log=False)
        self.assertEqual(0, source.regeneration_shields)
        self.assertNotIn("regeneration_shields", source.to_dict())
        prior_incarnation = source.logical_object_id
        engine.move_card(source.object_id, "battlefield", log=False)
        self.assertNotEqual(prior_incarnation, source.logical_object_id)
        create_regeneration_shield(
            engine,
            source.ref,
            actor="A",
            reason="stale incarnation witness",
            logical_object_id=prior_incarnation,
        )
        self.assertEqual(0, source.regeneration_shields)

    def test_regeneration_does_not_replace_sacrifice_exile_or_zero_toughness(self):
        sacrifice = self.session(7011907)
        sacrificed = self.add_skeleton(sacrifice, ref="A-sacrifice")
        create_regeneration_shield(
            sacrifice.engine,
            sacrificed.ref,
            actor="A",
            reason="sacrifice distinction",
            logical_object_id=sacrificed.logical_object_id,
        )
        sacrifice.engine.apply_effect(
            {"op": "sacrifice", "card": sacrificed.ref},
            actor="A",
        )
        self.assertEqual("graveyard", sacrificed.zone)
        self.assertEqual(0, sacrificed.regeneration_shields)

        exile = self.session(7011908)
        exiled = self.add_skeleton(exile, ref="A-exile")
        create_regeneration_shield(
            exile.engine,
            exiled.ref,
            actor="A",
            reason="exile distinction",
            logical_object_id=exiled.logical_object_id,
        )
        exile_permanent(
            exile.engine,
            exiled.ref,
            actor="B",
            reason="exile distinction",
        )
        self.assertEqual("exile", exiled.zone)
        self.assertEqual(0, exiled.regeneration_shields)

        zero = self.session(7011909)
        zero_toughness = self.add_skeleton(zero, ref="A-zero")
        create_regeneration_shield(
            zero.engine,
            zero_toughness.ref,
            actor="A",
            reason="zero-toughness distinction",
            logical_object_id=zero_toughness.logical_object_id,
        )
        zero_toughness.annotations["copy_overrides"] = {
            "name": zero_toughness.printed_name,
            "type_line": "Creature — Skeleton",
            "power": "1",
            "toughness": "0",
        }
        zero.engine._stabilize()
        self.assertEqual("graveyard", zero_toughness.zone)
        self.assertEqual(0, zero_toughness.regeneration_shields)

    def test_stale_and_competing_replacements_fail_before_mutation(self):
        session = self.session(7011905)
        engine = session.engine
        source = self.add_skeleton(session)
        create_regeneration_shield(
            engine,
            source.ref,
            actor="A",
            reason="stale witness",
            logical_object_id=source.logical_object_id,
        )
        plan = prepare_destructions(
            engine,
            (request_for_card(source),),
            cause=DestructionCause.EFFECT,
            actor="B",
            reason="stale destruction witness",
        )
        source.regeneration_shields += 1
        before_stale = authoritative_state_hash(engine.state)
        with self.assertRaisesRegex(DestructionError, "stale"):
            commit_destruction_plan(engine, plan)
        self.assertEqual(before_stale, authoritative_state_hash(engine.state))

        source.regeneration_shields = 1
        source.counters["shield"] = 1
        before_choice = authoritative_state_hash(engine.state)
        with self.assertRaisesRegex(DestructionError, "affected-player choice"):
            prepare_destructions(
                engine,
                (request_for_card(source),),
                cause=DestructionCause.EFFECT,
                actor="B",
                reason="competing replacement witness",
            )
        self.assertEqual(before_choice, authoritative_state_hash(engine.state))

        source.temporary_keywords.append("indestructible")
        protected = prepare_destructions(
            engine,
            (request_for_card(source),),
            cause=DestructionCause.EFFECT,
            actor="B",
            reason="Indestructible witness",
        )
        self.assertEqual(
            DestructionDisposition.INDESTRUCTIBLE,
            protected.entries[0].disposition,
        )

    def test_regeneration_disposition_mutant_is_killed(self):
        session = self.session(7011906)
        engine = session.engine
        source = self.add_skeleton(session)
        create_regeneration_shield(
            engine,
            source.ref,
            actor="A",
            reason="disposition witness",
            logical_object_id=source.logical_object_id,
        )
        with patch(
            "quorune.destruction._destruction_disposition",
            return_value=DestructionDisposition.DESTROY,
        ):
            with self.assertRaises(AssertionError):
                self.assertEqual(
                    DestructionDisposition.REGENERATION,
                    prepare_destructions(
                        engine,
                        (request_for_card(source),),
                        cause=DestructionCause.EFFECT,
                        actor="B",
                        reason="disposition mutation witness",
                    ).entries[0].disposition,
                )


if __name__ == "__main__":
    unittest.main()
