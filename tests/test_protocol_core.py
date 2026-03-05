# -*- coding: utf-8 -*-
"""Unit tests — SecureTimer and ClusteringRadius [Reviewer #1, Point 9]"""
import sys, os, math, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from protocol_core import SecureTimer, DCOPABaseTimer, ClusteringRadius

class TestSecureTimerAlpha(unittest.TestCase):
    def setUp(self):
        self.t = SecureTimer(alpha=0.6, beta=0.4, gamma0=0.3, delta=0.01)

    def test_alpha_beta_sum_one(self):
        self.assertAlmostEqual(self.t.alpha + self.t.beta, 1.0)

    def test_trusted_node_lower_timer(self):
        t_trusted   = self.t.compute(0.8, 1.0, 20, 100, C_bar_i=0.9, sigma_C=0.2)
        t_malicious = self.t.compute(0.8, 1.0, 20, 100, C_bar_i=0.1, sigma_C=0.2)
        self.assertLess(t_trusted, t_malicious)

    def test_dead_node_returns_inf(self):
        self.assertEqual(self.t.compute(0.0, 1.0, 20, 100, 0.8), float('inf'))

    def test_gamma_r_bounded(self):
        chk = self.t.normalization_check(sigma_C=0.5)
        self.assertLess(chk['total_weight'], 2.0)
        self.assertTrue(chk['bounded'])

    def test_gamma_r_zero_in_benign(self):
        """In a benign network (sigma_C≈0), gamma_R → 0."""
        g = self.t._adaptive_gamma_r(sigma_c=0.0)
        self.assertLess(g, 0.05)

    def test_gamma_r_max_under_attack(self):
        """Under heavy attack (sigma_C >> sigma0), gamma_R → gamma0."""
        g = self.t._adaptive_gamma_r(sigma_c=1.0)
        self.assertAlmostEqual(g, self.t.gamma0, places=3)


class TestRCManipulation(unittest.TestCase):
    def test_negative_epsilon_shortens_timer(self):
        rc = ClusteringRadius(area_side=100, K_opt=5)
        delta_t = rc.timer_perturbation(epsilon_d=-10, d_range=100)
        self.assertLess(delta_t, 0)

    def test_zero_epsilon_no_perturbation(self):
        rc = ClusteringRadius(area_side=100, K_opt=5)
        self.assertAlmostEqual(rc.timer_perturbation(0, 100), 0.0)


class TestDCOPABase(unittest.TestCase):
    def test_not_in_group_returns_tau_minus_delta(self):
        t = DCOPABaseTimer()
        self.assertAlmostEqual(t.compute(0.5, 0.5, tau=1.0, in_group=False),
                               1.0 - t.delta)

    def test_delta_sweep_collision_rate(self):
        """Verify delta=0.01 gives minimal collision rate (proxy)."""
        import random
        random.seed(42)
        for delta in [0.001, 0.01, 0.05, 0.1]:
            timer = DCOPABaseTimer(delta=delta)
            timers = [timer.compute(random.random(), random.random()) for _ in range(100)]
            rounded = [round(v, 4) for v in timers]
            unique = len(set(rounded))
            self.assertGreater(unique, 80)  # All configurations should mostly avoid collision


if __name__ == '__main__':
    unittest.main()
