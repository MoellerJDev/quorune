from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from common import keep_all, load_assets, make_session, pass_current
from quorune.counter_placement import (
    CounterPlacementRequest,
    place_counters,
)
from quorune.counter_removal import (
    commit_counter_removals,
    CounterRemoval,
    plan_counter_removals,
)
from quorune.destruction import destroy_permanent_refs
from quorune.model import CombatState
from quorune.record import (
    authoritative_state_hash,
    checkpoint_envelope,
    replay_record,
)


class KeywordCounterCompositionTests(unittest.TestCase):
    """CR 122.1b keyword counters composed with their executable owners."""

    @classmethod
    def setUpClass(cls):
        cls.db, cls.mishra, cls.zimone = load_assets()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def session(self, seed: int, *, step: str):
        session = make_session(
            self.db,
            self.mishra,
            self.zimone,
            players=4,
            seed=seed,
            auto_pass_empty=False,
        )
        keep_all(session)
        engine = session.engine
        engine.permissions.invalidate_current()
        engine.state.pending_decision = None
        engine.state.priority_player = None
        engine.state.priority_passes = []
        engine.state.phase = "combat"
        engine.state.step = step
        engine.state.combat = CombatState()
        session.commands.clear()
        session.decisions.clear()
        return session

    @staticmethod
    def token(
        engine,
        controller: str,
        name: str,
        *,
        power: int = 2,
        toughness: int = 2,
        temporary_keywords: tuple[str, ...] = (),
    ):
        ref = engine.create_token(
            controller,
            name=name,
            characteristics={
                "type_line": "Token Creature — Test",
                "power": str(power),
                "toughness": str(toughness),
                "keywords": [],
                "colors": ["G"],
            },
            temporary_keywords=temporary_keywords,
        )[0]
        return engine._resolve_object(
            controller,
            ref,
            zones={"battlefield"},
        )

    @staticmethod
    def place_keyword_counter(engine, card, counter_name: str) -> None:
        results = place_counters(
            engine,
            (
                CounterPlacementRequest(
                    subject_kind="permanent",
                    subject_id=card.object_id,
                    counter_name=counter_name,
                    amount=1,
                    placing_player=card.controller,
                    source_ref=card.ref,
                ),
            ),
            reason="keyword-counter composition witness",
        )
        if len(results) != 1 or results[0].placed != 1:
            raise AssertionError("Keyword-counter placement did not commit")

    @staticmethod
    def set_combat(engine, attacker, *blockers) -> None:
        attacker.attacking = "B"
        for blocker in blockers:
            blocker.blocking = attacker.object_id
        engine.state.combat = CombatState(
            attackers_declared=True,
            blockers_declared=bool(blockers),
            had_attacking_creature=True,
            attackers={attacker.object_id: "B"},
            defending_players=["B"],
            blockers=(
                {attacker.object_id: [card.object_id for card in blockers]}
                if blockers
                else {}
            ),
        )

    def assert_replays(self, session, name: str) -> None:
        expected_hash = authoritative_state_hash(session.state)
        with tempfile.TemporaryDirectory() as temporary:
            record_dir = Path(temporary) / name
            session.save(record_dir)
            replay = replay_record(record_dir, self.db, verify=True)
        self.assertTrue(replay["ok"], replay)
        self.assertEqual(expected_hash, replay["final_state_hash"])
        self.assertEqual(len(session.commands), replay["commands"])

    def test_flying_counter_feeds_offer_and_command_block_legality(self):
        session = self.session(122_001_001, step="declare_blockers")
        engine = session.engine
        engine.state.phase_index = 6
        attacker = self.token(engine, "A", "Counter-granted flyer")
        ground = self.token(engine, "B", "Ground blocker")
        reach = self.token(
            engine,
            "B",
            "Reach blocker",
            temporary_keywords=("Reach",),
        )
        self.place_keyword_counter(engine, attacker, "flying")
        attacker.attacking = "B"
        engine.state.combat = CombatState(
            attackers_declared=True,
            attackers={attacker.object_id: "B"},
            defending_players=["B"],
        )

        engine._begin_blocker_decisions()
        decision = session.packet("pilot:B", full=True)["decision"]
        self.assertNotIn(ground.ref, decision["ctx"]["legal_blocks"])
        self.assertIn(attacker.ref, decision["ctx"]["legal_blocks"][reach.ref])
        self.assertIsNone(session.packet("pilot:C", full=True)["decision"])
        self.assertIsNone(session.packet("pilot:D", full=True)["decision"])
        session.initial_checkpoint = checkpoint_envelope(session.state)
        session.commands.clear()
        session.decisions.clear()

        before = authoritative_state_hash(session.state)
        rejected = session.act(
            "pilot:B",
            {"a": "block", "blk": {ground.ref: attacker.ref}},
        )
        self.assertFalse(rejected.ok)
        self.assertEqual(before, authoritative_state_hash(session.state))
        accepted = session.act("pilot:B", {"a": "block", "blk": {}})
        self.assertTrue(accepted.ok, accepted.summary)
        self.assert_replays(session, "keyword-counter-flying-block")

    def test_vigilance_counter_feeds_four_player_attack_tap_owner(self):
        session = self.session(122_001_002, step="declare_attackers")
        engine = session.engine
        engine.state.phase_index = 5
        attacker = self.token(
            engine,
            "A",
            "Counter-granted vigilant attacker",
            temporary_keywords=("Haste",),
        )
        self.place_keyword_counter(engine, attacker, "vigilance")
        engine._issue_attackers()
        session.initial_checkpoint = checkpoint_envelope(session.state)
        session.commands.clear()
        session.decisions.clear()

        result = session.act(
            "pilot:A",
            {"a": "attack", "atk": {attacker.ref: "B"}},
        )
        self.assertTrue(result.ok, result.summary)
        self.assertFalse(attacker.tapped)
        self.assertEqual("B", attacker.attacking)
        self.assert_replays(session, "keyword-counter-vigilance-attack")

    def test_double_strike_counter_feeds_both_damage_steps(self):
        session = self.session(122_001_003, step="combat_damage")
        engine = session.engine
        engine.state.phase_index = 7
        attacker = self.token(
            engine,
            "A",
            "Counter-granted double striker",
        )
        self.place_keyword_counter(engine, attacker, "double strike")
        self.set_combat(engine, attacker)

        engine._enter_step()
        self.assertTrue(engine.state.combat.first_strike_step)
        self.assertEqual(38, engine.state.players["B"].life)
        engine.pump()
        session.initial_checkpoint = checkpoint_envelope(session.state)
        session.commands.clear()
        session.decisions.clear()

        while engine.state.combat.damage_step_index == 0:
            pass_current(session)

        self.assertEqual(1, engine.state.combat.damage_step_index)
        self.assertEqual(36, engine.state.players["B"].life)
        self.assert_replays(session, "keyword-counter-double-strike")

    def test_lifelink_counter_feeds_final_damage_result(self):
        session = self.session(122_001_004, step="combat_damage")
        engine = session.engine
        engine.state.phase_index = 7
        attacker = self.token(
            engine,
            "A",
            "Counter-granted lifelinker",
            power=3,
            toughness=6,
        )
        first = self.token(engine, "B", "First blocker", power=1)
        second = self.token(engine, "B", "Second blocker", power=1)
        self.place_keyword_counter(engine, attacker, "lifelink")
        self.set_combat(engine, attacker, first, second)
        engine.state.players["A"].life = 20

        engine._begin_combat_damage()
        session.initial_checkpoint = checkpoint_envelope(session.state)
        session.commands.clear()
        session.decisions.clear()
        result = session.act(
            "pilot:A",
            {
                "a": "dmg",
                "assignments": [
                    {
                        "source": attacker.ref,
                        "target": first.ref,
                        "amount": 2,
                    },
                    {
                        "source": attacker.ref,
                        "target": second.ref,
                        "amount": 1,
                    },
                ],
            },
        )

        self.assertTrue(result.ok, result.summary)
        self.assertEqual(23, engine.state.players["A"].life)
        self.assert_replays(session, "keyword-counter-lifelink-damage")

    def test_indestructible_counter_feeds_canonical_destruction(self):
        session = self.session(122_001_005, step="combat_damage")
        engine = session.engine
        permanent = self.token(
            engine,
            "B",
            "Counter-granted indestructible permanent",
        )
        self.place_keyword_counter(engine, permanent, "indestructible")

        protected = destroy_permanent_refs(
            engine,
            (permanent.ref,),
            actor="A",
            reason="keyword-counter Indestructible witness",
        )

        self.assertEqual(
            (permanent.object_id,),
            protected.indestructible_object_ids,
        )
        self.assertEqual("battlefield", permanent.zone)
        removal = plan_counter_removals(
            engine,
            (
                CounterRemoval(
                    object_id=permanent.object_id,
                    counter_name="indestructible",
                    amount=1,
                    expected_logical_object_id=permanent.logical_object_id,
                ),
            ),
        )
        commit_counter_removals(engine, removal)

        destroyed = destroy_permanent_refs(
            engine,
            (permanent.ref,),
            actor="A",
            reason="removed keyword-counter witness",
        )
        self.assertEqual(
            (permanent.object_id,),
            destroyed.destroyed_object_ids,
        )


if __name__ == "__main__":
    unittest.main()
