# Secure-IIoT-DCOPA — Reproducibility Package

[![CI](https://github.com/SecIIoT/Secure-IIoT-DCOPA/actions/workflows/ci.yml/badge.svg)](https://github.com/SecIIoT/Secure-IIoT-DCOPA/actions)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10850224.svg)](https://doi.org/10.5281/zenodo.10850224)

**Paper:** *Secure-IIoT-DCOPA: Tangle-Based Immutable Trust for Resilient Clustering in Critical IIoT*
**Journal:** Journal of Information Security and Applications (JISA)
**Authors:** Souadih Kamal, Mir Foudil, Meziane Farid

---

## Reproducibility Identifiers (Reviewer #1, Point 9)

| Artefact | Value |
|----------|-------|
| GitHub URL | `https://github.com/SecIIoT/Secure-IIoT-DCOPA` |
| Release tag | `v1.0` |
| **Source SHA-256** | `afd7664095f370eba864897461446fdaf0351f8dafdb2420f5ac57e612408eb6` |
| Zenodo DOI | `10.5281/zenodo.10850224` |

---

## Repository Structure

```
Secure_IIoT_DCOPA_GitHub/
├── src/
│   ├── protocol_core.py       # SecureTimer, DCOPA timer, RC radius (Eq. 1)
│   ├── crypto_engine.py       # ECDSA, ECDH, ChaCha20-Poly1305 (Alg. 3, 5, 8)
│   ├── trust_framework.py     # DLT-TBSEER trust + quorum detection
│   └── __init__.py
├── tests/
│   ├── test_protocol_core.py  # 20+ unit tests — timer equations
│   ├── test_crypto_engine.py  # 15+ unit tests — ECDSA/ECDH/ChaCha20
│   └── test_trust_framework.py# 15+ unit tests — trust, quorum, FPR
├── simulations/
│   ├── collusion_experiment.py# Quorum vs base: 89.4% vs 47% detection
│   └── latency_e2e.py         # E2E P95 latency: ≤ 120 ms for 500 nodes
├── config/
│   └── default_config.yaml    # All paper parameters (α, β, γ₀, δ …)
├── results_sample/
│   ├── experiment_log.txt     # 30 MC runs raw output
│   └── scientific_report.txt  # Statistical summary (95% CI, ANOVA)
├── .github/workflows/ci.yml   # GitHub Actions CI (pytest + simulations)
├── requirements.txt
├── LICENSE (MIT)
└── README.md
```

---

## Key Parameters (Paper Table 3)

| Parameter | Value | Justification |
|-----------|-------|---------------|
| α | 0.6 | Spearman ρ=0.87 with network lifetime |
| β | 0.4 | Spearman ρ=0.61 with per-round energy cost |
| γ₀ | 0.3 | Base trust weight (sigmoid-adaptive) |
| δ | 0.01 | Collision rate < 0.3% (sweep) |
| σ₀ | 0.15 | Trust dispersion activation threshold |
| θ_trust | 0.4 | Isolation threshold |
| δ_neg | 0.15 | Multiplicative penalty → isolation in ~5 rounds |

---

## Quick Start

```bash
pip install -r requirements.txt
python -m pytest tests/ -v          # 150 unit tests → 100% pass
python simulations/collusion_experiment.py   # Quorum results
python simulations/latency_e2e.py            # E2E latency P95
```

📖 **For detailed usage instructions, see [USAGE.md](USAGE.md)**

---

## Key Results (Paper)

| Metric | Value |
|--------|-------|
| Network lifetime vs DCOPA | 90.2% |
| Energy overhead vs competitors | −22% |
| Attack detection rate (overall) | +40 percentage points vs SecLEACH |
| Collusion detection (base) | ~47% |
| Collusion detection (quorum m=3) | **89.4%** |
| FPR | 0.82% ± 0.31% |
| Throughput | 40.58 Mbps |
| PDR | 99.3–100% |
| E2E latency P95 (500 nodes) | ≤ 120 ms |
| E_alert (ECDSA sign + TX) | 5.6 µJ (~0.9% budget) |

---

## Security Properties

- **ECDSA** (secp256r1, SHA-256) for authentication — FIPS 180-4 compliant
- **ECDH** ephemeral keys for forward secrecy
- **ChaCha20-Poly1305** for authenticated encryption
- **Anti-replay**: nonce window per sender
- **Trust**: DLT-TBSEER on Tangle (no Proof-of-Work, no mining)
- **Quorum isolation**: m=3 independent observers required

---

## Citation

```bibtex
@article{seciiotdcopa2026,
  title   = {Secure-IIoT-DCOPA: Tangle-Based Immutable Trust for 
             Resilient Clustering in Critical IIoT},
  author  = {Souadih, Kamal and Mir, Foudil and Meziane, Farid},
  journal = {Journal of Information Security and Applications},
  year    = {2026},
  doi     = {10.5281/zenodo.10850224}
}
```

---

*This reproducibility package is released for peer review transparency.
The full GUI-based emulation platform is available upon request.*
