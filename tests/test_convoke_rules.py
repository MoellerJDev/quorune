from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from common import keep_all, load_assets, make_session
from quorune.card_programs import compile_card_program
from quorune.compiler import keyword_nodes as keyword_nodes_module
from quorune.convoke import (
    ConvokeCandidate,
    ConvokeError,
    ConvokePaymentPlan,
    canonical_mana_requirements,
    find_convoke_plan,
    select_convoke_plan,
)
from quorune.oracle_ir import compile_oracle_card, generated_programs
from quorune.record import (
    authoritative_state_hash,
    checkpoint_envelope,
    replay_record,
)
from quorune.rules.capabilities import load_default_capability_registry
from quorune.rules.casting.commit import commit_cast
from quorune.rules.casting.model import CastProposalError, CastProposalRequest
from quorune.rules.casting.proposal import build_cast_offer, build_cast_proposal
from quorune.semantic_runtime import SemanticNodeError
from quorune.semantic_runtime.cast_costs import (
    default_cast_cost_component_registry,
)


class _NoRulingsDatabase:
    @staticmethod
    def rulings(record):
        del record
        return ()


class ConvokeModelTests(unittest.TestCase):
    def test_convoke_descriptor_and_plan_reject_malformed_values(self):
        registry = default_cast_cost_component_registry()
        valid = {
            "handler_id": "casting.payment.convoke.v1",
            "schema_version": 1,
            "event": "cast.cost",
            "payment": {"schema_version": 1, "kind": "convoke"},
        }
        for malformed in (
            {**valid, "unknown": True},
            {**valid, "schema_version": True},
            {**valid, "schema_version": 2},
            {**valid, "event": "continuous"},
            {**valid, "payment": []},
            {**valid, "payment": {"schema_version": 1, "kind": "improvise"}},
        ):
            with self.subTest(malformed=malformed):
                with self.assertRaises(SemanticNodeError):
                    registry.validate(malformed)

        with self.assertRaises(ConvokeError):
            ConvokeCandidate(True, "object:a1", "object:a1@0", ("G",))
        with self.assertRaises(ConvokeError):
            ConvokeCandidate("A1", "object:a1", "object:a1@0", ["G"])

        candidate = ConvokeCandidate("A1", "object:a1", "object:a1@0", ("G",))
        plan = select_convoke_plan(
            {"G": 1},
            (candidate,),
            affordable=lambda value: not any(value.remaining),
        )
        self.assertIsNotNone(plan)
        assert plan is not None
        self.assertEqual(plan, ConvokePaymentPlan.from_dict(plan.to_dict()))
        malformed_plan = plan.to_dict()
        malformed_plan["remaining"]["G"] = True
        with self.assertRaises(ConvokeError):
            ConvokePaymentPlan.from_dict(malformed_plan)
        malformed_plan = plan.to_dict()
        malformed_plan["requirements"].pop("C")
        with self.assertRaises(ConvokeError):
            ConvokePaymentPlan.from_dict(malformed_plan)
        with self.assertRaises(ConvokeError):
            ConvokePaymentPlan(
                requirements=list(plan.requirements),
                remaining=plan.remaining,
                contributions=plan.contributions,
            )
        with self.assertRaises(ConvokeError):
            select_convoke_plan(
                {"GENERIC": 2},
                (
                    ConvokeCandidate("A1", "object:a1", "logical:shared"),
                    ConvokeCandidate("A2", "object:a2", "logical:shared"),
                ),
                affordable=lambda value: not any(value.remaining),
            )

    def test_multicolor_creature_uses_the_payable_colored_assignment(self):
        creature = ConvokeCandidate(
            "A1",
            "object:a1",
            "object:a1@0",
            ("W", "U"),
        )
        plan = select_convoke_plan(
            {"W": 1, "U": 1},
            (creature,),
            affordable=lambda value: value.remaining_dict["W"] == 1
            and value.remaining_dict["U"] == 0,
        )

        self.assertIsNotNone(plan)
        assert plan is not None
        self.assertEqual("U", plan.contributions[0].symbol)
        self.assertEqual(1, plan.remaining_dict["W"])
        self.assertEqual(0, plan.remaining_dict["U"])

    def test_convoke_never_pays_colorless_and_canonicalizes_selection_order(self):
        first = ConvokeCandidate("A2", "object:a2", "object:a2@0", ("G",))
        second = ConvokeCandidate("A1", "object:a1", "object:a1@0", ())
        requirements = canonical_mana_requirements({"GENERIC": 1, "G": 1, "C": 1})
        forward = select_convoke_plan(
            requirements,
            (first, second),
            affordable=lambda value: value.remaining_dict["C"] == 1,
        )
        reverse = select_convoke_plan(
            requirements,
            (second, first),
            affordable=lambda value: value.remaining_dict["C"] == 1,
        )

        self.assertEqual(forward, reverse)
        assert forward is not None
        self.assertEqual(1, forward.remaining_dict["C"])
        self.assertEqual(0, forward.remaining_dict["GENERIC"])
        self.assertEqual(0, forward.remaining_dict["G"])
        self.assertEqual(forward.fingerprint, reverse.fingerprint)

    def test_convoke_planner_mutant_is_killed(self):
        creature = ConvokeCandidate("A1", "object:a1", "object:a1@0", ("G",))

        def assert_planner() -> None:
            self.assertIsNotNone(
                find_convoke_plan(
                    {"G": 1},
                    (creature,),
                    affordable=lambda value: not any(value.remaining),
                )
            )

        assert_planner()
        with mock.patch("quorune.convoke.convoke_plans_for_selected", return_value=()):
            with self.assertRaises(AssertionError):
                assert_planner()


class ConvokeCompilerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db, cls.mishra, cls.zimone = load_assets()
        cls.base = cls.db.lookup("Chord of Calling")
        cls.capabilities = load_default_capability_registry()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def record(self, text: str, *, keywords=("Convoke",)):
        return replace(
            self.base,
            oracle_id="00000000-0000-4000-8000-000000000051",
            name="Ordinary Convoke Fixture",
            oracle_text=text,
            keywords=tuple(keywords),
            faces=(),
        )

    def compile(self, text: str, *, keywords=("Convoke",)):
        return compile_oracle_card(
            self.record(text, keywords=keywords),
            capability_registry=self.capabilities,
            capability_profile="commander_review",
        )

    def test_ordinary_convoke_compiles_face_pinned_typed_program(self):
        record = self.record("Convoke")
        ir = self.compile("Convoke")

        self.assertEqual("exact", ir.status)
        node = ir.faces[0].nodes[0]
        self.assertEqual("ordinary-convoke-payment-v1", node.template_id)
        self.assertEqual("stack", node.active_zone)
        self.assertEqual("cast.cost", node.event)
        self.assertEqual(("casting.payment.convoke",), node.capability_dependencies)
        self.assertEqual(
            "casting.payment.convoke.v1",
            node.handlers[0]["handler_id"],
        )
        self.assertEqual("Convoke", record.oracle_text[node.span.start : node.span.end])

        programs = generated_programs(
            _NoRulingsDatabase(),
            record,
            trust_level="trusted",
            capability_registry=self.capabilities,
            capability_profile="commander_review",
        )
        program = next(program for program in programs if program.event == "cast.cost")
        self.assertEqual("front", program.provenance["face_id"])
        self.assertEqual("static:front:n1:convoke", program.ability_id)
        card_program = compile_card_program(
            _NoRulingsDatabase(),
            record,
            capability_registry=self.capabilities,
            capability_profile="commander_review",
            trust_level="trusted",
        )
        self.assertIn(program.ability_id, {ability.ability_id for ability in card_program.abilities})

    def test_multiple_convoke_instances_are_redundant_and_siblings_are_separate(self):
        duplicate = self.compile("Convoke, convoke")
        self.assertEqual(
            1,
            sum(node.event == "cast.cost" for node in duplicate.faces[0].nodes),
        )
        sibling = self.compile("Convoke, vigilance", keywords=("Convoke", "Vigilance"))
        convoke = next(node for node in sibling.faces[0].nodes if node.event == "cast.cost")
        self.assertEqual(
            "Convoke",
            sibling.faces[0].oracle_text[convoke.span.start : convoke.span.end],
        )
        self.assertEqual("ordinary-convoke-payment-v1", convoke.template_id)

    def test_unsupported_convoke_variants_remain_precise_residuals(self):
        for text in (
            "Convoke 2",
            "Convoke — Tap exactly two creatures to help cast this spell",
        ):
            with self.subTest(text=text):
                ir = self.compile(text)
                self.assertTrue(ir.material_residuals)
                self.assertTrue(
                    any(
                        "convoke-unsupported-wording" in blocker
                        for residual in ir.material_residuals
                        for blocker in residual.blockers
                    )
                )
                self.assertFalse(
                    any(
                        node.event == "cast.cost" and node.exact
                        for node in ir.faces[0].nodes
                    )
                )

        equivalent = self.compile(
            "You may tap two creatures rather than pay this spell's mana cost."
        )
        self.assertTrue(equivalent.material_residuals)
        self.assertFalse(
            any(node.event == "cast.cost" for node in equivalent.faces[0].nodes)
        )

    def test_convoke_compiler_mutant_is_killed(self):
        def assert_exact() -> None:
            node = next(
                node
                for node in self.compile("Convoke").faces[0].nodes
                if node.event == "cast.cost"
            )
            self.assertEqual("casting.payment.convoke.v1", node.handlers[0]["handler_id"])

        assert_exact()
        with mock.patch.object(
            keyword_nodes_module,
            "ordinary_convoke_keyword_node",
            return_value=None,
        ):
            with self.assertRaises((AssertionError, StopIteration)):
                assert_exact()


class ConvokeRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db, cls.mishra, cls.zimone = load_assets()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    @staticmethod
    def card(engine, seat: str, name: str):
        return next(
            card
            for card in engine.state.cards.values()
            if card.owner == seat and card.printed_name == name
        )

    def fixture(self, seed: int, *, players: int = 2, creature_count: int = 3):
        session = make_session(
            self.db,
            self.mishra,
            self.zimone,
            players=players,
            seed=seed,
        )
        keep_all(session)
        engine = session.engine
        chord = self.card(engine, "B", "Chord of Calling")
        engine.move_card(chord.object_id, "hand", log=False)
        creatures = tuple(
            engine.create_token(
                "B",
                name=f"Green Convoke Fixture {index}",
                characteristics={
                    "type_line": "Token Creature",
                    "colors": ["G"],
                    "power": "1",
                    "toughness": "1",
                },
                reason="Convoke rules fixture",
            )[0]
            for index in range(creature_count)
        )
        engine.state.active_player = "B"
        engine.state.started = True
        engine.state.phase = "precombat_main"
        engine.state.step = "main"
        engine.state.stack.clear()
        engine.state.priority_passes = []
        engine.state.pending_decision = None
        engine.state.priority_player = "B"
        engine.permissions.invalidate_current()
        return session, chord, creatures

    def test_convoke_offer_and_submission_share_whole_vector_payment(self):
        session, chord, creatures = self.fixture(7025101)
        engine = session.engine
        action = next(
            action
            for action in engine._priority_action_hints("B")["actions"]
            if action.get("card") == chord.ref
        )
        option = action["cost_options"][0]

        self.assertEqual(0, sum(option["requirements"].values()))
        self.assertEqual(set(creatures), set(option["choice_schema"]["convoke_cards"]["legal_refs"]))
        engine._cast(
            "B",
            {"card": chord.ref, "x": 0, "convoke_cards": list(reversed(creatures))},
        )

        self.assertEqual("stack", chord.zone)
        self.assertTrue(
            all(
                next(card for card in engine.state.cards.values() if card.ref == ref).tapped
                for ref in creatures
            )
        )

    def test_typed_convoke_pays_colored_x_cost_without_using_mana_sources(self):
        session, chord, creatures = self.fixture(7025108, creature_count=5)
        engine = session.engine

        options = engine._cast_cost_options(
            "B",
            chord,
            engine.semantics.get(f"{chord.oracle_id}:spell:front"),
            response={"x": 2, "convoke_cards": list(creatures)},
            hint=False,
        )

        self.assertEqual(1, len(options))
        self.assertEqual(0, sum(options[0]["requirements"].values()))
        engine._cast(
            "B",
            {"card": chord.ref, "x": 2, "convoke_cards": list(creatures)},
        )
        self.assertEqual("stack", chord.zone)
        self.assertTrue(
            all(
                next(
                    card
                    for card in engine.state.cards.values()
                    if card.ref == ref
                ).tapped
                for ref in creatures
            )
        )

    def test_raw_keyword_without_compiled_convoke_fails_closed(self):
        session, chord, _ = self.fixture(7025102)
        record = session.engine.card_record(chord)
        self.assertIn("Convoke", record.keywords)

        with mock.patch(
            "quorune.rules.casting.costs.compiled_convoke_specs",
            return_value=(),
        ):
            offer = build_cast_offer(session.engine, "B", chord)

        self.assertEqual("unpayable", offer.status)
        self.assertEqual("mandatory_cost_unpayable", offer.reason)

    def test_convoke_applies_after_static_cost_reduction(self):
        session, chord, creatures = self.fixture(7025103)
        engine = session.engine
        reducer = self.card(engine, "B", "Elves of Deep Shadow")
        engine.move_card(reducer.object_id, "battlefield", controller="B", log=False)
        reducer.tapped = True
        program = engine.semantics.get(f"{reducer.oracle_id}:spell:front")
        self.assertIsNotNone(program)
        program.cost_schema = {
            "static_modifiers": [
                {"spell_type": "instant", "generic_reduction": 1}
            ]
        }

        options = engine._cast_cost_options(
            "B",
            chord,
            engine.semantics.get(f"{chord.oracle_id}:spell:front"),
            response={"x": 1, "convoke_cards": list(creatures)},
            hint=False,
        )

        self.assertEqual(1, len(options))
        self.assertEqual(0, sum(options[0]["requirements"].values()))
        self.assertEqual(1, options[0]["cost_reductions"][0]["count"])

    def test_convoke_creature_cannot_also_activate_for_mana(self):
        session, chord, creatures = self.fixture(7025104, creature_count=2)
        engine = session.engine
        birds = self.card(engine, "B", "Birds of Paradise")
        engine.move_card(birds.object_id, "battlefield", controller="B", log=False)
        program = engine.semantics.get(f"{chord.oracle_id}:spell:front")

        payable = engine._cast_cost_options(
            "B",
            chord,
            program,
            response={"x": 0, "convoke_cards": list(creatures)},
            hint=False,
        )
        double_used = engine._cast_cost_options(
            "B",
            chord,
            program,
            response={"x": 0, "convoke_cards": [birds.ref, creatures[0]]},
            hint=False,
        )

        self.assertTrue(payable)
        self.assertEqual([], double_used)

    def test_stale_convoke_characteristics_roll_back_before_payment(self):
        session, chord, creatures = self.fixture(7025105)
        engine = session.engine
        response = {"card": chord.ref, "x": 0, "convoke_cards": list(creatures)}
        proposal = build_cast_proposal(
            engine,
            CastProposalRequest.from_submission("B", response),
        )
        selected = next(
            card for card in engine.state.cards.values() if card.ref == creatures[0]
        )
        selected.annotations["token_characteristics"]["type_line"] = "Token Artifact"
        before = authoritative_state_hash(engine.state)

        with self.assertRaisesRegex(CastProposalError, "changed identity or characteristics"):
            commit_cast(engine, proposal, response)

        self.assertEqual(before, authoritative_state_hash(engine.state))
        self.assertEqual("hand", chord.zone)
        self.assertFalse(any(engine.state.cards[object_id].tapped for object_id in engine.state.players["B"].zones["battlefield"] if engine.state.cards[object_id].ref in creatures))

    def test_four_player_convoke_offer_is_controller_scoped(self):
        session, chord, _ = self.fixture(7025106, players=4)
        owner = session.engine._priority_action_hints("B")["actions"]
        opponent = session.engine._priority_action_hints("A")["actions"]

        self.assertTrue(any(action.get("card") == chord.ref for action in owner))
        self.assertFalse(any(action.get("card") == chord.ref for action in opponent))
        self.assertNotIn(
            chord.printed_name,
            json.dumps(session.packet("pilot:A", full=True)["state"], sort_keys=True),
        )

    def test_convoke_payment_replays_exactly(self):
        session, chord, creatures = self.fixture(7025107)
        engine = session.engine
        engine.state.pending_decision = None
        engine.state.priority_player = None
        engine.permissions.invalidate_current()
        engine._grant_priority("B")
        engine.pump()
        session.initial_checkpoint = checkpoint_envelope(engine.state)
        session.commands.clear()
        session.decisions.clear()

        result = session.act(
            "pilot:B",
            {"a": "cast", "card": chord.ref, "x": 0, "convoke_cards": list(creatures)},
        )
        self.assertTrue(result.ok, result.summary)
        expected_hash = authoritative_state_hash(engine.state)

        with tempfile.TemporaryDirectory() as temporary:
            game_dir = Path(temporary) / "ordinary-convoke-replay"
            session.save(game_dir)
            replay = replay_record(game_dir, self.db, verify=True)
        self.assertTrue(replay["ok"], replay)
        self.assertEqual(expected_hash, replay["final_state_hash"])


if __name__ == "__main__":
    unittest.main()
