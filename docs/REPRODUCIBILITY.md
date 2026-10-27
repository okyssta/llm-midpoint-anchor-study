# Reproducibility

Two paths, with separate dependencies: **analysis from saved predictions** (no model, no GPU, no
third-party packages) and **inference** (downloads weights, needs ~6.2 GB for the 1.5B model in
float32).

## Recorded environment

| item | value |
|---|---|
| interpreter | CPython 3.14.7 (recorded host) |
| analysis dependencies | none — standard library only (`statistics.NormalDist`, `hashlib`, `json`) |
| minimum interpreter | 3.10 |
| inference dependencies | `torch==2.14.1`, `transformers==5.16.1`, `numpy==2.5.4` |
| hardware | 2 vCPU (Neoverse-N1, aarch64), 11.9 GB RAM, no GPU |
| precision | float32 on CPU |
| checkpoints | `Qwen/Qwen2.5-1.5B-Instruct` @ `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`; `Qwen/Qwen2.5-0.5B-Instruct` @ `7ae557604adf67be50417f59c2c2f167def9a775` |

The recorded host needed the 1.5B bf16 checkpoint converted to fp32 on disk first; loading a bf16
checkpoint with `dtype=float32` doubles peak allocation and swaps. Any host with enough RAM can load
the checkpoint directly in float32.

## Path conventions

Every script resolves paths from its own location (`HERE`/`ROOT`), not from the working directory, so
the commands below work from a fresh clone. Two exceptions are deliberate and documented:

- `midpoint.py --out` defaults to `<repo>/raw/midpoint.jsonl`; a relative `--out` is resolved against
  the working directory. The model default is the public `Qwen/Qwen2.5-1.5B-Instruct` (the recorded
  host used a local fp32 copy at `/root/models/qwen15-fp32`, passed explicitly).
- PDF generation is manual: the renderers emit HTML, which is printed to A4 by a headless browser with
  the embedded CSS.

## Analysis path (verified during repository preparation)

```bash
python3 code/test_stats_paired.py     # 26 checks
python3 code/check_analysis.py        # end-to-end recomputation, tolerance 1e-9
python3 code/make_manifest.py verify  # repository checksums
```

`check_analysis.py` copies the tree to a temporary directory, runs `recompute_v5.py` and
`assemble_v6.py` there, and compares the regenerated `results/*.json` and `paper/anchor_word_v6.md`
against the committed copies. Floats use an absolute tolerance of 1e-9; integer counts, tables and
strings must match exactly; the interaction's exact p is checked against 2/4096.

Observed on 2026-10-27 during preparation: worst deviation `0.000e+00`, assembled paper byte-identical.
The `1e-9` tolerance exists for other interpreters and libm versions, where the last bits can move by
~1e-16 without changing any result. A difference at that scale is floating point, not corruption; do
not "fix" committed results to match a locally regenerated file.

## Inference path (not run during repository preparation)

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-model.txt
python3 code/midpoint.py \
    --model Qwen/Qwen2.5-1.5B-Instruct --tag qwen15-repro \
    --L 9 --seed 101 --para baseline --mode forced --items 24 \
    --out raw/rerun_L9_s101_forced.jsonl
```

`--model` is passed unchanged to `AutoModelForCausalLM.from_pretrained`. `--tag` is only the label
written into each row. The harness appends to `--out`; write to a new file and compare with the
committed records rather than overwriting them.

To rebuild `results/` from a complete set of records, `recompute_v5.py` reads `raw/midpoint.jsonl` and
`raw/paired_scan.jsonl` and rewrites `results/`. That is the only script that writes into `results/`.

## Documents

```bash
python3 code/assemble_v6.py      # results + template -> paper/anchor_word_v6.md
python3 code/render_v6.py        # -> paper/paper.html
python3 code/render_audit.py     # -> paper/novelty_audit.html
```

The committed PDFs were produced from those HTML files by `Page.printToPDF` (A4, print background,
no margins). Regenerating the PDFs is not required to verify any number.

## Known internal references

The paper's §6 predates this repository and names paths from the original host (`/root/poscurse`,
`/root/models/qwen15-fp32`, `dist/anchor_word_v6_package.zip`). Those are historical; the same files
live in this repository at `code/`, `raw/`, `results/` and `paper/`. The paper text is kept verbatim so
the committed source and the committed PDF stay identical. Superseded drafts (`v1`–`v5`) are not
included; `docs/CORRECTION_LOG.md` records what changed between them.
