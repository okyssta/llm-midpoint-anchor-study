# Changing One Word

**A paired midpoint analysis of anchor direction in list indexing**, with a measured interaction
between two question templates. Small, exploratory, CPU-only, one model family.

- Paper: [`paper/anchor_word_v6.pdf`](paper/anchor_word_v6.pdf) (9 pages) · source
  [`paper/anchor_word_v6.md`](paper/anchor_word_v6.md)
- Novelty audit: [`paper/novelty_audit.pdf`](paper/novelty_audit.pdf) (3 pages) · source
  [`paper/novelty_audit.md`](paper/novelty_audit.md)

This repository accompanies an unpublished manuscript. It has not been peer reviewed, and no priority
claim is made.

---

## Research question

For an odd-length list, the middle item can be requested two ways that name the same item at the same
ordinal:

> What item is at the 5th position from the **beginning**?
> What item is at the 5th position from the **end**?

At the midpoint these differ only in the anchor word. That isolates anchor direction from the confound
in an ordinary forward/backward comparison, where the two directions necessarily visit different
positions for the same ordinal and the same position at different ordinals.

**Contribution (restrained).** A same-list, same-item, same-ordinal paired estimate of the anchor
effect in one small model, and evidence that the estimated effect differs between the two question
templates tested. The direction asymmetry itself, and prompt sensitivity in general, are prior results
(see [Relationship to prior work](#relationship-to-prior-work)).

---

## Main results

Two different quantities are reported, and they should not be conflated.

### (a) The accuracy gap at the midpoint

Backward minus forward accuracy, paired by item. Negative means the backward wording is worse.
Intervals are Newcombe's method 10 for paired proportions; tests are exact McNemar.

| cell | 2×2 (bwd × fwd) | Δ (pp) | 95% CI | exact p |
|---|---|---|---|---|
| original lists, forced choice (seed 71) | `[[4,0],[8,12]]` | −33.3 | [−51.2, −11.6] | 0.00781 |
| original lists, free generation (seed 71) | `[[4,0],[8,12]]` | −33.3 | [−51.2, −11.6] | 0.00781 |
| fresh lists, forced choice (seed 101) | `[[4,0],[9,11]]` | −37.5 | [−55.2, −14.8] | 0.00391 |
| L=7, forced choice | `[[2,0],[6,16]]` | −25.0 | [−44.3, −5.0] | 0.03125 |
| L=11, forced choice | `[[2,2],[3,17]]` | −4.2 | [−24.5, +16.3] | 1.00000 |
| word-ordinal paraphrase | `[[3,6],[2,13]]` | +16.7 | [−7.2, +38.2] | 0.28906 |
| counting paraphrase | `[[0,3],[3,18]]` | 0.0 | [−21.3, +21.3] | 1.00000 |
| Qwen2.5-0.5B, L=9 | `[[0,3],[0,21]]` | +12.5 | [−3.5, +31.0] | 0.25000 |
| Qwen2.5-0.5B, L=7 | `[[0,2],[0,22]]` | +8.3 | [−6.7, +25.8] | 0.50000 |

The reduction is 33–38 points in the baseline setting. **No interval lies entirely below the
pre-specified −15 pp practical margin**, so the supported claim is about sign — backward wording
reduces accuracy — not about size. Cells whose forward accuracy is below 15% are labelled "no
headroom" in the paper and are not evidence either way.

### (b) The difference between the two template effects

Both wording cells ran on the same 24 lists, so each item contributes both effects. The interaction is
the difference of those effects, estimated within item:

| quantity | estimate | 95% CI | p |
|---|---|---|---|
| anchor effect, baseline wording | −37.50 pp | — | — |
| anchor effect, word-ordinal wording | +16.67 pp | — | — |
| interaction (difference of the two) | **−54.17 pp** | [−79.17, −33.33] | 2/4096 = 0.00048828125 (exact) |

This is an **anchor × question-template** interaction, not a digit-versus-word ordinal effect: the
paraphrase also changes "What" to "Which" and drops "at the … position". It was specified after the
baseline cells existed, and is labelled exploratory.

---

## Design and scope

| item | value |
|---|---|
| models | `Qwen/Qwen2.5-1.5B-Instruct` (snapshot `989aa798…`), `Qwen/Qwen2.5-0.5B-Instruct` (snapshot `7ae55760…`) |
| precision / device | float32, CPU only (2 vCPU, no GPU) |
| conditions | midpoint of odd-length lists; L ∈ {7, 9, 11}; anchor × wording crossed |
| samples | 24 items per cell, paired by item; 9 cells; two list seeds (71, 101) |
| scoring | single forward pass over the L letters in the list (uniform baseline 1/L); greedy generation as a cross-check |
| item pool | `LETTERS[:L]`, so L=7 draws J–P, L=9 J–R, L=11 J–T |
| multiple comparisons | none applied |

Full method, prompts, candidate definition and statistics: paper §2 and §6.

---

## Limitations

- **Small exploratory study.** One position per list, 24 items per cell, nine cells, one tokenizer.
- **Limited models and templates.** One model family (0.5B, 1.5B); two question templates. The 0.5B
  cells sit at a 0% forward floor and carry no directional evidence.
- **Uncorrected comparisons.** Nine cells, no multiplicity correction; the L=7 row (p = 0.031) would
  not survive a Bonferroni-style adjustment.
- **Length is confounded with item pool.** `LETTERS[:L]` means each length draws different letters, so
  cross-length rows describe three pools as well as three lengths. Only within-list contrasts are used
  for claims.
- **No mechanism and no broad generalisation.** Attention, positional encoding and ordinal arithmetic
  are untested. The studied effect does not clear the practical margin, and no claim is made about
  frontier models.
- **Interval method chosen post hoc.** 90% bootstrap intervals were used in earlier versions; the 95%
  Newcombe method and the interaction analysis were introduced after the data existed. `docs/CORRECTION_LOG.md`
  records what changed and why.

---

## Relationship to prior work

- **Zhang et al., _The Position Curse_ (arXiv:2605.07127, 2026)** establish that backward positional
  retrieval lags forward retrieval across models, anchors, query types and item types (pp. 1–2, 5).
  Their protocol instantiates both midpoint queries at L=5, but the paper reports condition-level
  aggregates and does not report a paired midpoint analysis. We replicate the asymmetry and add the
  paired midpoint contrast; we do not claim the asymmetry.
- **Sclar et al., _Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design_
  (ICLR 2024, arXiv:2310.11324)** show prompt-formatting changes worth up to 76 accuracy points across
  53 classification and multiple-choice tasks (p. 1). Formatting of templates, not ordinal indexing.
- **Leidinger et al., _The language of prompting_ (Findings of EMNLP 2023)** show semantically
  equivalent grammatical and lexical variation changing accuracy by up to 5 points on QA and NLI
  (p. 5). Again not positional retrieval.
- **Liu et al., _Lost in the Middle_ (arXiv:2307.03172)** report a U-shaped effect of where evidence
  sits in a long context — a different axis (position of evidence, not anchor direction).
- **Berglund et al., _The Reversal Curse_ (arXiv:2309.12288)** report direction asymmetry in learned
  factual relations, not in-context ordinal indexing.

Citations are unverified against publisher metadata beyond the arXiv/ACL identifiers above; see the
audit's search-limitations section (`paper/novelty_audit.md` §4).

---

## Repository layout

```
README.md                  this file
CITATION.cff               citation metadata (no DOI, no venue)
requirements-analysis.txt  analysis path (standard library only)
requirements-model.txt     inference pins
paper/
  anchor_word_v6.pdf       paper (9 pp)
  anchor_word_v6.md        canonical paper source
  paper_v6_template.md     build template that anchor_word_v6.md is assembled from
  novelty_audit.pdf        novelty audit (3 pp)
  novelty_audit.md         audit source
code/
  stats_paired.py          Newcombe method 10, exact McNemar, NormalDist quantiles
  test_stats_paired.py     statistical regression tests (26 checks)
  recompute_v5.py          raw records -> results/
  assemble_v6.py           template + results -> paper/anchor_word_v6.md
  check_analysis.py        CI: recompute in a temp copy and compare at 1e-9
  midpoint.py              inference harness for one cell
  task.py                  list/query generation
  render_v6.py             paper markdown -> HTML (for PDF printing)
  render_audit.py          audit markdown -> HTML
  find.py                  page-level text search used while auditing literature
  make_manifest.py         build/verify SHA256SUMS
raw/                       item-level prediction records (5 JSONL files)
results/                   per-cell aggregates, interaction audit, per-item indicators
docs/
  ENVIRONMENT.md           recorded environment, model revisions
  REPRODUCIBILITY.md       commands, tolerances, what was and was not rerun
  AUDIT.md                 harness audit (defects found and fixed during the study)
  CORRECTION_LOG.md        v5 -> v6 corrections and finalisation changes
  NOVELTY_EVIDENCE.md      page-anchored quotes behind the audit
SHA256SUMS                 repository checksum manifest
.github/workflows/analysis.yml   CI: tests + analysis validation (no GPU, no weights)
```

---

## Reproduce

### 1. Statistics from the saved predictions (no model, no GPU, no dependencies)

Python 3.10+; the analysis path imports only the standard library.

```bash
git clone https://github.com/okyssta/llm-midpoint-anchor-study
cd llm-midpoint-anchor-study

python3 code/test_stats_paired.py    # 26 checks, exits nonzero on failure
python3 code/check_analysis.py       # recomputes every cell + interaction, compares at 1e-9
python3 code/make_manifest.py verify # 35 checksum entries
```

Expected: `ALL PASS`; `PASS — regenerated results match the committed records` with worst deviation
`0.000e+00`; `35 entries checked: OK`.

`check_analysis.py` copies the repository to a temporary directory and runs the pipeline there, so the
committed `results/` and `paper/` files are never modified.

### 2. Re-run inference (optional; downloads model weights)

This was **not** run during repository preparation. It needs the pins in `requirements-model.txt` and
enough disk for a 1.5B model in float32 (~6.2 GB).

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-model.txt

# one cell; writes to a new file so the committed records are untouched
python3 code/midpoint.py \
    --model Qwen/Qwen2.5-1.5B-Instruct --tag qwen15-repro \
    --L 9 --seed 101 --para baseline --mode forced --items 24 \
    --out raw/rerun_L9_s101_forced.jsonl
```

`--model` is passed unchanged to `from_pretrained`, so it must be a checkpoint identifier or a local
directory; the default is the public `Qwen/Qwen2.5-1.5B-Instruct`. `--tag` only labels rows. With no
`--out`, rows append to `raw/midpoint.jsonl` in this repository — pass `--out` to write elsewhere.

### 3. Rebuild the documents (optional)

```bash
python3 code/assemble_v6.py    # template + results -> paper/anchor_word_v6.md
python3 code/render_v6.py      # -> paper/paper.html
python3 code/render_audit.py   # -> paper/novelty_audit.html
```

PDF generation is a manual step: open the HTML in a headless Chromium and print to A4 with the
embedded CSS. It is not automated here and is not part of CI.

---

## Provenance: what was verified, and when

**Historical experiment runs.** All model inference reported in the paper ran on a single 2-vCPU CPU
host in October 2026 and is recorded in `raw/`. Model snapshots and precision are in
`docs/ENVIRONMENT.md`.

**Checks performed during repository preparation (2026-10-27).** No model inference was rerun.

1. The frozen release's checksums were verified before any file was reorganised.
2. `code/test_stats_paired.py`: 26 checks, all pass.
3. `code/check_analysis.py`: every cell and the interaction recomputed from `raw/` in a temporary copy;
   maximum absolute deviation 0.0 at tolerance 1e-9; assembled paper byte-identical to the committed
   source.
4. `code/make_manifest.py verify`: all repository checksums match.
5. Both PDFs open and were page-checked (9 pp, 3 pp).
6. Internal links and file references in this README and the docs were checked.

---

## Citation

`CITATION.cff` holds the title, version and date. It deliberately omits a surname, affiliation, DOI and
venue: none is known, and none is invented. Cite as:

> Kyssta. *Changing One Word: a paired test of anchor direction in list indexing.* Version 6, 2026.
> https://github.com/okyssta/llm-midpoint-anchor-study

## License

**No license has been assigned.** The originating study carried no license file, and none is added
here: adding one would silently relicense the paper, the code and the data. All rights are reserved by
default. If you need to reuse this material, contact the repository owner for terms.
