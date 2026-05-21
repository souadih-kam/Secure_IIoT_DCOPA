# Secure-IIoT-DCOPA — Reproducibility Package

[![CI]()
[![DOI]()

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
@article{SOUADIH2026104502,
title = {Secure-IIoT-DCOPA: Tangle-based immutable trust for resilient clustering in critical IIoT},
journal = {Journal of Information Security and Applications},
volume = {100},
pages = {104502},
year = {2026},
issn = {2214-2126},
doi = {https://doi.org/10.1016/j.jisa.2026.104502},
url = {https://www.sciencedirect.com/science/article/pii/S2214212626001328},
author = {Kamal Souadih and Foudil Mir},
keywords = {Industrial internet of things (IIoT), Security and resilience, Distributed trust management (DLT/Tangle), Energy efficiency, Wireless sensor networks},
abstract = {The Industrial Internet of Things (IIoT) increasingly exposes wireless sensor networks to complex security and reliability challenges in critical infrastructures. Traditional clustering protocols such as DCOPA achieve good energy efficiency but lack native mechanisms to ensure confidentiality, integrity, and resilience against coordinated threats. This paper presents Secure-IIoT-DCOPA, a security- and resilience-oriented architecture designed to protect IIoT environments without compromising network longevity. The proposed system integrates (1) a lightweight cryptographic engine combining ECC, ECDH, ECDSA, and ChaCha20-Poly1305 to ensure efficient data protection, and (2) DLT-TBSEER, a dynamic trust management framework based on a Tangle-inspired distributed ledger that enforces immutable reputations, proactive isolation of malicious nodes, and autonomous network reorganization for service continuity. Experimental validation was performed on a high-fidelity emulation platform with 300 nodes (20% malicious) over 1200 rounds using 30 Monte Carlo runs. Secure-IIoT-DCOPA achieved a packet delivery ratio (PDR) of 99.95% ± 0.05%, an average throughput of 254.55 ± 1.45 packets per round, and successfully isolated all malicious nodes (100%). Compared to reference protocols (SECDCOPA: 17.54%, SecLEACH: 30.22%, MSCR: 35.45%), our approach achieved a behavioral attack detection rate of 50.14%, compared to SecLEACH (13.33%), SECDCOPA (0.00%), and MSCR (0.00%), representing an absolute improvement of ∼+37 percentage points over SecLEACH and ∼+42% relative improvement over SECDCOPA (the primary comparison baseline; see Table 11 for per-protocol breakdown), and reduced relative energy cost by ∼−15% while maintaining maximal network lifetime. Through its integrated design, formal validation, and application-driven evaluation, Secure-IIoT-DCOPA demonstrates a robust and energy-aware framework capable of ensuring security, trust, and resilience in next-generation IIoT systems.}
}
```

---

*This reproducibility package is released for peer review transparency.
The full GUI-based emulation platform is available upon request.*



