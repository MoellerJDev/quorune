from __future__ import annotations

from typing import Any, Mapping, Protocol, Sequence

from ..errors import GameRuleError
from ..replacement.immutable import FrozenMap, thaw_value
from .model import (
    SelectionContract,
    SelectionContinuation,
    SelectionModelError,
    decode_selection_continuation,
)


APNAP_OPERATION_ID = "selection.nontarget.apnap.v1"


class ApnapChoiceHost(Protocol):
    state: Any
    active_seats: Sequence[str]
    permissions: Any

    def apnap_order(self) -> list[str]: ...


class ApnapChoiceOwnerMixin:
    """Own ordered multiplayer collection and simultaneous choice commit."""

    def _apnap_selection_continuation(
        self,
        *,
        actor: str,
        state: Mapping[str, Any],
        legal_refs: tuple[str, ...],
    ) -> SelectionContinuation:
        resume = dict(state.get("resume") or {})
        stack_ref = str(resume.get("stack_ref") or "") or None
        item = next(
            (
                candidate
                for candidate in self.state.stack
                if candidate.ref == stack_ref
            ),
            None,
        )
        source_ref = self._stack_source_ref(item) if item is not None else None
        effect = dict(state.get("effect") or {})
        return SelectionContinuation(
            contract=SelectionContract.NONTARGET_CHOICE,
            operation_id=APNAP_OPERATION_ID,
            actor=actor,
            state_revision=self.state.revision,
            stack_ref=stack_ref,
            source_ref=source_ref,
            visibility="actor_private" if bool(effect.get("hidden")) else "public",
            payload=FrozenMap(
                {
                    "choice_state": dict(state),
                    "legal_refs": legal_refs,
                }
            ),
        )

    def _choice_options(self, seat: str, effect: Mapping[str, Any]) -> list[str]:
        zone = str(effect.get("zone") or "battlefield")
        card_type = str((effect.get("filter") or {}).get("type") or "").casefold()
        controller_only = bool((effect.get("filter") or {}).get("controlled", True))
        candidates: list[str] = []
        for object_id in self.state.players[seat].zones.get(zone, []):
            card = self.state.cards[object_id]
            if controller_only and zone == "battlefield" and card.controller != seat:
                continue
            if card_type and card_type not in str(self._effective_card_data(card).get("type_line") or "").casefold():
                continue
            candidates.append(card.ref)
        return candidates

    def _issue_apnap_choice(self, *, effect: Mapping[str, Any], continuation: Mapping[str, Any]) -> None:
        players_spec = effect.get("players", "all")
        if players_spec == "all":
            queue = self.apnap_order()
        elif players_spec == "opponents":
            actor = str(effect.get("actor") or self.state.stack[-1].controller)
            queue = [seat for seat in self.apnap_order() if seat != actor]
        else:
            queue = [seat for seat in players_spec if seat in self.active_seats]
        choice_state = {
            "queue": queue,
            "selected": {},
            "effect": dict(effect),
            "resume": dict(continuation),
        }
        self._issue_next_apnap_choice(choice_state)

    def _issue_next_apnap_choice(self, state: dict[str, Any]) -> None:
        queue = list(state["queue"])
        if not queue:
            self._apply_apnap_choices(state)
            return
        seat = queue[0]
        effect = state["effect"]
        options = self._choice_options(seat, effect)
        count = min(int(effect.get("count", 1)), len(options))
        self.permissions.issue(
            kind="choice.apnap",
            role="pilot",
            actors=[seat],
            allowed_actions=["choose"],
            payload_by_actor={
                seat: {
                    "prompt": str(effect.get("prompt") or "Choose card(s)"),
                    "count": count,
                    "options": options,
                    "prior_public_choices": dict(state["selected"]) if not effect.get("hidden") else {},
                }
            },
            continuation={
                "selection": self._apnap_selection_continuation(
                    actor=seat,
                    state=state,
                    legal_refs=tuple(options),
                ).to_dict()
            },
        )

    def _complete_apnap_choice(self, decision: Any) -> None:
        seat = decision.actors[0]
        raw_continuation = decision.continuation
        legacy_state = dict(raw_continuation.get("choice_state") or {})
        legacy = SelectionContinuation(
            contract=SelectionContract.NONTARGET_CHOICE,
            operation_id=APNAP_OPERATION_ID,
            actor=seat,
            state_revision=decision.created_revision,
            stack_ref=str(
                dict(legacy_state.get("resume") or {}).get("stack_ref") or ""
            )
            or None,
            visibility=(
                "actor_private"
                if bool(dict(legacy_state.get("effect") or {}).get("hidden"))
                else "public"
            ),
            payload=FrozenMap(
                {
                    "choice_state": legacy_state,
                    "legal_refs": self._choice_options(
                        seat, dict(legacy_state.get("effect") or {})
                    )
                    if legacy_state
                    else (),
                }
            ),
        )
        try:
            selection = decode_selection_continuation(
                raw_continuation,
                expected_contract=SelectionContract.NONTARGET_CHOICE,
                expected_operation_id=APNAP_OPERATION_ID,
                legacy=legacy,
            )
        except SelectionModelError as exc:
            raise GameRuleError(str(exc)) from exc
        if selection.actor != seat:
            raise GameRuleError("APNAP choice actor changed")
        if selection.state_revision != decision.created_revision:
            raise GameRuleError("APNAP choice state revision changed")
        payload = thaw_value(selection.payload)
        state = dict(payload.get("choice_state") or {})
        effect = dict(state.get("effect") or {})
        expected_visibility = (
            "actor_private" if bool(effect.get("hidden")) else "public"
        )
        if selection.visibility != expected_visibility:
            raise GameRuleError("APNAP choice visibility changed")
        queue = list(state.get("queue") or [])
        if not queue or queue[0] != seat:
            raise GameRuleError("APNAP choice queue actor changed")
        resume = dict(state.get("resume") or {})
        if str(resume.get("stack_ref") or "") != str(
            selection.stack_ref or ""
        ):
            raise GameRuleError("APNAP choice stack identity changed")
        if "selection" in raw_continuation and selection.stack_ref:
            item = next(
                (
                    candidate
                    for candidate in self.state.stack
                    if candidate.ref == selection.stack_ref
                ),
                None,
            )
            if item is None:
                raise GameRuleError(
                    "The APNAP choice's stack object no longer exists"
                )
            if selection.source_ref != self._stack_source_ref(item):
                raise GameRuleError("APNAP choice source identity changed")
        response = decision.responses[seat]
        values = list(response.get("cards") or response.get("choices") or [])
        options = self._choice_options(seat, effect)
        issued_options = tuple(str(value) for value in payload.get("legal_refs", ()))
        if "selection" in raw_continuation and tuple(options) != issued_options:
            raise GameRuleError("APNAP choice candidates changed")
        required = min(int(effect.get("count", 1)), len(options))
        if len(values) != required:
            raise GameRuleError(f"{seat} must choose exactly {required} option(s)")
        refs: list[str] = []
        for value in values:
            card = self._resolve_object(
                seat,
                str(value),
                zones={str(effect.get("zone") or "battlefield")},
            )
            if card.ref not in options or card.ref in refs:
                raise GameRuleError("Invalid or duplicate APNAP choice")
            refs.append(card.ref)
        selected = dict(state["selected"])
        selected[seat] = refs
        queue = list(state["queue"])[1:]
        state["selected"] = selected
        state["queue"] = queue
        self._issue_next_apnap_choice(state)

    def _apply_apnap_choices(self, state: dict[str, Any]) -> None:
        effect = state["effect"]
        then = str(effect.get("then") or "sacrifice")
        # Choices were made in APNAP order, but the actions happen simultaneously.
        selected_objects: list[str] = []
        for refs in state["selected"].values():
            for ref in refs:
                card = next(card for card in self.state.cards.values() if card.ref == ref)
                selected_objects.append(card.object_id)
        origins = {oid: self.state.cards[oid].zone for oid in selected_objects}
        destination = {
            "sacrifice": "graveyard",
            "discard": "graveyard",
            "exile": "exile",
        }.get(then)
        if destination is None:
            raise GameRuleError(f"Unsupported APNAP continuation {then}")
        self._move_cards_simultaneously(
            [(object_id, destination) for object_id in selected_objects],
            reason=(
                f"simultaneous APNAP {then}"
                if then != "exile"
                else "simultaneous APNAP choice"
            ),
            log=False,
        )
        self._log(None, f"choice.{then}", f"Applied simultaneous {then} choices.", {"objects": [self.state.cards[oid].ref for oid in selected_objects], "origins": origins}, importance=2, changed_objects=selected_objects)
        resume = state["resume"]
        self._continue_resolution(
            stack_ref=str(resume["stack_ref"]),
            effects=[dict(item) for item in resume.get("effects", [])],
            destination=resume.get("destination"),
            note=str(resume.get("note") or ""),
        )
