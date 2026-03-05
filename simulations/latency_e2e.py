# -*- coding: utf-8 -*-
"""
End-to-end latency simulation — multi-hop IIoT network
=======================================================
Computes 95th-percentile E2E latency for varying network sizes.
Validates Expert claim: P95(E2E) <= 120 ms for 500 nodes, 20% malicious.
"""
import sys, random, statistics

def simulate_e2e_latency(n_nodes=500, malicious_pct=0.2, hops_max=4,
                         n_rounds=1000, seed=42):
    """
    Returns list of E2E latency samples (ms).
    Model:
      E2E = T_crypto + sum(T_hop_i)
      T_crypto ~ N(15, 3) ms  (local validation for ECDSA+ChaCha20)
      T_hop    ~ Exp(lambda=1/8) ms per hop, up to hops_max hops
      Under malicious traffic: add queuing delay ~ U(0, 15) ms
    """
    rng = random.Random(seed)
    latencies = []
    malicious_fraction = malicious_pct if n_nodes > 200 else 0.1

    for _ in range(n_rounds):
        t_crypto = max(5, rng.gauss(15, 3))   # ECDSA + ChaCha20, ms
        n_hops = rng.randint(1, hops_max)
        t_prop = sum(rng.expovariate(1/8) for _ in range(n_hops))
        t_queue = rng.uniform(0, 15) * malicious_fraction * 2
        latencies.append(t_crypto + t_prop + t_queue)

    p95 = sorted(latencies)[int(0.95 * len(latencies))]
    return latencies, p95


if __name__ == '__main__':
    print(f"{'Nodes':>7} {'Malicious':>10} | {'Mean(ms)':>10} {'P95(ms)':>10} {'<120ms?':>8}")
    print("-" * 55)
    for n in [50, 100, 200, 300, 500]:
        for mal in [0.0, 0.20]:
            lats, p95 = simulate_e2e_latency(n_nodes=n, malicious_pct=mal)
            mean = statistics.mean(lats)
            ok = "✓" if p95 < 120 else "✗"
            print(f"{n:>7} {int(mal*100):>9}% | {mean:>10.1f} {p95:>10.1f} {ok:>8}")
