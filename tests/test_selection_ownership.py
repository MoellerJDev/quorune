from __future__ import annotations

import copy
import unittest

from quorune.replacement.immutable import FrozenMap
from quorune.selection import (
    SelectionContinuation,
    SelectionContract,
    SelectionModelError,
    decode_selection_continuation,
)


class SelectionContinuationTests(unittest.TestCase):
    @staticmethod
    def continuation(**changes):
        values = {
            "contract": SelectionContract.SEARCH,
            "operation_id": "selection.search.semantic.v1",
            "actor": "B",
            "state_revision": 19,
            "stack_ref": "S7",
            "source_ref": "B12",
            "visibility": "actor_private",
            "payload": {
                "legal_refs": ["B20", "B21"],
                "search": {"zone": "library", "minimum": 0},
            },
        }
        values.update(changes)
        return SelectionContinuation(**values)

    def test_round_trip_is_deeply_immutable_and_canonical(self):
        supplied = {
            "legal_refs": ["B20", "B21"],
            "search": {"minimum": 0, "zone": "library"},
        }
        continuation = self.continuation(payload=supplied)
        expected = continuation.to_dict()
        supplied["legal_refs"].append("B22")
        supplied["search"]["minimum"] = 1

        self.assertEqual(expected, continuation.to_dict())
        restored = SelectionContinuation.from_dict(continuation.to_dict())
        self.assertEqual(continuation, restored)
        self.assertEqual(continuation.fingerprint, restored.fingerprint)
        self.assertIsInstance(restored.payload, FrozenMap)

        reordered = self.continuation(
            payload={
                "search": {"zone": "library", "minimum": 0},
                "legal_refs": ["B20", "B21"],
            }
        )
        self.assertEqual(continuation.fingerprint, reordered.fingerprint)

    def test_material_identity_changes_change_fingerprint(self):
        original = self.continuation()
        for changed in (
            self.continuation(actor="A"),
            self.continuation(state_revision=20),
            self.continuation(stack_ref="S8"),
            self.continuation(source_ref="B13"),
            self.continuation(
                payload={
                    "legal_refs": ["B20"],
                    "search": {"zone": "library", "minimum": 0},
                }
            ),
        ):
            self.assertNotEqual(original.fingerprint, changed.fingerprint)

    def test_malformed_or_extended_envelopes_fail_closed(self):
        valid = self.continuation().to_dict()
        cases = [
            {key: value for key, value in valid.items() if key != "actor"},
            {**valid, "unknown": True},
            {**valid, "schema_version": True},
            {**valid, "state_revision": True},
            {**valid, "payload": []},
            {**valid, "payload": {"bad": object()}},
        ]
        for value in cases:
            with self.subTest(value=value):
                with self.assertRaises(SelectionModelError):
                    SelectionContinuation.from_dict(value)
        with self.assertRaisesRegex(
            SelectionModelError, "must be a mapping"
        ):
            SelectionContinuation.from_dict([])  # type: ignore[arg-type]

    def test_contract_and_operation_are_not_interchangeable(self):
        continuation = self.continuation()
        envelope = {"selection": continuation.to_dict()}
        self.assertEqual(
            continuation,
            decode_selection_continuation(
                envelope,
                expected_contract=SelectionContract.SEARCH,
                expected_operation_id="selection.search.semantic.v1",
            ),
        )
        with self.assertRaisesRegex(SelectionModelError, "contract changed"):
            decode_selection_continuation(
                envelope,
                expected_contract=SelectionContract.TARGETING,
                expected_operation_id="selection.search.semantic.v1",
            )
        with self.assertRaisesRegex(
            SelectionModelError, "operation identity changed"
        ):
            decode_selection_continuation(
                envelope,
                expected_contract=SelectionContract.SEARCH,
                expected_operation_id="selection.search.other.v1",
            )

    def test_legacy_shape_requires_an_explicit_pinned_adapter(self):
        continuation = self.continuation()
        with self.assertRaisesRegex(SelectionModelError, "envelope is missing"):
            decode_selection_continuation(
                {},
                expected_contract=SelectionContract.SEARCH,
                expected_operation_id="selection.search.semantic.v1",
            )
        self.assertEqual(
            continuation,
            decode_selection_continuation(
                {"legacy": copy.deepcopy(continuation.to_dict())},
                expected_contract=SelectionContract.SEARCH,
                expected_operation_id="selection.search.semantic.v1",
                legacy=continuation,
            ),
        )


if __name__ == "__main__":
    unittest.main()
