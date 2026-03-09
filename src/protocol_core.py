# -*- coding: utf-8 -*-
"""
ProtocolCore — Secure-IIoT-DCOPA Timer and DCOPA Core Computation
==================================================================
Implements the competitive timer equations from the paper:

  DCOPA base timer (Section 5, Eq. original):
    T(i) = (α·E_i + β·D_i)·(τ − δ)   if i ∈ G
           τ − δ                       otherwise

  Secure-IIoT-DCOPA modified timer (Section 6.2, Eq. 1):
    T_i = T_base · (α·E_max/E_i + β·d(i,BS)/d_max + γ_R·(1 − C̄_i))

  RC clustering radius (Section 5.3):
    RC = 2M / √(πK)

Authors: Souadih Kamal, Mir Foudil
License: MIT (reproducibility package only)
"""

import math
from typing import Optional


class SecureTimer:
    """
    Secure-IIoT-DCOPA competitive timer with trust-integrated election.

    This implements Equation 1 of the paper, extended with the adaptive
    γ_R normalization added per Reviewer #1 (Point 6).

    Parameters
    ----------
    alpha : float
        Energy weight. Paper value: 0.6
        (Spearman ρ=0.87 with network lifetime)
    beta : float
        Distance weight. Paper value: 0.4
        (Spearman ρ=0.61 with per-round energy cost)
        Constraint: alpha + beta = 1.0
    gamma0 : float
        Base trust weight. Paper value: 0.3
        (adaptive: actual γ_R ∈ [0, gamma0] via sigmoid)
    delta : float
        Tie-breaking constant. Paper value: 0.01
        (sweep {0.001, 0.01, 0.05, 0.1} → collision rate < 0.3%)
    """

    def __init__(
        self,
        alpha: float = 0.6,
        beta: float = 0.4,
        gamma0: float = 0.3,
        delta: float = 0.01,
        sigma0: float = 0.15,
        k_sigmoid: float = 20.0,
    ):
        assert abs(alpha + beta - 1.0) < 1e-9, "alpha + beta must equal 1.0"
        self.alpha = alpha
        self.beta = beta
        self.gamma0 = gamma0
        self.delta = delta
        self.sigma0 = sigma0
        self.k_sigmoid = k_sigmoid

    def _adaptive_gamma_r(self, sigma_c: float) -> float:
        """Compute adaptive trust weight via sigmoid (Eq. gamma_R_adaptive)."""
        sigmoid = 1.0 / (1.0 + math.exp(-self.k_sigmoid * (sigma_c - self.sigma0)))
        return self.gamma0 * sigmoid

    def compute(
        self,
        E_i: float,
        E_max: float,
        d_i: float,
        d_max: float,
        C_bar_i: float,
        sigma_C: float = 0.0,
        T_base: float = 1.0,
    ) -> float:
        """
        Compute the Secure-IIoT-DCOPA timer value T_i.

        T_i = T_base · (α · E_max/E_i  +  β · d_i/d_max  +  γ_R(t) · (1 − C̄_i))

        The node with the SMALLEST timer broadcasts its CH candidacy first.
        High energy + close to BS + high trust → small timer → higher CH probability.

        Parameters
        ----------
        E_i : float
            Residual energy of node i (Joules).
        E_max : float
            Maximum initial energy (Joules).
        d_i : float
            Distance from node i to Base Station (meters).
        d_max : float
            Maximum distance in the network (meters).
        C_bar_i : float
            Average trust score attributed to node i by its neighbors ∈ [0,1].
        sigma_C : float
            Standard deviation of trust scores in the network at this round.
            Used to compute adaptive γ_R. Default 0 (γ_R ≈ 0, benign network).
        T_base : float
            Base timer duration (seconds). Default: 1.0

        Returns
        -------
        float
            Timer value T_i ≥ 0. Lower → higher CH election priority.
        """
        if E_i <= 0 or E_max <= 0 or d_max <= 0:
            return float('inf')  # Dead or invalid node — never elected

        energy_term = self.alpha * (E_max / E_i)
        distance_term = self.beta * (d_i / d_max)
        gamma_r = self._adaptive_gamma_r(sigma_C)
        trust_term = gamma_r * (1.0 - C_bar_i)

        return T_base * (energy_term + distance_term + trust_term)

    def normalization_check(self, sigma_C: float = 0.2) -> dict:
        """
        Verify the normalization constraint α + β + γ_R < 2·T_base.

        Returns a summary dict with all component weights.
        """
        gamma_r = self._adaptive_gamma_r(sigma_C)
        total = self.alpha + self.beta + gamma_r
        return {
            'alpha': self.alpha,
            'beta': self.beta,
            'gamma_R': gamma_r,
            'total_weight': total,
            'bounded': total < 2.0,  # Ensures T_i < 2·T_base
        }


class DCOPABaseTimer:
    """
    Original DCOPA timer (without trust factor) for comparison.

    T(i) = (α·E_i + β·D_i)·(τ − δ)

    where:
      E_i = normalized residual energy ∈ [0,1]
      D_i = normalized distance ∈ [0,1]
      τ   = round duration
      δ   = tie-breaking constant
    """

    def __init__(self, alpha: float = 0.6, beta: float = 0.4, delta: float = 0.01):
        self.alpha = alpha
        self.beta = beta
        self.delta = delta

    def normalize_energy(self, E_i: float, E_min: float, E_max: float) -> float:
        """Normalize residual energy to [0,1]."""
        if E_max == E_min:
            return 0.5
        return (E_i - E_min) / (E_max - E_min)

    def normalize_distance(self, d_i: float, d_min: float, d_max: float) -> float:
        """Normalize distance to BS to [0,1]."""
        if d_max == d_min:
            return 0.5
        return (d_i - d_min) / (d_max - d_min)

    def compute(
        self,
        E_i_norm: float,
        D_i_norm: float,
        tau: float = 1.0,
        in_group: bool = True,
    ) -> float:
        """
        Compute DCOPA base timer.

        Parameters
        ----------
        E_i_norm : float  Normalized energy ∈ [0,1]
        D_i_norm : float  Normalized distance ∈ [0,1]
        tau : float       Round duration
        in_group : bool   Whether node is eligible for CH election
        """
        if not in_group:
            return tau - self.delta
        return (self.alpha * E_i_norm + self.beta * D_i_norm) * (tau - self.delta)


class ClusteringRadius:
    """
    RC computation and RC manipulation impact analysis.

    RC = 2M / √(πK)

    where M² is the deployment area and K the optimal number of clusters.
    """

    def __init__(self, area_side: float, K_opt: int):
        """
        Parameters
        ----------
        area_side : float  Side length of square deployment area (meters)
        K_opt : int        Optimal number of clusters
        """
        self.M = area_side
        self.K = K_opt
        self.RC = 2 * area_side / math.sqrt(math.pi * K_opt)

    def timer_perturbation(
        self, epsilon_d: float, d_range: float, tau: float = 1.0, delta: float = 0.01, beta: float = 0.4
    ) -> float:
        """
        Compute the timer perturbation caused by distance falsification.

        ΔT(i) = β · ε_d / (d_max − d_min) · (τ − δ)

        A negative ε_d (node claims proximity) → ΔT < 0 → fraudulent
        CH election boost (see Section 5.3.1 — Point 4 of reviewer corrections).

        Parameters
        ----------
        epsilon_d : float  Distance falsification error (m). Negative = fake proximity.
        d_range : float    d_max − d_min (m)
        """
        if d_range == 0:
            return 0.0
        return beta * (epsilon_d / d_range) * (tau - delta)
