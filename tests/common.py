from __future__ import annotations

import os
from pathlib import Path

from quorune import CardDatabase, CommanderSession, DeckLoader, GameConfig
from quorune.counter_removal import (
    commit_counter_removal_effect,
    CounterRemoval,
    plan_counter_removal_effect,
)
from quorune.model import TurnHistory

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.environ.get("MTG_CARD_DB", ROOT / "data" / "scryfall-20260728-compact.sqlite3"))


def load_assets():
    db = CardDatabase(DB_PATH)
    loader = DeckLoader(db)
    mishra = loader.load(ROOT / "examples" / "mishra-eminent-one.txt", commander="Mishra, Eminent One", deck_name="Mishra")
    zimone = loader.load(ROOT / "examples" / "zimone-and-dina.txt", commander="Zimone and Dina", deck_name="Zimone")
    return db, mishra, zimone


def make_session(db, mishra, zimone, *, players=4, seed=1, auto_pass_empty=False):
    seats = [chr(ord("A") + i) for i in range(players)]
    decks = {seat: (mishra if i % 2 == 0 else zimone) for i, seat in enumerate(seats)}
    return CommanderSession.create(
        db,
        decks,
        first_player="A",
        seed=seed,
        config=GameConfig(seed=seed, auto_pass_empty_priority=auto_pass_empty),
    )


def keep_all(session):
    while session.state.pending_decision and session.state.pending_decision.kind == "mulligan.declare":
        for principal in list(session.pending_principals()):
            result = session.act(principal, {"a": "keep"})
            assert result.ok, result.summary


def pass_current(session, *, yield_mode=None):
    principals = session.pending_principals()
    assert principals
    principal = principals[0]
    response = {"a": "pass"}
    if yield_mode:
        response["y"] = yield_mode
    result = session.act(principal, response)
    assert result.ok, result.summary
    return principal


def set_fixture_turn(engine, turn_sequence: int) -> None:
    """Move a directly seeded rules fixture to a clean turn boundary."""

    engine.state.turn_sequence = int(turn_sequence)
    if engine.state.turn_history is not None:
        engine.state.turn_history = TurnHistory(
            turn_sequence=engine.state.turn_sequence
        )


def advance_fixture_turn(engine, count: int = 1) -> None:
    set_fixture_turn(engine, engine.state.turn_sequence + int(count))


def change_permanent_counter(engine, card, name: str, delta: int) -> tuple[int, int]:
    """Apply a negative fixture delta through the production removal owner."""

    if type(delta) is not int or delta >= 0:
        raise ValueError("Fixture counter removal requires a negative integer")
    result = commit_counter_removal_effect(
        engine,
        plan_counter_removal_effect(
            engine,
            CounterRemoval(
                card.object_id,
                name,
                -delta,
                expected_zone=card.zone,
                expected_logical_object_id=card.logical_object_id,
            ),
        ),
    )
    if result.counter_name == "defense" and result.before and not result.after:
        engine._queue_siege_defeated_trigger(card)
    return result.before, result.after
