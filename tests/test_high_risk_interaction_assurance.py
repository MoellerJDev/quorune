from __future__ import annotations

import unittest

from common import DB_PATH
from high_risk_interaction_support import (
    ALL_HIGH_RISK_BOUNDARY_PAIRS,
    assert_high_risk_boundary_pairs,
)
from quorune.carddb import CardDatabase


class HighRiskInteractionAssuranceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.db = CardDatabase(DB_PATH)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.db.close()

    def test_all_declared_residual_pairs_fail_closed_at_runtime_boundary(
        self,
    ) -> None:
        self.assertEqual(81, len(ALL_HIGH_RISK_BOUNDARY_PAIRS))
        assert_high_risk_boundary_pairs(
            self,
            ALL_HIGH_RISK_BOUNDARY_PAIRS,
            database=self.db,
        )


if __name__ == "__main__":
    unittest.main()
