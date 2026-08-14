from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from common import ROOT, keep_all, make_session
from quorune.carddb import CardDatabase, CardRecord
from quorune.compiler import (
    counter_keyword_activation_nodes as activation_nodes,
)
from quorune.counter_keyword_abilities import (
    CounterKeywordAbilityError,
    FixedCounterKeywordAbilitySpec,
    compile_fixed_counter_keyword_ability,
    fixed_counter_keyword_handler_descriptor,
)
from quorune.deck import DeckLoader
from quorune.errors import GameRuleError
from quorune.model import CardInstance
from quorune.mana_payment_continuations import (
    issue_mana_payment_replacement_choice,
)
from quorune.oracle_ir import compile_oracle_card, register_generated_programs
from quorune.projection import StateProjector
from quorune.record import (
    authoritative_state_hash,
    checkpoint_envelope,
    replay_record,
)
from quorune.replacement_effects import ReplacementEffectError
from quorune.rules.activation.commit import (
    _commit_source_cost,
    ActivationProposalError,
)
from quorune.rules.capabilities import (
    CapabilityRegistry,
    load_default_capability_registry,
)
from quorune.semantic_runtime.counter_keyword_abilities import (
    fixed_counter_keyword_specs_from_descriptors,
)
from quorune.session import CommanderSession
from scripts.build_test_database import build_fixture_database


REGISTRY_PATH = ROOT / "quorune" / "rules" / "capability-registry.json"
FIXTURE_PATH = (
    ROOT / "tests" / "fixtures" / "fixed-counter-keyword-activations.json"
)
KEYWORD_CAPABILITY = "activation.counter_keyword.fixed"
SOURCE_COST_CAPABILITY = "activation.source_zone_change.fixed"


def focused_card_database(directory: str) -> CardDatabase:
    database = Path(directory) / "fixed-counter-keyword-activations.sqlite3"
    build_fixture_database(
        [
            ROOT / "tests" / "fixtures" / "scryfall-exact-lists.json",
            ROOT / "tests" / "fixtures" / "counter-replacement-cards.json",
            FIXTURE_PATH,
        ],
        database,
    )
    return CardDatabase(database)


class FixedCounterKeywordModelTests(unittest.TestCase):
    def test_fixed_counter_keyword_descriptor_is_strict_and_round_trips(self):
        spec = compile_fixed_counter_keyword_ability(
            material_line="Reinforce 2—{1}{G}",
            oracle_line=(
                "Reinforce 2—{1}{G} ({1}{G}, Discard this card: Put two "
                "+1/+1 counters on target creature.)"
            ),
            line_index=1,
            mechanic="reinforce",
            printed_power=None,
        )
        self.assertIsNotNone(spec)
        assert spec is not None
        self.assertEqual(
            spec,
            FixedCounterKeywordAbilitySpec.from_dict(spec.to_dict()),
        )
        ability = spec.to_activated_ability()
        self.assertEqual(("hand",), ability.zones)
        self.assertTrue(ability.discard_source)
        self.assertTrue(ability.sorcery_speed)
        self.assertEqual(2, spec.amount)
        self.assertEqual("+1/+1", spec.counter_name)
        self.assertEqual(
            (spec,),
            fixed_counter_keyword_specs_from_descriptors(
                [fixed_counter_keyword_handler_descriptor(spec)]
            ),
        )

        payload = spec.to_dict()
        payload["mana_cost"]["GENERIC"] = 99
        self.assertEqual(1, spec.mana_cost["GENERIC"])
        malformed = spec.to_dict()
        malformed["unknown"] = True
        with self.assertRaisesRegex(CounterKeywordAbilityError, "unknown"):
            FixedCounterKeywordAbilitySpec.from_dict(malformed)

    def test_activation_source_zone_continuation_gate_is_exact(self):
        event = SimpleNamespace(
            kind="zone.change",
            payload={"origin": "hand", "destination": "graveyard"},
        )
        required = SimpleNamespace(
            pending=SimpleNamespace(choice=SimpleNamespace(chooser="A")),
            batch=SimpleNamespace(events=(event,)),
            effects=(),
        )
        host = SimpleNamespace()
        unsupported = (
            {"sac_self": 1},
            {"discard_self": True},
            {"discard_self": 1, "exile_self": 1},
        )
        for cost_summary in unsupported:
            with self.subTest(cost_summary=cost_summary):
                with self.assertRaisesRegex(
                    ReplacementEffectError,
                    "unsupported",
                ):
                    issue_mana_payment_replacement_choice(
                        host,
                        seat="A",
                        action="activate",
                        response={"cost_summary": cost_summary},
                        required=required,
                    )


class FixedCounterKeywordCompilerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.db = focused_card_database(cls.temporary.name)
        cls.registry_value = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.capabilities = load_default_capability_registry()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        cls.temporary.cleanup()

    def compile(self, record: CardRecord):
        return compile_oracle_card(
            record,
            capability_registry=self.capabilities,
            capability_profile="commander_review",
        )

    def keyword_node(self, record: CardRecord):
        mechanic = {
            "Beastbreaker of Bala Ged": "level up",
            "Abzan Battle Priest": "outlast",
            "Earthbrawn": "reinforce",
            "Deadbridge Goliath": "scavenge",
        }[record.name]
        ir = self.compile(record)
        return ir, next(
            node for node in ir.faces[0].nodes if mechanic in node.mechanics
        )

    def test_four_fixed_counter_keywords_compile_source_spanned_activations(self):
        expected = {
            "Beastbreaker of Bala Ged": (
                "level up",
                "battlefield",
                "level",
                1,
                "$source.zone_object",
                False,
                False,
            ),
            "Abzan Battle Priest": (
                "outlast",
                "battlefield",
                "+1/+1",
                1,
                "$source.zone_object",
                False,
                False,
            ),
            "Earthbrawn": (
                "reinforce",
                "hand",
                "+1/+1",
                1,
                "$target.0",
                True,
                False,
            ),
            "Deadbridge Goliath": (
                "scavenge",
                "graveyard",
                "+1/+1",
                5,
                "$target.0",
                False,
                True,
            ),
        }
        for name, facts in expected.items():
            with self.subTest(name=name):
                record = self.db.lookup(name)
                ir, node = self.keyword_node(record)
                (
                    mechanic,
                    active_zone,
                    counter,
                    amount,
                    card,
                    discard_source,
                    exile_source,
                ) = facts
                self.assertTrue(node.exact, ir.material_residuals)
                self.assertEqual("activated_ability", node.kind)
                self.assertEqual("activate", node.event)
                self.assertEqual(active_zone, node.active_zone)
                self.assertEqual(
                    f"fixed-{mechanic.replace(' ', '-')}-activation-v1",
                    node.template_id,
                )
                self.assertEqual(counter, node.effects[0]["counter"])
                self.assertEqual(amount, node.effects[0]["amount"])
                self.assertEqual(card, node.effects[0]["card"])
                self.assertEqual(discard_source, node.cost["discard_source"])
                self.assertEqual(exile_source, node.cost["exile_source"])
                self.assertEqual(
                    record.oracle_text[
                        node.span.start : node.span.end
                    ],
                    node.text,
                )
                self.assertEqual(
                    "ability.activated.fixed-counter-keyword.v1",
                    node.handlers[0]["handler_id"],
                )
                self.assertIn(KEYWORD_CAPABILITY, node.capability_dependencies)
                self.assertIn(
                    "counter.producer.fixed_effect",
                    node.capability_dependencies,
                )
                self.assertEqual(
                    mechanic in {"reinforce", "scavenge"},
                    SOURCE_COST_CAPABILITY in node.capability_dependencies,
                )

    def test_unsupported_counter_keyword_variants_remain_precise_residuals(self):
        cases = (
            ("Level up {X}", ("Level Up",), "2"),
            ("Outlast {W/U}", ("Outlast",), "2"),
            ("Reinforce X—{2}{G}", ("Reinforce",), None),
            ("Scavenge {2}{B}", ("Scavenge",), "*"),
        )
        base = self.db.lookup("Deadbridge Goliath")
        for text, keywords, power in cases:
            with self.subTest(text=text):
                record = replace(
                    base,
                    oracle_id=f"fixture:{text}",
                    name="Counter Keyword Residual Fixture",
                    oracle_text=text,
                    keywords=keywords,
                    power=power,
                    faces=(),
                )
                ir = self.compile(record)
                self.assertNotEqual("exact", ir.status)
                self.assertEqual(
                    "unsupported_fixed_counter_keyword_activation",
                    ir.faces[0].residuals[0].kind,
                )

    def test_scavenge_dynamic_power_and_type_changing_boundary_fail_closed(self):
        base = self.db.lookup("Deadbridge Goliath")
        face = {
            "name": "Changing Scavenge Face",
            "type_line": base.type_line,
            "oracle_text": base.oracle_text,
            "keywords": list(base.keywords),
            "power": "5",
            "toughness": base.toughness,
        }
        ir = self.compile(
            replace(
                base,
                oracle_id="fixture:face-changing-scavenge",
                name="Face-Changing Scavenge Fixture",
                faces=(face,),
            )
        )
        self.assertNotEqual("exact", ir.status)
        self.assertTrue(
            any(
                residual.kind
                == "unsupported_fixed_counter_keyword_activation"
                for residual in ir.material_residuals
            )
        )
        capability = self.capabilities.capability(KEYWORD_CAPABILITY)
        assert capability is not None
        exclusions = " ".join(capability["applicability"]["exclusions"])
        self.assertIn("type-changing", exclusions)
        self.assertIn("face", exclusions)

    def test_fixed_counter_keyword_dependencies_fail_closed(self):
        record = self.db.lookup("Earthbrawn")
        for blocked in (
            KEYWORD_CAPABILITY,
            SOURCE_COST_CAPABILITY,
            "counter.producer.fixed_effect",
            "target.revalidate_resolution",
        ):
            with self.subTest(blocked=blocked):
                value = deepcopy(self.registry_value)
                row = next(
                    item
                    for item in value["capabilities"]
                    if item["id"] == blocked
                )
                row["status"] = "blocked"
                row["blockers"] = ["focused mutation witness"]
                ir = compile_oracle_card(
                    record,
                    capability_registry=CapabilityRegistry(value),
                    capability_profile="commander_review",
                )
                node = next(
                    candidate
                    for candidate in ir.faces[0].nodes
                    if "reinforce" in candidate.mechanics
                )
                self.assertFalse(node.exact)
                self.assertTrue(node.residual_ids)

    def test_fixed_counter_keyword_compiler_mutant_is_killed(self):
        def assert_exact() -> None:
            _ir, node = self.keyword_node(self.db.lookup("Deadbridge Goliath"))
            self.assertTrue(node.exact)
            self.assertEqual(5, node.effects[0]["amount"])

        assert_exact()
        with mock.patch.object(
            activation_nodes,
            "compile_fixed_counter_keyword_ability",
            return_value=None,
        ):
            with self.assertRaises(AssertionError):
                assert_exact()


class FixedCounterKeywordRuntimeTests(unittest.TestCase):
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
        cls.capabilities = load_default_capability_registry()

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
        session.engine.permissions.invalidate_current()
        session.engine.state.pending_decision = None
        session.engine.state.priority_player = None
        session.engine.state.priority_passes = []
        session.commands.clear()
        session.decisions.clear()
        return session

    def add_card(
        self,
        session,
        *,
        seat: str,
        name: str,
        ref: str,
        zone: str,
        register: bool = True,
        controller: str | None = None,
    ):
        engine = session.engine
        record = self.db.lookup(name)
        public = zone not in {"hand", "library"}
        card = CardInstance(
            object_id=f"fixture:{ref}",
            ref=ref,
            oracle_id=record.oracle_id,
            printed_name=record.name,
            owner=seat,
            controller=controller or seat,
            zone=zone,
            zone_timestamp=engine.state.event_sequence + 1,
            acquired_control_turn_count=-1,
            known_to=list(engine.seats) if public else [seat],
            revealed_to=list(engine.seats) if public else [],
        )
        engine.state.cards[card.object_id] = card
        engine.state.players[seat].zones[zone].append(card.object_id)
        if register:
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
    def prepare_priority(session, *, seat: str = "A", mana: int = 8):
        engine = session.engine
        for symbol in ("B", "C", "G", "R", "U", "W"):
            engine.state.players[seat].mana_pool[symbol] = mana
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
    def pass_until(session, predicate, *, limit: int = 48):
        for _ in range(limit):
            if predicate():
                return
            principals = session.pending_principals()
            if not principals:
                raise AssertionError("Resolution stopped without a decision")
            result = session.act(principals[0], {"action_id": "pass"})
            if not result.ok:
                raise AssertionError(result.summary)
        raise AssertionError("Resolution did not converge")

    @staticmethod
    def choose_replacements(session, *, limit: int = 8):
        for _ in range(limit):
            decision = session.state.pending_decision
            if decision is None or decision.kind != "replacement.order":
                return
            seat = decision.actors[0]
            packet = StateProjector(
                session.engine.card_db, session.state
            )._decision(f"pilot:{seat}")
            assert packet is not None
            selected = packet["ctx"]["options"][0]["id"]
            result = session.act(
                f"pilot:{seat}",
                {"a": "choose", "replacement": selected},
            )
            if not result.ok:
                raise AssertionError(result.summary)
        raise AssertionError("Replacement sequence did not converge")

    def stage_keyword(
        self,
        session,
        *,
        name: str,
        source_zone: str,
        ref: str,
    ):
        source = self.add_card(
            session,
            seat="A",
            name=name,
            ref=ref,
            zone=source_zone,
        )
        target = (
            source
            if source_zone == "battlefield"
            else self.add_card(
                session,
                seat="A",
                name="Beastbreaker of Bala Ged",
                ref=f"{ref}-target",
                zone="battlefield",
                register=False,
            )
        )
        self.prepare_priority(session)
        ability = next(
            ability
            for ability in session.engine._activated_abilities(source)
            if ability.zones == (source_zone,)
            and (
                ability.discard_source
                or ability.exile_source
                or ability.tap_source
                or "level counter" in ability.effect_text
            )
        )
        return source, target, ability

    def test_each_fixed_counter_keyword_pays_cost_and_places_counters(self):
        cases = (
            ("Beastbreaker of Bala Ged", "battlefield", "level", 1),
            ("Abzan Battle Priest", "battlefield", "+1/+1", 1),
            ("Earthbrawn", "hand", "+1/+1", 1),
            ("Deadbridge Goliath", "graveyard", "+1/+1", 5),
        )
        for index, (name, zone, counter, amount) in enumerate(cases):
            with self.subTest(name=name):
                session = self.session(7027700 + index)
                engine = session.engine
                source, target, ability = self.stage_keyword(
                    session,
                    name=name,
                    source_zone=zone,
                    ref=f"A-counter-keyword-{index}",
                )
                session.initial_checkpoint = checkpoint_envelope(engine.state)
                session.commands.clear()
                session.decisions.clear()
                response = {
                    "action_id": (
                        f"activate:{source.ref}:{ability.ability_id}"
                    )
                }
                if ability.target_schema is not None:
                    response["targets"] = [target.ref]
                result = session.act("pilot:A", response)
                self.assertTrue(result.ok, result.summary)
                if ability.tap_source:
                    self.assertTrue(source.tapped)
                if ability.discard_source:
                    self.assertEqual("graveyard", source.zone)
                if ability.exile_source:
                    self.assertEqual("exile", source.zone)
                self.pass_until(session, lambda: not engine.state.stack)
                self.assertEqual(amount, target.counters.get(counter, 0))

    def test_scavenge_fixed_power_activation_replays_exactly(self):
        session = self.session(7027707)
        engine = session.engine
        source, target, ability = self.stage_keyword(
            session,
            name="Deadbridge Goliath",
            source_zone="graveyard",
            ref="A-scavenge-replay",
        )
        session.initial_checkpoint = checkpoint_envelope(engine.state)
        session.commands.clear()
        session.decisions.clear()
        result = session.act(
            "pilot:A",
            {
                "action_id": f"activate:{source.ref}:{ability.ability_id}",
                "targets": [target.ref],
            },
        )
        self.assertTrue(result.ok, result.summary)
        self.pass_until(session, lambda: not engine.state.stack)
        self.assertEqual("exile", source.zone)
        self.assertEqual(5, target.counters.get("+1/+1", 0))
        expected_hash = authoritative_state_hash(engine.state)
        with tempfile.TemporaryDirectory() as temporary:
            game_dir = Path(temporary) / "scavenge-replay"
            session.save(game_dir)
            replay = replay_record(game_dir, self.db, verify=True)
        self.assertTrue(replay["ok"], replay)
        self.assertEqual(expected_hash, replay["final_state_hash"])

    def test_counter_keyword_source_departure_does_not_counter_returned_object(self):
        session = self.session(7028701)
        engine = session.engine
        source, _target, ability = self.stage_keyword(
            session,
            name="Beastbreaker of Bala Ged",
            source_zone="battlefield",
            ref="A-level-departure",
        )
        result = session.act(
            "pilot:A",
            {"action_id": f"activate:{source.ref}:{ability.ability_id}"},
        )
        self.assertTrue(result.ok, result.summary)
        engine.move_card(source.object_id, "hand", log=False)
        engine.move_card(
            source.object_id,
            "battlefield",
            controller="A",
            log=False,
        )
        self.pass_until(session, lambda: not engine.state.stack)
        self.assertEqual(0, source.counters.get("level", 0))

    def test_rejected_source_cost_activation_rolls_back_mana_and_zone(self):
        session = self.session(7027702)
        engine = session.engine
        source, _target, ability = self.stage_keyword(
            session,
            name="Earthbrawn",
            source_zone="hand",
            ref="A-reinforce-rejected",
        )
        before = authoritative_state_hash(engine.state)
        result = session.act(
            "pilot:A",
            {
                "action_id": f"activate:{source.ref}:{ability.ability_id}",
                "targets": ["B"],
            },
        )
        self.assertFalse(result.ok)
        self.assertEqual(before, authoritative_state_hash(engine.state))
        self.assertEqual("hand", source.zone)

    def test_activation_source_cost_replacement_journal_fails_closed(self):
        session = self.session(7027703)
        source, _target, ability = self.stage_keyword(
            session,
            name="Earthbrawn",
            source_zone="hand",
            ref="A-reinforce-journal",
        )
        with self.assertRaisesRegex(
            ActivationProposalError,
            "ambiguous",
        ):
            _commit_source_cost(
                session.engine,
                source,
                ability,
                {
                    "_mana_replacement_selections": {
                        "zone.change:1:2:wrong-ref": []
                    }
                },
            )
        self.assertEqual("hand", source.zone)

    def test_reinforce_source_cost_replacement_suspends_before_mutation(self):
        session = self.session(7027704, players=4)
        engine = session.engine
        source, target, ability = self.stage_keyword(
            session,
            name="Earthbrawn",
            source_zone="hand",
            ref="A-reinforce-replacement",
        )
        voidwalker = self.add_card(
            session,
            seat="B",
            name="Dauthi Voidwalker",
            ref="B-voidwalker",
            zone="battlefield",
            controller="B",
        )
        engine.create_token(
            "B",
            name="",
            copy_of=voidwalker.ref,
            reason="reinforce source-cost ordering witness",
        )
        self.prepare_priority(session)
        session.initial_checkpoint = checkpoint_envelope(engine.state)
        session.commands.clear()
        session.decisions.clear()
        before_mana = sum(engine.state.players["A"].mana_pool.values())
        result = session.act(
            "pilot:A",
            {
                "action_id": f"activate:{source.ref}:{ability.ability_id}",
                "targets": [target.ref],
            },
        )
        self.assertTrue(result.ok, result.summary)
        self.assertEqual("replacement.order", session.state.pending_decision.kind)
        self.assertEqual("hand", source.zone)
        self.assertFalse(engine.state.stack)
        self.assertEqual(
            before_mana,
            sum(engine.state.players["A"].mana_pool.values()),
        )
        projector = StateProjector(self.db, engine.state)
        self.assertIsNotNone(projector._decision("pilot:A"))
        for seat in ("B", "C", "D"):
            self.assertIsNone(projector._decision(f"pilot:{seat}"))

        with tempfile.TemporaryDirectory() as temporary:
            game_dir = Path(temporary) / "reinforce-source-replacement"
            session.save(game_dir)
            restarted = CommanderSession.load(self.db, game_dir)
            self.choose_replacements(restarted)
            restarted_source = restarted.engine.state.cards[source.object_id]
            self.assertEqual("exile", restarted_source.zone)
            self.assertTrue(restarted.engine.state.stack)
            expected_hash = authoritative_state_hash(restarted.engine.state)
            restarted.save(game_dir)
            replay = replay_record(game_dir, self.db, verify=True)
        self.assertTrue(replay["ok"], replay)
        self.assertEqual(expected_hash, replay["final_state_hash"])

    def test_counter_keyword_quantity_replacement_suspends_and_replays(self):
        session = self.session(7027705, players=4)
        engine = session.engine
        source, _target, ability = self.stage_keyword(
            session,
            name="Beastbreaker of Bala Ged",
            source_zone="battlefield",
            ref="A-level-replacement",
        )
        self.add_card(
            session,
            seat="A",
            name="Doubling Season",
            ref="A-doubling",
            zone="battlefield",
        )
        self.add_card(
            session,
            seat="A",
            name="Doc Samson, Super Psychiatrist",
            ref="A-doc",
            zone="battlefield",
        )
        self.prepare_priority(session)
        session.initial_checkpoint = checkpoint_envelope(engine.state)
        session.commands.clear()
        session.decisions.clear()
        result = session.act(
            "pilot:A",
            {"action_id": f"activate:{source.ref}:{ability.ability_id}"},
        )
        self.assertTrue(result.ok, result.summary)
        self.pass_until(
            session,
            lambda: session.state.pending_decision is not None
            and session.state.pending_decision.kind == "replacement.order",
        )
        projector = StateProjector(self.db, engine.state)
        self.assertIsNotNone(projector._decision("pilot:A"))
        for seat in ("B", "C", "D"):
            self.assertIsNone(projector._decision(f"pilot:{seat}"))
        self.choose_replacements(session)
        self.pass_until(session, lambda: not engine.state.stack)
        self.assertGreater(source.counters.get("level", 0), 1)
        expected_hash = authoritative_state_hash(engine.state)
        with tempfile.TemporaryDirectory() as temporary:
            game_dir = Path(temporary) / "counter-keyword-quantity"
            session.save(game_dir)
            replay = replay_record(game_dir, self.db, verify=True)
        self.assertTrue(replay["ok"], replay)
        self.assertEqual(expected_hash, replay["final_state_hash"])

    def test_activation_zone_cost_resume_mutant_is_killed(self):
        def assert_suspends() -> None:
            session = self.session(7027706, players=4)
            engine = session.engine
            source, target, ability = self.stage_keyword(
                session,
                name="Earthbrawn",
                source_zone="hand",
                ref="A-reinforce-mutant",
            )
            voidwalker = self.add_card(
                session,
                seat="B",
                name="Dauthi Voidwalker",
                ref="B-voidwalker-mutant",
                zone="battlefield",
                controller="B",
            )
            engine.create_token(
                "B",
                name="",
                copy_of=voidwalker.ref,
                reason="activation zone-cost mutation witness",
            )
            self.prepare_priority(session)
            result = session.act(
                "pilot:A",
                {
                    "action_id": f"activate:{source.ref}:{ability.ability_id}",
                    "targets": [target.ref],
                },
            )
            self.assertTrue(result.ok, result.summary)
            self.assertEqual(
                "replacement.order",
                session.state.pending_decision.kind,
            )

        assert_suspends()
        with mock.patch(
            "quorune.mana_payment_continuations.issue_mana_payment_replacement_choice",
            side_effect=ReplacementEffectError(
                "mutant rejects activation zone-change continuation"
            ),
        ):
            with self.assertRaises(AssertionError):
                assert_suspends()


if __name__ == "__main__":
    unittest.main()
