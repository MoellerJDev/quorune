from __future__ import annotations

import unittest

from common import keep_all, load_assets, make_session
from quorune.errors import GameRuleError, StateInvariantError
from quorune.record import authoritative_state_hash
from quorune.turn_priority_model import PriorityGrantPlan, PriorityPassPlan


class TurnPriorityDecisionOwnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db, cls.mishra, cls.zimone = load_assets()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def make_engine(self, seed: int):
        session = make_session(
            self.db,
            self.mishra,
            self.zimone,
            players=2,
            seed=seed,
        )
        keep_all(session)
        engine = session.engine
        engine.permissions.invalidate_current()
        engine.state.pending_decision = None
        engine.state.priority_player = None
        engine.state.priority_passes = []
        return engine

    def test_priority_plans_are_closed_immutable_and_canonical(self):
        grant = PriorityGrantPlan("A", 4, cleanup_frame=False)
        self.assertEqual(grant, PriorityGrantPlan.from_dict(grant.to_dict()))
        with self.assertRaisesRegex(ValueError, "invalid shape"):
            PriorityGrantPlan.from_dict({**grant.to_dict(), "extra": True})
        with self.assertRaisesRegex(ValueError, "exact integer"):
            PriorityGrantPlan("A", True)  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "nonempty string"):
            PriorityGrantPlan.from_dict(
                {"seat": 1, "priority_epoch": 4, "cleanup_frame": False}
            )

        passed = PriorityPassPlan(
            seat="A",
            passes=("A",),
            next_seat="B",
            round_complete=False,
            stack_waiting=False,
        )
        self.assertEqual(passed, PriorityPassPlan.from_dict(passed.to_dict()))
        with self.assertRaisesRegex(ValueError, "unique"):
            PriorityPassPlan(
                seat="A",
                passes=("A", "A"),
                next_seat="B",
                round_complete=False,
                stack_waiting=False,
            )
        with self.assertRaisesRegex(ValueError, "cannot name a next seat"):
            PriorityPassPlan(
                seat="A",
                passes=("A", "B"),
                next_seat="A",
                round_complete=True,
                stack_waiting=False,
            )
        with self.assertRaisesRegex(ValueError, "nonempty string"):
            PriorityPassPlan.from_dict(
                {
                    "seat": "A",
                    "passes": ["A"],
                    "next_seat": 2,
                    "round_complete": False,
                    "stack_waiting": False,
                }
            )

    def test_engine_facade_commits_through_typed_priority_owner(self):
        engine = self.make_engine(5001001)
        owner = engine.turn_priority
        plan = owner.prepare_priority_grant("A", cleanup_frame=False)
        self.assertIsNotNone(plan)
        assert plan is not None
        self.assertEqual(engine.state.priority_epoch + 1, plan.priority_epoch)

        owner.commit_priority_grant(plan)

        self.assertEqual("A", engine.state.priority_player)
        self.assertEqual([], engine.state.priority_passes)
        self.assertEqual(plan.priority_epoch, engine.state.priority_epoch)
        with self.assertRaisesRegex(StateInvariantError, "stale"):
            owner.commit_priority_grant(plan)

    def test_priority_pass_plan_preserves_turn_order_and_rejects_wrong_actor(self):
        engine = self.make_engine(5001002)
        engine._grant_priority("A")

        with self.assertRaisesRegex(GameRuleError, "does not have priority"):
            engine.turn_priority.prepare_priority_pass("B")
        plan = engine.turn_priority.prepare_priority_pass("A")
        self.assertEqual(("A",), plan.passes)
        self.assertEqual("B", plan.next_seat)
        self.assertFalse(plan.round_complete)

        engine.turn_priority.commit_priority_pass(plan, automatic=True)
        self.assertEqual("B", engine.state.priority_player)
        self.assertEqual(["A"], engine.state.priority_passes)

    def test_yield_epochs_retain_game_record_v3_keys_and_invalidate(self):
        engine = self.make_engine(5001003)
        engine._grant_priority("A")
        engine._set_yield("A", "until_public_change")
        before = engine._yield_change_epoch("stack")

        engine._log(
            "A",
            "stack.cast",
            "A stack object changed the priority window.",
            importance=0,
        )

        self.assertEqual(before + 1, engine._yield_change_epoch("stack"))
        self.assertIn("yield_change:stack", engine.state.ref_counters)
        self.assertEqual("stack", engine._yield_stop_reason("A"))

    def test_owner_mutation_rolls_back_and_remains_bound_to_live_state(self):
        engine = self.make_engine(5001004)
        before = authoritative_state_hash(engine.state)

        with self.assertRaisesRegex(GameRuleError, "rollback witness"):
            with engine.transaction():
                engine._grant_priority("A")
                raise GameRuleError("rollback witness")

        self.assertEqual(before, authoritative_state_hash(engine.state))
        engine._grant_priority("A")
        self.assertEqual("A", engine.state.priority_player)

    def test_priority_decision_payload_has_stable_yield_modes(self):
        engine = self.make_engine(5001005)
        engine._grant_priority("A")
        decision = engine._issue_priority(
            "A",
            {
                "actions": [{"id": "pass", "kind": "pass"}],
                "cast": [],
                "lands": [],
                "abilities": [],
                "mana_abilities": [],
            },
        )

        self.assertEqual(
            [
                "none",
                "until_public_change",
                "until_my_turn",
                "auto_if_no_response",
            ],
            decision.payload_by_actor["A"]["yield_modes"],
        )


if __name__ == "__main__":
    unittest.main()
