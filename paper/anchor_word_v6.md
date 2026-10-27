# Changing One Word: a paired test of anchor direction in list indexing

**v6 — statistical correction.** Supersedes v5 (`history/v5_paper/`). The v5 intervals were computed
with a mis-specified Newcombe routine: the phi coefficient omitted Newcombe's n/2 correction and the
routine did not handle zero marginals. Every interval, verdict and derived sentence here is regenerated
by `code/recompute_v5.py` and `code/assemble_v6.py` from the same raw records. §7 is the correction log.
Host: 2 vCPU (Neoverse-N1), 11.9 GB RAM, no GPU; all models run in float32 on CPU.

---

## Abstract

For a list of odd length, the middle item can be addressed by two questions that name the same ordinal
and differ only in the anchor word:

> What item is at the **5th** position from the **beginning**?
> What item is at the **5th** position from the **end**?

Same list, same target, same ordinal. Any difference between them is a direction effect with ordinal
magnitude held fixed. This is the one place in the task family where direction can be isolated on a
single list.

On Qwen2.5-1.5B-Instruct with 9-item lists, the backward wording scores 17% against 50% for the
forward wording: the backward wording **reduces accuracy by 33.3 percentage points** (paired
difference -33.3 pp, 95% CI [-51.2,-11.6], exact McNemar p = 0.00781). Free generation on the same lists gives
an identical table (-33.3 pp (95% CI [-51.2,-11.6], p = 0.00781)); a second, independent set of lists gives -37.5 pp (95% CI [-55.2,-14.8], p = 0.00391). The reduction is
established by the interval in all three cells.

It does **not** clear the pre-specified practical margin of 15 points: the upper ends of those intervals
are −11.6, −11.6 and −14.8 points, so the data support "backward wording reduces accuracy" but not
"the reduction exceeds 15 points". We keep those two claims separate throughout.

The result is also **sensitive to the question template, and that is tested directly rather than
inferred**. Both wording cells ran on the same 24 lists, so each item contributes both effects: the
baseline effect is -37.50 pp, the word-ordinal effect +16.67 pp, and their interaction is -54.17 pp
(95% CI [-79.17,-33.33], exact permutation p = 0.00048828). The two prompts differ in several respects at once, so
this is an anchor × question-template interaction, not a digit-versus-word effect; it is exploratory. At L=11 the contrast is -4.2 pp (95% CI [-24.5,+16.3], p = 1.00000): no reduction detected at this sample size,
and the interval still admits a penalty of about 20 points, so we did not establish generalisation to
that length.

We claim one thing: in this model, with this wording, changing the anchor word alone reduces accuracy
by 33–38 points, and that reduction depends on the question template used to phrase the ordinal. We do **not** claim a
general direction effect, a mixture of two mechanisms, or anything about frontier models.

---

## 1. Why this contrast

Indexing a list from the end requires an offset the model must compute rather than read. The prior
study we started from (arXiv 2605.07127) reports that models fail such queries and attributes the
failure to positional encoding, leaving the mechanism untested. A forward/backward aggregate cannot
separate *where the item is* from *which way it is counted*, because the two directions visit different
positions at the same offset.

The midpoint removes that confound. At odd L, "5th from the beginning" and "5th from the end" address
the same item at the same ordinal, so the only difference between the two prompts is the anchor word.
The design is deliberately narrow: it buys internal validity at the cost of covering one position.

---

## 2. Method

### 2.1 The midpoint contrast

For odd L, i = (L+1)/2. Two prompts, same list, same target, same ordinal:

```
Items: L, O, J, M, R, P, N, K, Q
Question: What item is at the 5th position from the beginning?   →  R
Items: L, O, J, M, R, P, N, K, Q
Question: What item is at the 5th position from the end?         →  R
```

Scoring is a single forward pass that reads next-token logits for **the L letters appearing in that
list**, not all eleven pool letters: `midpoint.py` builds the candidate set as `{c for c in items}`.
The uniform-choice baseline is therefore 1/L — 14.3% at L=7, 11.1% at L=9 — and not 1/11.

This differs from the earlier v2 protocol (`score_positions.py`), which scored all eleven letters J–T
and logged candidate mass (min 0.996, median 1.000, n = 480). Those mass figures belong to v2; the midpoint harness does not
store mass per row, so it is not asserted for these records. In both protocols the candidate is a bare
letter id: an earlier version summed three token variants per letter and scored a leading-space form
that carried no mass. Validation against greedy generation is reported in §3.2.

### 2.2 Decision rule, and when it was fixed

Two different things are involved and they have different histories.

**The practical margin (±15 pp) and the 24-item cells** were fixed before the midpoint runs, in the v4
design. That part is prespecified.

**The interval method is not prespecified.** v1–v4 used 90% percentile-bootstrap intervals. The 95%
Newcombe interval was adopted in v5 and its implementation corrected in v6, after the data existed.
The correction changed the verdicts (§7), so the current labelling rules must be read as post hoc.
No dated protocol registered a 95% criterion or the interaction analysis in advance.

Current labels, applied to the corrected intervals:

| label | condition |
|---|---|
| reduction established | 95% interval entirely below 0 |
| reduction, margin cleared | 95% interval entirely below −15 pp |
| reduction, margin not cleared | interval below 0 but its upper end is above −15 pp |
| no reduction detected | interval contains 0 |
| no headroom | forward accuracy below 15%; not used as evidence either way |

"Reduction established" and "margin cleared" are separate rows on purpose. The first is a claim about
sign, the second about size, and this data supports the first without the second.

### 2.3 Replication grid

Cells of 24 items each, paired by item:

| factor varied | levels |
|---|---|
| list set | seed 71 (the original), seed 101 (fresh) |
| measurement | forced choice, free generation |
| length | L = 7, 9, 11 |
| wording | baseline, word ordinal, counting |
| model | Qwen2.5-1.5B-Instruct, Qwen2.5-0.5B-Instruct |

**Item pool.** `task.py::make_items` shuffles `LETTERS[:L]`, so each length draws from a different
pool: L=7 uses J–P, L=9 uses J–R, L=11 uses J–T. Changing L therefore changes both the number of items
and the letters they are drawn from. The within-list midpoint contrasts are unaffected — both prompts
see the same list, the same target and the same candidates — but cross-length comparisons do not
isolate length alone and are reported as descriptive.

The grid is small, uncorrected for multiplicity, and was extended cell by cell as results came in.
It is a set of probes, not a confirmatory design.

---

## 3. Results

### 3.1 The grid

| model | L | seed | wording | mode | table (bwd×fwd) | fwd % | bwd % | Δ pp | 95% CI | exact p | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen05 | 7 | 101 | baseline | forced | [[0,2],[0,22]] | 0 | 8 | +8.3 | [-6.7,+25.8] | 0.50000 | no headroom |
| qwen05 | 9 | 101 | baseline | forced | [[0,3],[0,21]] | 0 | 12 | +12.5 | [-3.5,+31.0] | 0.25000 | no headroom |
| qwen15 | 7 | 101 | baseline | forced | [[2,0],[6,16]] | 33 | 8 | -25.0 | [-44.3,-5.0] | 0.03125 | reduction, margin not cleared |
| qwen15 | 9 | 71 | baseline | forced | [[4,0],[8,12]] | 50 | 17 | -33.3 | [-51.2,-11.6] | 0.00781 | reduction, margin not cleared |
| qwen15 | 9 | 71 | baseline | generate | [[4,0],[8,12]] | 50 | 17 | -33.3 | [-51.2,-11.6] | 0.00781 | reduction, margin not cleared |
| qwen15 | 9 | 101 | baseline | forced | [[4,0],[9,11]] | 54 | 17 | -37.5 | [-55.2,-14.8] | 0.00391 | reduction, margin not cleared |
| qwen15 | 9 | 101 | counting | forced | [[0,3],[3,18]] | 12 | 12 | +0.0 | [-21.3,+21.3] | 1.00000 | no headroom |
| qwen15 | 9 | 101 | word_ordinal | forced | [[3,6],[2,13]] | 21 | 38 | +16.7 | [-7.2,+38.2] | 0.28906 | no reduction detected |
| qwen15 | 11 | 101 | baseline | forced | [[2,2],[3,17]] | 21 | 17 | -4.2 | [-24.5,+16.3] | 1.00000 | no reduction detected |

*Rows are backward correct/incorrect by forward correct/incorrect. Intervals are Newcombe method 10
with Newcombe's n/2 covariance correction, computed from the counts shown. A row such as L=7
(−25.0 pp, CI [−44.3,−5.0]) establishes a reduction but not a reduction larger than 15 points; the
two are different claims and the verdict column keeps them apart.*

### 3.2 Does the midpoint result survive generation?

The original lists (seed 71), scored by greedy generation, produce the **same 2×2 table** as forced
choice ([[4,0],[8,12]]) and therefore the same interval, [-51.2,-11.6], and the same exact p = 0.00781.
Two measurement modes give identical item-level outcomes here, so the result is not an artefact of
reading the next-token distribution.

### 3.3 What replicates, and how strongly

Four cells show a reduction whose interval excludes zero: the original lists by forced choice
(-33.3 pp), the original lists by generation (identical table), the fresh lists (-37.5 pp (95% CI [-55.2,-14.8], p = 0.00391)), and L=7
(-25.0 pp (95% CI [-44.3,-5.0], p = 0.03125)). Their exact p-values are 0.00781, 0.00781, 0.00391 and 0.03125.

None of the four clears the 15-point margin: their upper ends are −11.6, −11.6, −14.8 and −5.0 points.
So the correct summary is *the backward wording reduces accuracy, by an amount this study cannot bound
below 15 points* — not *the backward wording costs at least 15 points*.

Three cells show no reduction detected: L=11 (-4.2 pp (95% CI [-24.5,+16.3], p = 1.00000)), the word-ordinal paraphrase (+16.7 pp (95% CI [-7.2,+38.2], p = 0.28906)), and the
counting paraphrase, whose forward arm is at 12% and is therefore labelled no headroom rather than
counted as evidence of equivalence.

### 3.4 The anchor × question-template interaction, tested on identical lists

| quantity | estimate | 95% CI | p |
|---|---|---|---|
| effect of the anchor word, baseline wording | -37.50 pp | — | — |
| effect of the anchor word, word-ordinal wording | +16.67 pp | — | — |
| interaction (difference of the two effects) | -54.17 pp | [-79.17,-33.33] | 0.00048828 (exact, 2/4096) |

The paraphrase is not a minimal pair: it changes "What" to "Which" and drops "at the … position" while
turning the digit into a word. The contrast therefore measures an **anchor × question-template**
interaction and cannot be attributed to digit-versus-word ordinal alone; that would need a pair
differing in the numeral only. This analysis is exploratory — it was specified after the baseline cells
existed.

Each item's interaction term is defined explicitly as

```
(bwd_baseline − fwd_baseline) − (bwd_paraphrase − fwd_paraphrase)
```

with all four indicators read from the same list. The mean over 24 items is −54.17 points, matching
the difference of the two separately estimated effects (−37.50 − 16.67). Per-item terms are exported in
`results/interaction_audit.json` and the raw indicators in `results/per_item_indicators.csv`.

**Inference.** Percentile bootstrap over items: 10,000 resamples, `random.Random(0)`, resampling item
records with replacement.

The permutation test is exact, not Monte Carlo. Under the null the two wording conditions are
exchangeable within an item, so each item's effect pair may be swapped; swapping a zero term changes
nothing, so only the 12 nonzero terms matter (eleven of −1, one of −2). That is 2¹² = 4,096 sign
assignments, and all are enumerated. Exactly two are at least as extreme as the observed statistic,
giving **p = 2/4096 = 0.00048828125**.

A Monte Carlo run is retained only as a cross-check: 100,000 permutations, seed 0, 47 exceedances,
plus-one p = 0.00048. It agrees with the exact value and is not the reported p.

This is the direct form of the comparison. Comparing two separate significance tests would conflate
the size of the two effects with their precision; the interaction compares them on the same items,
where the shared list-to-list variance cancels.

### 3.5 The second model

At L=9 the 0.5B model's forward accuracy at the midpoint is 0%; its difference is +12.5 pp (95% CI [-3.5,+31.0], p = 0.25000). The
interval includes zero. A forward arm at the floor means a *further* penalty could not be observed,
which does not make the observed *positive* estimate real; the cell is uninformative about direction
in both directions and is labelled no headroom.

### 3.6 Positional context (no claim about the published aggregate)

| target position (L=10) | forward % | backward % | Δ pp | 95% CI | exact p |
|---|---|---|---|---|---|
| 1 | 100 | 0 | -100.0 | [-100.0,-80.5] | 0.0000 |
| 2 | 92 | 0 | -91.7 | [-97.7,-69.4] | 0.0000 |
| 3 | 4 | 0 | -4.2 | [-20.2,+10.1] | 1.0000 |
| 4 | 46 | 4 | -41.7 | [-61.0,-17.8] | 0.0020 |
| 5 | 29 | 8 | -20.8 | [-39.9,-1.9] | 0.0625 |
| 6 | 12 | 8 | -4.2 | [-20.0,+10.3] | 1.0000 |
| 7 | 17 | 25 | +8.3 | [-10.2,+26.8] | 0.6250 |
| 8 | 8 | 29 | +20.8 | [-1.7,+41.7] | 0.1250 |
| 9 | 21 | 8 | -12.5 | [-30.6,+4.2] | 0.2500 |
| 10 | 33 | 25 | -8.3 | [-28.5,+12.8] | 0.6875 |

For context only: the forward label alone varies sharply with position (100, 100, 5, 50, 40, 35, 0, 15, 0, 35 for positions 1-10). We do **not**
infer anything about the published forward/backward aggregate. The original study evaluates all valid
offsets; when positions are weighted equally, both directions cover the same positions, so a position
effect does not by itself make its aggregate an artefact. Our midpoint result stands on its own.

### 3.7 Interventions (secondary, exploratory)

| frame | k | n | plain % | stamped % | Δ pp |
|---|---|---|---|---|---|
| fwd | 1 | 20 | 100 | 100 | +0 |
| fwd | 2 | 20 | 100 | 100 | +0 |
| fwd | 3 | 20 | 0 | 5 | +5 |
| fwd | 4 | 20 | 40 | 100 | +60 |
| bwd | 1 | 20 | 40 | 45 | +5 |
| bwd | 2 | 20 | 5 | 0 | -5 |
| bwd | 3 | 20 | 15 | 0 | -15 |
| bwd | 4 | 20 | 0 | 0 | +0 |

Index stamping — writing the resolved index into the prompt — was tried as a probe, not as a test of a
stated hypothesis. Its numbers are reported because they were run, and no claim rests on them.

---

## 4. What this does and does not show

**Supported.** In Qwen2.5-1.5B-Instruct at L=9, holding the list, the target and the ordinal fixed,
the backward anchor reduces accuracy by 33–38 points (two list sets, two measurement modes). The size
of that reduction depends on the question template: the anchor × template interaction against the
word-ordinal form is −54.17 points (exact p = 0.000488), estimated within item. That interaction is
exploratory and is not evidence about digit-versus-word ordinals, because the paraphrase changes more
than the numeral.

**Not supported.** That the reduction exceeds 15 points (no interval clears the margin). That the
effect generalises to L=11, to other models, or to frontier models. That it has a particular mechanism.
That the published aggregate is a positional artefact.

**Exploratory.** The L=7 cell, the counting paraphrase, the 0.5B cells, the positional scan and the
stamping probe. They are reported for completeness and none is used to support the central claim.

---

## 5. Limitations

One model family, three list lengths, 24 items per cell, one position (the midpoint), one tokenizer,
CPU float32. Length is confounded with item pool — L=7 draws from J–P, L=9 from J–R, L=11 from J–T — so
the cross-length rows describe three different pools as well as three lengths. The grid is uncorrected for multiplicity; with nine cells, one p-value near 0.03 would not
survive a Bonferroni-style adjustment, which is another reason the L=7 row is labelled exploratory. The
interval method was chosen after seeing the data, and the correction in v6 changed verdicts — both facts
argue for treating the labels as descriptive rather than confirmatory. Everything here is a small-model
probe; nothing follows about larger models without running them.

---

## 6. Reproducibility

**Models.** `Qwen/Qwen2.5-1.5B-Instruct`, snapshot `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`, float32.
On this host the bf16 checkpoint must be converted to fp32 on disk first (loading bf16 with
`dtype=float32` doubles peak allocation and swaps); the converted copy is `/root/models/qwen15-fp32`.
`Qwen/Qwen2.5-0.5B-Instruct`, snapshot `7ae557604adf67be50417f59c2c2f167def9a775`, float32. Tokenizers
are the snapshots' own.

**Decoding.** Greedy in both modes. Forced choice reads next-token logits at the final prompt position
in a single forward pass; generation uses `max_new_tokens=6` and parses the first letter in A–T.

**Candidates.** The midpoint harness scores the L letters present in the list — for L=9, nine of
J–T — as bare token ids (41–51), each asserted single-token with `decode(id) == letter`. Uniform-choice
baseline 1/L. The v2 scoring protocol is different: it scored all eleven letters J–T, and its
candidate-mass log (min 0.996, median 1.000, n = 480) applies to v2 only. Leading-space variants (`' J'`, id 619) are different
continuations and are excluded in both.

**Exact prompts.** `code/midpoint.py::build`, L=9, i=5:

```
Items: L, O, J, M, R, P, N, K, Q
Question: What item is at the 5th position from the beginning?
Answer with the letter only.
Answer:
```

with `from the end` for the backward arm, and the paraphrases
`Which item is fifth from the beginning?` and `Counting from the beginning, which item is number 5?`.
System message: `You answer with a single letter.`; prompts are wrapped in the tokenizer's chat template.

**Statistics.** Paired binary contrasts use Newcombe's method 10 as implemented in
`code/stats_paired.py`, which reproduces `statsmodels.stats.proportion.confint_proportions_paired`
(main branch) to 1e-9 on the reference table `[[10,5],[2,20]]` → [−0.0643926050711, 0.2211160178958],
and reproduces the three tables in the correction request. Normal quantiles come from
`statistics.NormalDist`, not a hand-rolled approximation; 90%, 95% and 99% intervals are tested against
reference values and checked for nesting. Regression tests:
`code/test_stats_paired.py` (reference case, the three empirical tables, transpose symmetry,
concordant and boundary tables, McNemar values, margin classification). Exact McNemar p-values are
computed separately by `stats_paired.mcnemar_exact` and are unaffected by the interval correction.
The interaction uses an item-level bootstrap and a within-item permutation test, as described in §3.4;
it is a different procedure from the paired intervals and is not described as Newcombe.

**Versions.** Python 3.14.7; torch 2.14 (CPU); transformers 5.16; statsmodels 0.15.0 (reference only,
not used at runtime); numpy/scipy as installed by statsmodels.

**Data and code.** `/root/poscurse`: `raw/midpoint.jsonl`, `raw/paired_scan.jsonl`,
`raw/positional_scan.jsonl`; `code/`; `results/v5_corrected.json`, `results/interaction_audit.json`,
`results/per_item_indicators.csv`; `AUDIT.md`; `history/` for superseded versions. A shareable archive
with the same contents is `dist/anchor_word_v6_package.zip`.

`SHA256SUMS` covers every delivered file except itself. Verifying it checks the **delivered** artifacts,
not a reanalysis: regenerating results can rewrite those files. Re-running the analysis on a different
Python or libm may move interval endpoints in the last bits (on the order of 1e-16) without changing any
estimate, verdict or conclusion, so regenerated numbers should be compared with a numerical tolerance
(for example 1e-9) rather than by byte equality.

---

## 7. Correction log (v5 → v6)

| item | v5 | v6 | effect |
|---|---|---|---|
| phi coefficient | `(ad−bc)/√((a+b)(c+d)(a+c)(b+d))` | Newcombe's n/2 adjustment: positive covariance reduced by n/2, floored at 0 | intervals widen |
| zero marginals | divided by zero → 0 by accident of the guard | phi explicitly 0 when any marginal total is 0 | correct boundary case |
| original midpoint | −33 pp [−50,−17] | −33.3 [−51.2,−11.6] | verdict: margin no longer cleared |
| fresh midpoint | −38 pp [−54,−21] | −37.5 [−55.2,−14.8] | verdict: margin no longer cleared |
| L=7 | −25 [−38,−12], "unresolved" | −25.0 [−44.3,−5.0], reduction established | verdict upgraded from unresolved to reduction |
| word-ordinal | +17 [−4,+33] | +16.7 [−7.2,+38.2] | interval now contains 0: no reduction detected |
| L=11 | −4 [−21,+12] | −4.2 [−24.5,+16.3] | unchanged verdict, wider interval |
| 0.5B | +12 [−6,+29] | +12.5 [−3.5,+31.0] | consistent with p = 0.25 |
| McNemar p | 0.008 / 0.004 | 0.00781 / 0.00391 | unchanged: 8 and 9 discordant pairs |
| interaction | −54.2, p = 0.0004, Monte Carlo without plus-one | −54.17, p = 2/4096 = 0.00048828125, exact enumeration; Monte Carlo kept as a cross-check | same conclusion, exact p |
| "costs about a third" | abstract | "reduces accuracy by 33–38 percentage points" | matches the estimates |
| interval description | "Newcombe throughout" | paired contrasts Newcombe; interaction bootstrap + exact permutation | accurate |

Corrections made while finalising v6, after the reference implementation was reproduced:

| item | was | now | effect |
|---|---|---|---|
| candidate set | "eleven letters J–T" for all scoring | midpoint scores the L letters in the list (`{c for c in items}`); v2 scored 11 | uniform baseline 1/L, not 1/11, for the midpoint cells |
| item pool | unstated | `LETTERS[:L]` → J–P / J–R / J–T | length is confounded with pool; cross-length rows descriptive only |
| interaction naming | "wording interaction", "word-ordinal" | anchor × question-template interaction | no digit-versus-word claim without a minimal pair |
| interaction p | Monte Carlo, plus-one | exact 2/4096 = 0.00048828125 | MC retained only as cross-check (47 exceedances) |
| non-default alpha | hand-rolled inverse normal returned −2.5758 for α=0.01 | `statistics.NormalDist` | 90% and 99% intervals now correct and tested |
| test runner | printed verdict only | exits nonzero on failure | CI-usable |

---

## 8. Artifacts

| path | contents |
|---|---|
| `paper/anchor_word_v6.pdf` | this paper |
| `paper/paper_v6_final.md` | assembled source |
| `paper/paper_v6.md` | template before number substitution |
| `code/stats_paired.py` | Newcombe method 10, exact McNemar, `NormalDist` quantiles |
| `code/test_stats_paired.py` | regression tests, nonzero exit on failure |
| `code/recompute_v5.py` | raw JSONL → corrected aggregates, per-item CSV, exact permutation |
| `code/assemble_v6.py` | aggregates → `paper_v6_final.md` |
| `code/midpoint.py`, `code/task.py` | experiment harness |
| `raw/midpoint.jsonl`, `raw/paired_scan.jsonl`, `raw/positional_scan.jsonl` | item-level records |
| `raw/v2_score_qwen15.jsonl`, `raw/v2_stamped.jsonl` | v2 protocol records (11-letter candidates, mass log) |
| `results/v5_corrected.json` | every cell: 2×2 table, proportions, interval, p, verdict |
| `results/interaction_audit.json` | per-item terms, exact and Monte Carlo permutation detail |
| `results/per_item_indicators.csv` | four correctness flags per item per condition |
| `CORRECTION_LOG.md` | standalone correction log |
| `AUDIT.md` | harness audit |

`SHA256SUMS` in the distributed package covers every file except itself, including
`code/make_manifest.py`; it is generated after all files are final, and `make_manifest.py verify` fails
on a mismatch or on any file present but unlisted.
