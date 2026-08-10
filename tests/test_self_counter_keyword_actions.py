from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from common import ROOT, keep_all, make_session
from quorune.carddb import CardDatabase
from quorune.compiler.self_counter_keyword_actions import (
    SelfCounterKeywordAction,
    fixed_self_counter_keyword_action_template,
)
from quorune.deck import DeckLoader
from quorune.errors import GameRuleError
from quorune.model import CardInstance
from quorune.object_query import ObjectQueryResult
from quorune.oracle_ir import compile_oracle_card, register_generated_programs
from quorune.permanent_designations import (
    BecomeMonstrousRequest,
    PermanentDesignationError,
    become_monstrous,
)
from quorune.projection import StateProjector
from quorune.record import (
    authoritative_state_hash,
    checkpoint_envelope,
    replay_record,
)
from quorune.replacement.immutable import FrozenMap
from quorune.rules.capabilities import (
    CapabilityRegistry,
    capability_dependencies_for_node,
    load_default_capability_registry,
)
from quorune.rules.node_capability_shapes import (
    fixed_self_counter_keyword_action_node_capabilities,
)
from quorune.semantic_choices.context import (
    SemanticChoiceContext,
    SnapshotSemanticChoiceQuery,
)
from quorune.semantic_choices.self_counter_keyword_actions import (
    FixedSelfCounterKeywordActionHandler,
)
from quorune.semantic_runtime import BecomeMonstrousIntent, PlaceCountersIntent
from quorune.session import CommanderSession
from scripts.build_test_database import build_fixture_database


REGISTRY_PATH = ROOT / "quorune" / "rules" / "capability-registry.json"


def focused_card_database(directory: str) -> CardDatabase:
    database = Path(directory) / "self-counter-keyword-actions.sqlite3"
    build_fixture_database(
        [
            ROOT / "tests" / "fixtures" / "scryfall-exact-lists.json",
            ROOT / "tests" / "fixtures" / "counter-replacement-cards.json",
            ROOT / "tests" / "fixtures" / "self-counter-keyword-actions.json",
        ],
        database,
    )
    return CardDatabase(database)


def object_row(
    *,
    counters: dict[str, int] | None = None,
    monstrous_value: int | None = None,
    logical_object_id: str = "logical:source",
    zone: str = "battlefield",
    phased_out: bool = False,
) -> ObjectQueryResult:
    return ObjectQueryResult(
        object_id="fixture:source",
        logical_object_id=logical_object_id,
        ref="A-source",
        printed_name="Source fixture",
        owner="A",
        controller="A",
        zone=zone,
        types=("creature",),
        counters=FrozenMap(counters or {}),
        phased_out=phased_out,
        monstrous_value=monstrous_value,
    )


def choice_context(row: ObjectQueryResult) -> SemanticChoiceContext:
    return SemanticChoiceContext(
        actor="A",
        stack_ref="S1",
        stack_controller="A",
        stack_label="Fixed keyword action",
        source_ref=row.ref,
        card_ref=None,
        semantic_program_id="fixture:self-counter-action",
        semantic_program_version=1,
        query=SnapshotSemanticChoiceQuery(
            seat_order=("A", "B"),
            active_order=("A", "B"),
            object_rows=(row,),
            libraries_by_seat=FrozenMap({"A": (), "B": ()}),
        ),
        source_logical_object_id="logical:source",
    )


class FixedSelfCounterKeywordCompilerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.db = focused_card_database(cls.temporary.name)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        cls.temporary.cleanup()

    def test_fixed_templates_and_shapes_are_closed(self):
        expected = (
            (
                "Adapt 2.",
                SelfCounterKeywordAction.ADAPT,
                2,
                "keyword_action.adapt.fixed",
            ),
            (
                "Monstrosity three.",
                SelfCounterKeywordAction.MONSTROSITY,
                3,
                "keyword_action.monstrosity.fixed",
            ),
        )
        for text, action, amount, capability in expected:
            with self.subTest(text=text):
                template = fixed_self_counter_keyword_action_template(text)
                self.assertIsNotNone(template)
                assert template is not None
                self.assertIs(template.action, action)
                self.assertEqual(amount, template.amount)
                self.assertEqual(
                    (capability,),
                    fixed_self_counter_keyword_action_node_capabilities(
                        effects=template.effects,
                        target_schema=None,
                        mechanic_ids=template.mechanics,
                    ),
                )

    def test_unsupported_adapt_and_monstrosity_variants_remain_residuals(self):
        for text in (
            "Adapt 0.",
            "Adapt X.",
            "Adapt 2 twice.",
            "Target creature adapts 2.",
            "Adapt 2, then draw a card.",
            "Monstrosity 0.",
            "Monstrosity X.",
            "Monstrosity 3, then it fights target creature.",
            "It becomes monstrous.",
        ):
            with self.subTest(text=text):
                self.assertIsNone(
                    fixed_self_counter_keyword_action_template(text)
                )

    def test_self_counter_keyword_shape_rejects_malformed_nodes(self):
        valid = {
            "op": "fixed_self_counter_keyword_action",
            "action": "adapt",
            "amount": 2,
            "source": "$source",
        }
        for mutation, mechanics in (
            ({**valid, "amount": 0}, ("adapt", "cr-122-counters")),
            ({**valid, "amount": True}, ("adapt", "cr-122-counters")),
            ({**valid, "source": "$target.0"}, ("adapt", "cr-122-counters")),
            ({**valid, "action": "monstrosity"}, ("adapt", "cr-122-counters")),
            ({**valid, "extra": 1}, ("adapt", "cr-122-counters")),
            (valid, ("adapt",)),
        ):
            with self.subTest(mutation=mutation, mechanics=mechanics):
                self.assertEqual(
                    (),
                    fixed_self_counter_keyword_action_node_capabilities(
                        effects=(mutation,),
                        target_schema=None,
                        mechanic_ids=mechanics,
                    ),
                )

    def _assert_compiled(
        self,
        name: str,
        *,
        template_id: str,
        capability_id: str,
        action: str,
        amount: int,
    ) -> None:
        ir = compile_oracle_card(
            self.db.lookup(name),
            capability_registry=load_default_capability_registry(),
            capability_profile="commander_review",
        )
        node = next(
            value
            for value in ir.faces[0].nodes
            if value.template_id == template_id
        )
        self.assertEqual("exact", ir.status)
        self.assertEqual("activated_ability", node.kind)
        self.assertEqual(
            {
                "op": "fixed_self_counter_keyword_action",
                "action": action,
                "amount": amount,
                "source": "$source",
            },
            node.effects[0],
        )
        self.assertIn(capability_id, node.capability_dependencies)
        text = self.db.lookup(name).oracle_text
        source_text = text[node.span.start : node.span.end]
        self.assertEqual(text.splitlines()[-1], source_text)
        self.assertIn(f"{action.title()} {amount}.", source_text)

    def test_fixed_adapt_compiles_source_spanned_and_capability_closed(self):
        self._assert_compiled(
            "Aeromunculus",
            template_id="keyword-action-adapt-fixed-v1",
            capability_id="keyword_action.adapt.fixed",
            action="adapt",
            amount=1,
        )

    def test_fixed_monstrosity_compiles_source_spanned_and_capability_closed(self):
        self._assert_compiled(
            "Gluttonous Cyclops",
            template_id="keyword-action-monstrosity-fixed-v1",
            capability_id="keyword_action.monstrosity.fixed",
            action="monstrosity",
            amount=3,
        )

    def test_compiler_dependencies_fail_closed(self):
        payload = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        for dependency in (
            "counter.placement.quantity_replacement",
            "permanent.designation.monstrous",
        ):
            with self.subTest(dependency=dependency):
                mutated = json.loads(json.dumps(payload))
                row = next(
                    value
                    for value in mutated["capabilities"]
                    if value["id"] == dependency
                )
                row["status"] = "blocked"
                row["blockers"] = ["test mutation"]
                registry = CapabilityRegistry(mutated)
                registry.mark_evidence_verified("0" * 64)
                ir = compile_oracle_card(
                    self.db.lookup("Gluttonous Cyclops"),
                    capability_registry=registry,
                    capability_profile="commander_review",
                )
                self.assertNotEqual("exact", ir.status)
                self.assertTrue(
                    any(
                        dependency in blocker
                        for residual in ir.material_residuals
                        for blocker in residual.blockers
                    )
                )

    def test_self_counter_keyword_compiler_mutant_is_killed(self):
        with patch(
            "quorune.compiler.resolution_effect_templates."
            "fixed_self_counter_keyword_action_template",
            return_value=None,
        ):
            ir = compile_oracle_card(
                self.db.lookup("Aeromunculus"),
                capability_registry=load_default_capability_registry(),
                capability_profile="commander_review",
            )
        self.assertNotEqual("exact", ir.status)
        self.assertTrue(ir.material_residuals)


class FixedSelfCounterKeywordRuleTests(unittest.TestCase):
    def setUp(self):
        self.handler = FixedSelfCounterKeywordActionHandler()

    def test_adapt_condition_is_checked_only_on_resolution(self):
        available = self.handler.prepare(
            {
                "op": self.handler.operation,
                "action": "adapt",
                "amount": 2,
                "source": "A-source",
            },
            choice_context(object_row()),
        )
        self.assertEqual((PlaceCountersIntent,), tuple(
            type(intent) for intent in available.preparation_intents
        ))

        blocked = self.handler.prepare(
            {
                "op": self.handler.operation,
                "action": "adapt",
                "amount": 2,
                "source": "A-source",
            },
            choice_context(object_row(counters={"+1/+1": 1})),
        )
        self.assertEqual((), blocked.preparation_intents)
        self.assertIn("already has", blocked.auto_continue.reason)

    def test_monstrosity_prepares_counter_then_designation(self):
        preparation = self.handler.prepare(
            {
                "op": self.handler.operation,
                "action": "monstrosity",
                "amount": 3,
                "source": "A-source",
            },
            choice_context(object_row()),
        )
        self.assertEqual(
            (PlaceCountersIntent, BecomeMonstrousIntent),
            tuple(type(intent) for intent in preparation.preparation_intents),
        )
        self.assertEqual(3, preparation.preparation_intents[1].value)

        already = self.handler.prepare(
            {
                "op": self.handler.operation,
                "action": "monstrosity",
                "amount": 3,
                "source": "A-source",
            },
            choice_context(object_row(monstrous_value=3)),
        )
        self.assertEqual((), already.preparation_intents)

    def test_handler_rejects_malformed_or_stale_values(self):
        valid = {
            "op": self.handler.operation,
            "action": "adapt",
            "amount": 2,
            "source": "A-source",
        }
        for mutation in (
            {**valid, "amount": True},
            {**valid, "amount": 0},
            {**valid, "action": "evolve"},
            {**valid, "source": "B-source"},
            {**valid, "extra": 1},
        ):
            with self.subTest(mutation=mutation):
                with self.assertRaisesRegex(Exception, "malformed|changed"):
                    self.handler.prepare(
                        mutation,
                        choice_context(object_row()),
                    )

        for row in (
            object_row(zone="graveyard"),
            object_row(phased_out=True),
            object_row(logical_object_id="logical:new"),
        ):
            preparation = self.handler.prepare(valid, choice_context(row))
            self.assertEqual((), preparation.preparation_intents)


class PermanentDesignationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
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
            self.mishra,
            self.zimone,
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

    def add_permanent(self, session, *, name: str, ref: str, seat: str = "A"):
        record = self.db.lookup(name)
        card = CardInstance(
            object_id=f"fixture:{ref}",
            ref=ref,
            oracle_id=record.oracle_id,
            printed_name=record.name,
            owner=seat,
            controller=seat,
            zone="battlefield",
            zone_timestamp=session.state.event_sequence + 1,
            acquired_control_turn_count=-1,
            known_to=list(session.engine.seats),
            revealed_to=list(session.engine.seats),
        )
        session.state.cards[card.object_id] = card
        session.state.players[seat].zones["battlefield"].append(card.object_id)
        register_generated_programs(
            self.db,
            session.engine.semantics,
            (record,),
            trust_level="provisional",
            capability_registry=load_default_capability_registry(),
            capability_profile=session.state.config.review_profile,
            promote_exact_runtime_handlers=True,
            promote_exact_effect_programs=True,
        )
        return card

    @staticmethod
    def prepare_priority(session, *, seat: str = "A") -> None:
        engine = session.engine
        engine.state.active_player = seat
        engine.state.started = True
        engine.state.phase = "precombat_main"
        engine.state.step = "main"
        engine.state.stack.clear()
        engine.state.priority_passes = []
        engine.state.pending_decision = None
        engine.state.priority_player = None
        engine.permissions.invalidate_current()
        engine._grant_priority(seat)
        engine.pump()

    @staticmethod
    def pass_until(session, predicate, *, limit: int = 32):
        for _ in range(limit):
            if predicate():
                return
            principals = session.pending_principals()
            if not principals:
                raise AssertionError("Resolution stopped without a decision")
            result = session.act(principals[0], {"action_id": "pass"})
            if not result.ok:
                raise AssertionError(result.summary)
        raise AssertionError("Resolution did not reach the expected state")

    def activate(
        self,
        session,
        source,
        *,
        mana: dict[str, int],
        pin_replay: bool = False,
    ):
        session.state.players["A"].mana_pool.update(mana)
        self.prepare_priority(session)
        if pin_replay:
            session.initial_checkpoint = checkpoint_envelope(session.state)
            session.commands.clear()
            session.decisions.clear()
        ability = next(
            value
            for value in session.engine._activated_abilities(source)
            if "adapt " in value.effect_text.casefold()
            or "monstrosity " in value.effect_text.casefold()
        )
        action_id = f"activate:{source.ref}:{ability.ability_id}"
        packet = session.packet("pilot:A", full=True)
        self.assertIn(
            action_id,
            {
                action["id"]
                for action in packet["decision"]["ctx"]["legal"]["actions"]
            },
        )
        result = session.act("pilot:A", {"action_id": action_id})
        self.assertTrue(result.ok, result.summary)

    def add_competing_counter_replacements(self, session):
        self.add_permanent(
            session,
            name="Doubling Season",
            ref=f"A-doubling-{session.state.config.seed}",
        )
        self.add_permanent(
            session,
            name="Doc Samson, Super Psychiatrist",
            ref=f"A-doc-{session.state.config.seed}",
        )

    def choose_all_replacements(self, session, *, seat: str = "A"):
        for _ in range(12):
            decision = session.state.pending_decision
            if decision is None or decision.kind != "replacement.order":
                return
            projected = StateProjector(self.db, session.state)._decision(
                f"pilot:{seat}"
            )
            self.assertIsNotNone(projected)
            selected = projected["ctx"]["options"][0]["id"]
            result = session.act(
                f"pilot:{seat}",
                {
                    "action_id": "choose",
                    "choices": {"replacement": selected},
                },
            )
            self.assertTrue(result.ok, result.summary)
        self.fail("Replacement sequence did not converge")

    @staticmethod
    def designation_request(card, *, value: int = 3):
        return BecomeMonstrousRequest(
            object_id=card.object_id,
            object_ref=card.ref,
            logical_object_id=card.logical_object_id,
            value=value,
            actor="A",
            reason="Monstrosity fixture",
        )

    def test_monstrous_designation_preserves_value_control_change_and_phasing(self):
        session = self.session(7013701)
        card = self.add_permanent(
            session, name="Gluttonous Cyclops", ref="A-cyclops-designation"
        )
        result = become_monstrous(
            session.engine,
            self.designation_request(card),
        )
        self.assertTrue(result.changed)
        self.assertEqual(3, card.monstrous_value)
        session.engine.change_control(
            card.object_id, "B", reason="designation control"
        )
        card.phased_out = True
        card.phased_out = False
        self.assertEqual(3, card.monstrous_value)
        projected = StateProjector(self.db, session.state)._obj(card, "pilot:B")
        self.assertEqual(3, projected["monstrous"])
        self.assertTrue(any(
            event.code == "permanent.monstrous"
            for event in session.state.events
        ))

    def test_monstrous_designation_is_strict_and_old_incarnation_is_ignored(self):
        session = self.session(7013702)
        card = self.add_permanent(
            session, name="Gluttonous Cyclops", ref="A-cyclops-stale"
        )
        request = self.designation_request(card)
        with self.assertRaises(PermanentDesignationError):
            replace(request, value=True)
        with self.assertRaises(PermanentDesignationError):
            become_monstrous(session.engine, object())

        session.engine.move_card(card.object_id, "graveyard")
        session.engine.move_card(card.object_id, "battlefield", controller="A")
        result = become_monstrous(session.engine, request)
        self.assertFalse(result.changed)
        self.assertIsNone(card.monstrous_value)

    def test_zone_change_clears_and_copy_does_not_inherit_monstrous(self):
        session = self.session(7013703)
        card = self.add_permanent(
            session, name="Gluttonous Cyclops", ref="A-cyclops-zone"
        )
        become_monstrous(session.engine, self.designation_request(card))
        copied_ref = session.engine.create_token(
            "A",
            name=card.printed_name,
            copy_of=card.ref,
            reason="monstrous copy fixture",
        )[0]
        copied = session.engine._resolve_object(
            "A", copied_ref, zones={"battlefield"}
        )
        self.assertIsNone(copied.monstrous_value)

        session.engine.move_card(card.object_id, "graveyard")
        self.assertIsNone(card.monstrous_value)
        historical = card.to_dict()
        self.assertNotIn("monstrous_value", historical)
        self.assertEqual(historical, CardInstance.from_dict(historical).to_dict())

    def test_zero_counter_commit_result_still_creates_monstrous_designation(self):
        session = self.session(7013704)
        source = self.add_permanent(
            session, name="Gluttonous Cyclops", ref="A-cyclops-zero"
        )
        self.activate(session, source, mana={"C": 5, "R": 2})
        with patch.object(
            session.engine,
            "place_counters_intent",
            return_value=[],
        ):
            self.pass_until(
                session,
                lambda: not session.state.stack,
            )
        self.assertEqual({}, source.counters)
        self.assertEqual(3, source.monstrous_value)

    def test_adapt_uses_canonical_counter_replacement_and_replays(self):
        session = self.session(7014601)
        source = self.add_permanent(
            session, name="Aeromunculus", ref="A-aeromunculus-replay"
        )
        self.add_competing_counter_replacements(session)
        self.activate(
            session,
            source,
            mana={"C": 2, "G": 1, "U": 1},
            pin_replay=True,
        )
        self.pass_until(
            session,
            lambda: session.state.pending_decision is not None
            and session.state.pending_decision.kind == "replacement.order",
        )
        self.choose_all_replacements(session)
        self.assertIn(source.counters["+1/+1"], {3, 4})
        expected_hash = authoritative_state_hash(session.state)
        with tempfile.TemporaryDirectory() as temporary:
            record_dir = Path(temporary) / "adapt-replay"
            session.save(record_dir)
            replay = replay_record(record_dir, self.db, verify=True)
        self.assertTrue(replay["ok"], replay)
        self.assertEqual(expected_hash, replay["final_state_hash"])

    def test_four_player_adapt_replacement_choice_is_seat_scoped(self):
        session = self.session(7014602, players=4)
        source = self.add_permanent(
            session, name="Aeromunculus", ref="A-aeromunculus-four"
        )
        self.add_competing_counter_replacements(session)
        self.activate(session, source, mana={"C": 2, "G": 1, "U": 1})
        self.pass_until(
            session,
            lambda: session.state.pending_decision is not None
            and session.state.pending_decision.kind == "replacement.order",
        )
        self.assertIsNotNone(
            StateProjector(self.db, session.state)._decision("pilot:A")
        )
        for seat in ("B", "C", "D"):
            self.assertIsNone(
                StateProjector(self.db, session.state)._decision(
                    f"pilot:{seat}"
                )
            )

    def test_monstrous_replacement_resume_replays_exactly(self):
        session = self.session(7013705, players=4)
        source = self.add_permanent(
            session, name="Gluttonous Cyclops", ref="A-cyclops-replay"
        )
        self.add_competing_counter_replacements(session)
        self.activate(
            session,
            source,
            mana={"C": 5, "R": 2},
            pin_replay=True,
        )
        self.pass_until(
            session,
            lambda: session.state.pending_decision is not None
            and session.state.pending_decision.kind == "replacement.order",
        )
        self.assertIsNotNone(
            StateProjector(self.db, session.state)._decision("pilot:A")
        )
        for seat in ("B", "C", "D"):
            self.assertIsNone(
                StateProjector(self.db, session.state)._decision(
                    f"pilot:{seat}"
                )
            )
        with tempfile.TemporaryDirectory() as temporary:
            record_dir = Path(temporary) / "monstrous-restart"
            session.save(record_dir)
            restarted = CommanderSession.load(self.db, record_dir)
            self.choose_all_replacements(restarted)
            restarted_source = restarted.state.cards[source.object_id]
            self.assertIn(restarted_source.counters["+1/+1"], {7, 8})
            self.assertEqual(3, restarted_source.monstrous_value)
            restarted.save(record_dir)
            replay = replay_record(record_dir, self.db, verify=True)
        self.assertTrue(replay["ok"], replay)
        self.assertEqual(
            authoritative_state_hash(restarted.state),
            replay["final_state_hash"],
        )

    def test_monstrous_replacement_resume_pins_source_identity(self):
        session = self.session(7013706)
        source = self.add_permanent(
            session, name="Gluttonous Cyclops", ref="A-cyclops-stale-resume"
        )
        self.add_competing_counter_replacements(session)
        self.activate(session, source, mana={"C": 5, "R": 2})
        self.pass_until(
            session,
            lambda: session.state.pending_decision is not None
            and session.state.pending_decision.kind == "replacement.order",
        )
        old_logical = source.logical_object_id
        session.engine.move_card(source.object_id, "graveyard")
        session.engine.move_card(source.object_id, "battlefield", controller="A")
        self.assertNotEqual(old_logical, source.logical_object_id)
        projected = StateProjector(self.db, session.state)._decision("pilot:A")
        selected = projected["ctx"]["options"][0]["id"]
        result = session.act(
            "pilot:A",
            {
                "action_id": "choose",
                "choices": {"replacement": selected},
            },
        )
        self.assertFalse(result.ok)
        current = session.state.cards[source.object_id]
        self.assertEqual({}, current.counters)
        self.assertIsNone(current.monstrous_value)

    def test_designation_failure_rolls_back_counter_placement(self):
        session = self.session(7013707)
        source = self.add_permanent(
            session, name="Gluttonous Cyclops", ref="A-cyclops-rollback"
        )
        self.activate(session, source, mana={"C": 5, "R": 2})
        result = None
        with patch(
            "quorune.semantic_choices.intent_host.become_monstrous",
            side_effect=PermanentDesignationError("designation mutation"),
        ):
            for _ in range(12):
                principals = session.pending_principals()
                self.assertTrue(principals)
                result = session.act(principals[0], {"action_id": "pass"})
                if not result.ok:
                    break
        self.assertIsNotNone(result)
        self.assertFalse(result.ok)
        current = session.state.cards[source.object_id]
        self.assertEqual({}, current.counters)
        self.assertIsNone(current.monstrous_value)

    def test_monstrous_designation_runtime_mutant_is_killed(self):
        session = self.session(7013708)
        card = self.add_permanent(
            session, name="Gluttonous Cyclops", ref="A-cyclops-mutant"
        )

        def assert_designated() -> None:
            card.monstrous_value = None
            become_monstrous(session.engine, self.designation_request(card))
            self.assertEqual(3, card.monstrous_value)

        assert_designated()
        with patch(
            "quorune.permanent_designations.become_monstrous",
            return_value=None,
        ):
            with self.assertRaises(AssertionError):
                card.monstrous_value = None
                # Call through the patched public owner to model removal.
                from quorune import permanent_designations

                permanent_designations.become_monstrous(
                    session.engine,
                    self.designation_request(card),
                )
                self.assertEqual(3, card.monstrous_value)


if __name__ == "__main__":
    unittest.main()
