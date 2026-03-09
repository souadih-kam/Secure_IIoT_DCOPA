# -*- coding: utf-8 -*-
"""
TrustFramework — DLT-TBSEER Trust Calculation and Update Logic
==============================================================
Implements the trust update rule and isolation mechanism described in
Section 8 (DLT-TBSEER Trust Framework) of the paper.

This module corresponds to:
  - Equation 2   : Multiplicative trust update rule
  - Equation (gamma_R) : Adaptive trust weight (sigmoid normalization)
  - Algorithm 12 : Malicious Node Isolation

Authors: Souadih Kamal, Mir Foudil
License: MIT (reproducibility package only)
"""

import math
from typing import Dict, Optional


class TrustFramework:
    """
    DLT-TBSEER trust management for Secure-IIoT-DCOPA.

    Models the trust evolution of a node as observed by its neighbors.
    Trust scores are in [0, 1]; isolation is triggered when the score
    falls below theta_trust.

    Parameters
    ----------
    delta_pos : float
        Positive reinforcement factor for successful interactions.
        Paper value: 0.10
    delta_neg : float
        Negative penalty factor for failed/malicious interactions.
        Paper value: 0.15  (faster decay than reward — asymmetric)
    theta_trust : float
        Isolation threshold.
        Paper value: 0.40
    gamma0 : float
        Base trust weight in the timer equation (Eq. 1).
        Paper value: 0.30
    """

    def __init__(
        self,
        delta_pos: float = 0.10,
        delta_neg: float = 0.15,
        theta_trust: float = 0.40,
        gamma0: float = 0.30,
        sigma0: float = 0.15,
        k_sigmoid: float = 20.0,
    ):
        self.delta_pos = delta_pos
        self.delta_neg = delta_neg
        self.theta_trust = theta_trust
        self.gamma0 = gamma0
        self.sigma0 = sigma0        # Activation threshold for adaptive γ_R
        self.k_sigmoid = k_sigmoid  # Sigmoid sharpness

    # ------------------------------------------------------------------
    # Trust Update Rule (Equation 2)
    # ------------------------------------------------------------------

    def update_trust(self, current_trust: float, success: bool) -> float:
        """
        Update trust score after one interaction.

        Positive update (success=True):
            C^{t+1} = C^t + δ_pos · (1 - C^t)   [bounded, approaches 1]

        Negative update (success=False):
            C^{t+1} = C^t · (1 - δ_neg)          [multiplicative decay]

        The asymmetric design ensures that:
        - A node starting at C=0.9 reaches C < θ_trust in ≈5 rounds
          when δ_neg=0.15 (fast isolation).
        - A fully trusted node (C=1.0) requires many consecutive failures
          before isolation — robust against transient faults.
        """
        if success:
            # Additive reward (bounded to [0,1])
            return min(1.0, current_trust + self.delta_pos * (1.0 - current_trust))
        else:
            # Multiplicative penalty (ensures C stays in [0,1])
            return max(0.0, current_trust * (1.0 - self.delta_neg))

    # ------------------------------------------------------------------
    # Isolation Decision (Algorithm 12)
    # ------------------------------------------------------------------

    def should_isolate(self, trust_score: float) -> bool:
        """
        Return True if the node should be isolated.

        A node is isolated when its trust score falls below theta_trust.
        Once isolated, it is removed from routing and CH election.
        """
        return trust_score < self.theta_trust

    # ------------------------------------------------------------------
    # Adaptive Trust Weight γ_R (Added per Reviewer #1 — Point 6)
    # ------------------------------------------------------------------

    def adaptive_gamma_r(self, sigma_c: float) -> float:
        """
        Compute the adaptive trust weight γ_R(t) via a sigmoid function.

        γ_R(t) = γ_0 · σ(k · (σ_C(t) − σ_0))

        where:
          σ_C(t) = std of trust scores in the network at round t
          σ_0    = activation threshold (benign network: σ_C ≈ 0)
          k      = sigmoid sharpness

        Properties:
          - σ_C → 0 (uniform trust, benign): γ_R → 0   (trust term inactive)
          - σ_C > σ_0 (malicious nodes present): γ_R → γ_0  (fully active)
          - Bounded: γ_R ∈ [0, γ_0]

        Parameters
        ----------
        sigma_c : float
            Standard deviation of trust scores across the network.
        """
        sigmoid = 1.0 / (1.0 + math.exp(-self.k_sigmoid * (sigma_c - self.sigma0)))
        return self.gamma0 * sigmoid

    # ------------------------------------------------------------------
    # Collusion Detection Utility
    # ------------------------------------------------------------------

    def rounds_to_isolation(self, initial_trust: float) -> int:
        """
        Estimate how many consecutive failed rounds until isolation.

        Used to assess the vulnerability window for collusion attacks
        (Section 7.1 of the paper).

        Formula: r_drop = ⌈log(θ_trust / C_0) / log(1 − δ_neg)⌉
        """
        if initial_trust <= self.theta_trust:
            return 0
        log_ratio = math.log(self.theta_trust / initial_trust)
        log_decay = math.log(1.0 - self.delta_neg)
        return math.ceil(log_ratio / log_decay)


class NetworkTrustState:
    """
    Tracks trust scores for all nodes in the network.
    Provides aggregate statistics used by adaptive γ_R.
    """

    def __init__(self, trust_framework: TrustFramework):
        self.tf = trust_framework
        self.scores: Dict[int, float] = {}

    def initialize_node(self, node_id: int, initial_trust: float = 1.0):
        """Register a new node with an initial trust score."""
        self.scores[node_id] = initial_trust

    def record_interaction(self, observer_id: int, target_id: int, success: bool):
        """Update trust from observer's perspective after one interaction."""
        if target_id not in self.scores:
            self.scores[target_id] = 1.0
        self.scores[target_id] = self.tf.update_trust(
            self.scores[target_id], success
        )

    def get_trust(self, node_id: int) -> float:
        """Get current trust score of a node (default: 1.0 if unknown)."""
        return self.scores.get(node_id, 1.0)

    def get_isolated_nodes(self):
        """Return set of node IDs that should be isolated."""
        return {nid for nid, score in self.scores.items()
                if self.tf.should_isolate(score)}

    def trust_dispersion(self) -> float:
        """
        Compute σ_C(t): standard deviation of all trust scores.
        Used as input to adaptive_gamma_r().
        """
        if len(self.scores) < 2:
            return 0.0
        mean = sum(self.scores.values()) / len(self.scores)
        variance = sum((s - mean) ** 2 for s in self.scores.values()) / len(self.scores)
        return math.sqrt(variance)

    def current_gamma_r(self) -> float:
        """Compute the current adaptive γ_R based on network trust state."""
        return self.tf.adaptive_gamma_r(self.trust_dispersion())




class TrustFramework:
    """
    DLT-TBSEER trust management logic.
    Added: quorum detection (Expert), tangle transaction log (Reviewer #4).
    """
    def __init__(self, theta_trust=0.4, delta_pos=0.1, delta_neg=0.15):
        self.theta_trust = theta_trust
        self.delta_pos   = delta_pos
        self.delta_neg   = delta_neg
        self._scores     = {}
        self._tangle_log = []

    def get_trust(self, observer, observed):
        return self._scores.get((observer, observed), 1.0)

    def update(self, observer, observed, success: bool):
        C = self.get_trust(observer, observed)
        if success:
            C_new = C + self.delta_pos * (1.0 - C)
        else:
            C_new = C * (1.0 - self.delta_neg)
        C_new = max(0.0, min(1.0, C_new))
        self._scores[(observer, observed)] = C_new
        self._tangle_log.append({
            'observer': observer, 'observed': observed,
            'success': success, 'score': C_new
        })

    def get_tangle_transactions(self):
        return list(self._tangle_log)

    def is_isolated(self, trusted_observers, observed, quorum_m=1):
        """Return True if >= quorum_m observers see observed below threshold."""
        count = sum(
            1 for obs in trusted_observers
            if self.get_trust(obs, observed) < self.theta_trust
        )
        return count >= quorum_m
