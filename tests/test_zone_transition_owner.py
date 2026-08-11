from __future__ import annotations

import unittest

from common import keep_all, load_assets, make_session
from quorune import CommanderEngine
from quorune.errors import GameRuleError
from quorune.model import GameState
from quorune.record import authoritative_state_hash
from quorune.zone_transitions import ZoneTransitionOwner
from quorune.zone_trigger_events import ZoneTransitionKind


class ZoneTransitionOwnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db, cls.mishra, cls.zimone = load_assets()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def make_engine(self, seed: int) -> CommanderEngine:
        session = make_session(
            self.db,
            self.mishra,
            self.zimone,
            players=2,
            seed=seed,
        )
        keep_all(session)
        session.engine.permissions.invalidate_current()
        session.engine.state.pending_decision = None
        session.engine.state.priority_player = None
        return session.engine

    @staticmethod
    def card(engine: CommanderEngine, owner: str, name: str):
        return next(
            card
            for card in engine.state.cards.values()
            if card.owner == owner and card.printed_name == name
        )

    def test_engine_facade_and_typed_owner_commit_identical_state(self):
        facade_engine = self.make_engine(4007001)
        owner_engine = CommanderEngine(
            self.db,
            GameState.from_dict(facade_engine.state.to_dict()),
        )
        card = self.card(facade_engine, "A", "Sol Ring")

        facade_engine.move_card(
            card.object_id,
            "battlefield",
            controller="A",
            reason="facade parity",
            semantic_events=True,
        )
        ZoneTransitionOwner(owner_engine).move_card(
            card.object_id,
            "battlefield",
            controller="A",
            reason="facade parity",
            semantic_events=True,
        )

        self.assertEqual(
            authoritative_state_hash(facade_engine.state),
            authoritative_state_hash(owner_engine.state),
        )

    def test_owner_transaction_rolls_back_every_zone_mutation(self):
        engine = self.make_engine(4007002)
        card = self.card(engine, "A", "Sol Ring")
        before = authoritative_state_hash(engine.state)

        with self.assertRaisesRegex(GameRuleError, "rollback witness"):
            with engine.transaction():
                ZoneTransitionOwner(engine).move_card(
                    card.object_id,
                    "battlefield",
                    controller="A",
                    reason="rollback witness",
                    semantic_events=True,
                )
                raise GameRuleError("rollback witness")

        self.assertEqual(before, authoritative_state_hash(engine.state))

    def test_hidden_zone_journal_splits_public_and_private_identity(self):
        engine = self.make_engine(4007003)
        object_id = engine.state.players["B"].zones["library"][-1]
        card = engine.state.cards[object_id]

        ZoneTransitionOwner(engine).move_card(
            object_id,
            "hand",
            reason="private draw-shaped transition",
            log=True,
        )

        public = next(
            event
            for event in reversed(engine.state.events)
            if event.code == "zone.move"
        )
        private = next(
            event
            for event in reversed(engine.state.events)
            if event.code == "zone.move.private"
        )
        self.assertNotIn(card.printed_name, public.summary)
        self.assertNotIn("object", public.details)
        self.assertIn("A", public.visibility)
        self.assertIn(card.printed_name, private.summary)
        self.assertNotIn("A", private.visibility)
        self.assertIn("B", private.visibility)

    def test_simultaneous_moves_share_one_timestamp_and_keep_physical_identity(self):
        engine = self.make_engine(4007004)
        cards = (
            self.card(engine, "A", "Sol Ring"),
            self.card(engine, "A", "Sensei's Divining Top"),
        )
        for card in cards:
            engine.move_card(
                card.object_id,
                "battlefield",
                controller="A",
                log=False,
            )
        physical_ids = tuple(card.object_id for card in cards)

        moved = ZoneTransitionOwner(engine).move_cards_simultaneously(
            tuple((card.object_id, "graveyard") for card in cards),
            reason="simultaneous owner witness",
        )

        self.assertEqual(physical_ids, tuple(card.object_id for card in moved))
        self.assertEqual({"graveyard"}, {card.zone for card in moved})
        self.assertEqual(1, len({card.zone_timestamp for card in moved}))
        self.assertEqual(2, len({card.logical_object_id for card in moved}))

    def test_malformed_transition_and_library_position_fail_before_mutation(self):
        engine = self.make_engine(4007005)
        card = self.card(engine, "A", "Sol Ring")
        before = authoritative_state_hash(engine.state)

        with self.assertRaisesRegex(GameRuleError, "typed event kind"):
            ZoneTransitionOwner(engine).move_card(
                card.object_id,
                "graveyard",
                transition_kind="ordinary",  # type: ignore[arg-type]
            )
        self.assertEqual(before, authoritative_state_hash(engine.state))

        with self.assertRaisesRegex(GameRuleError, "Library position"):
            ZoneTransitionOwner(engine).move_card(
                card.object_id,
                "library",
                position=True,  # type: ignore[arg-type]
            )
        self.assertEqual(before, authoritative_state_hash(engine.state))

        with self.assertRaisesRegex(
            GameRuleError,
            "battlefield permanent",
        ):
            ZoneTransitionOwner(engine).move_card(
                card.object_id,
                "graveyard",
                transition_kind=ZoneTransitionKind.SACRIFICE,
            )
        self.assertEqual(before, authoritative_state_hash(engine.state))


if __name__ == "__main__":
    unittest.main()
