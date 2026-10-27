# Environment

## Analysis path (all reported statistics)

| item | value |
|---|---|
| interpreter | CPython 3.14.7 |
| third-party packages | **none** — `stats_paired.py`, `recompute_v5.py`, `assemble_v6.py`, `test_stats_paired.py` and `make_manifest.py` import only the standard library |
| minimum interpreter | 3.10 (`statistics.NormalDist` exists from 3.8; nothing else is version-sensitive) |
| runtime | `recompute_v5.py` takes under one second on one core |
| memory | < 100 MB |

`requirements-analysis.txt` is intentionally comment-only: there is nothing to install to verify any
number in the paper.

### Numerical reproducibility

The statistics are deterministic given the raw records: no sampling is used for the reported p-values or
intervals (the interaction p is exact enumeration; the Monte Carlo run is only a cross-check, and the
bootstrap interval is seeded). Across Python versions and libm implementations, `math.sqrt`, `math.log`
and `NormalDist.inv_cdf` can differ in the last bits, so regenerated interval endpoints may differ from
the delivered ones by on the order of 1e-16. That is not corruption and changes no estimate, verdict or
conclusion: compare with a tolerance, e.g. 1e-9, not by byte equality. Byte equality applies to the
delivered files, which is what `make_manifest.py verify` checks.

## Model path (only needed to regenerate the raw JSONL)

| item | value |
|---|---|
| hardware | 2 vCPU (Neoverse-N1, aarch64), 11.9 GB RAM, no GPU |
| precision | float32 on CPU throughout |
| libraries | see `requirements-model.txt` |
| checkpoints | `Qwen/Qwen2.5-1.5B-Instruct` @ `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`; `Qwen/Qwen2.5-0.5B-Instruct` @ `7ae557604adf67be50417f59c2c2f167def9a775` |

On this host the 1.5B bf16 checkpoint had to be converted to fp32 on disk first; loading a bf16
checkpoint with `dtype=float32` doubles peak allocation and swaps.

## Reference implementation used to validate the interval routine

`statsmodels` 0.15.0 was installed to inspect and cross-check
`statsmodels.stats.proportion.confint_proportions_paired`. That function is **not** in 0.15.0 (it is on
the main branch), so the routine was reproduced from the reference source and pinned by tests.
statsmodels is **not imported at runtime** and is not required to reproduce any result.
