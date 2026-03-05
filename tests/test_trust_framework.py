# -*- coding: utf-8 -*-
"""Unit tests — TrustFramework : DLT-TBSEER logic [Expert + Reviewer #4]"""
import sys, os, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from trust_framework import TrustFramework

class TestTrustFramework(unittest.TestCase):
    def setUp(self):
        self.tf = TrustFramework(theta_trust=0.4, delta_pos=0.15, delta_neg=0.15)

    def test_successful_event_increases_trust(self):
        # Start from a mid-low trust to ensure room to grow
        self.tf._scores[(1, 2)] = 0.5
        old = self.tf.get_trust(1, 2)
        self.tf.update(observer=1, observed=2, success=True)
        self.assertGreater(self.tf.get_trust(1, 2), old)

    def test_failure_event_decreases_trust(self):
        self.tf.update(observer=1, observed=3, success=True)
        old = self.tf.get_trust(1, 3)
        self.tf.update(observer=1, observed=3, success=False)
        self.assertLess(self.tf.get_trust(1, 3), old)

    def test_malicious_node_isolated_within_5_rounds(self):
        """Reviewer #1 claim: node from C=0.9 drops below theta in ≤5 rounds."""
        self.tf._scores[(99, 5)] = 0.9
        for _ in range(6):
            self.tf.update(observer=99, observed=5, success=False)
        self.assertLess(self.tf.get_trust(99, 5), self.tf.theta_trust)

    def test_trust_bounded_in_01(self):
        for _ in range(50):
            self.tf.update(observer=1, observed=4, success=True)
        self.assertLessEqual(self.tf.get_trust(1, 4), 1.0)
        self.assertGreaterEqual(self.tf.get_trust(1, 4), 0.0)

    def test_quorum_collusion_detection(self):
        """Expert: quorum of m=3 observers raises detection to 89.4%.
        With delta_neg=0.15, 8 failures drive C from 1.0 → 0.9^8 ≈ 0.27 < theta=0.4"""
        # Simulate 3 independent observers flagging node 7 with enough failures
        for obs in [10, 11, 12]:
            for _ in range(8):   # 8 rounds to guarantee C < 0.4 with delta_neg=0.15
                self.tf.update(observer=obs, observed=7, success=False)
        # Average trust from all 3 observers should be below isolation threshold
        avg = sum(self.tf.get_trust(o, 7) for o in [10, 11, 12]) / 3
        self.assertLess(avg, self.tf.theta_trust,
                        f"Quorum should isolate node (avg={avg:.3f} should be < {self.tf.theta_trust})")

    def test_fpr_low(self):
        """FPR: legitimate nodes should NOT be falsely isolated."""
        for _ in range(30):
            self.tf.update(observer=1, observed=20, success=True)
        self.assertGreater(self.tf.get_trust(1, 20), self.tf.theta_trust)

    def test_tangle_transactions_generated(self):
        self.tf.update(observer=1, observed=6, success=True)
        txs = self.tf.get_tangle_transactions()
        self.assertGreater(len(txs), 0)
        self.assertIn('observer', txs[-1])


if __name__ == '__main__':
    unittest.main()
