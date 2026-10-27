# Audit of "Two Ways a Language Model Fails to Index a List"

Status: **complete** — verdicts below are final for this round. Every entry names the check that decided it, and whether the
criticism was confirmed, rejected, or partly right. Numbers are regenerated from `raw/v2_*`
after the harness fix unless stated otherwise.

## A. Harness defects (confirmed, fixed, re-run)

> **Historical note.** Sections A–F were written against v1 and are kept for the record. Several of
the verdicts in them were themselves overturned later (see G and H): the "surface-order" claim, the
"position explains direction" claim, and the 1/L baseline above. Read A–F as the state of the audit at
that time, not as current conclusions.

| # | criticism | verdict | evidence | action |
|---|---|---|---|---|
| A1 | Seed may change the list when `k` changes | **rejected** | `make_items(L, seed, item_id)` takes no `k`; 20 items × 4 offsets compared, 0 mismatches | regression assertion in `test_task.py` |
| A2 | Every cell is scored twice (duplicated prompts) | **confirmed** | only 4 distinct prompts among the 8 view-format cells; `plain/fwd == revframe/bwd` etc. | n now reported as unique items; CIs clustered by item |
| A3 | Candidate-token variants are summed across incompatible forms | **confirmed, twice** | each letter has three ids (`J`, ` J`, `\tJ`). v1 summed all three; the first "fix" scored only `" J"`, which returned `cand_mass = 0.000` — the model emits the **bare** letter after `assistant\n` | scorer uses the bare-letter id, asserts it is single-token, and records `cand_mass`; with the fix mass = 1.000 on all rows |
| A4 | Probability mass on valid candidates not recorded | **confirmed** | v1 normalised over candidates, so `p(gold)` was conditional by construction | `cand_mass` stored per row; audit script reports its distribution |
| A5 | Chance level wrong | **confirmed, then corrected again** | pool is 11 letters (J–T). Uniform guessing over candidates = 1/11 ≈ 9%. A constant responder is also right 1/11 of the time, **not** 1/L as this audit first stated: gold letters are uniform over the 11-letter pool, so a fixed letter matches with probability 1/11 whether the list has 6 or 10 items. `1/L` would only hold if the gold were uniform over the list positions and the predicted letter were guaranteed to be in the list | both figures corrected in the paper and here; the model never predicted a letter outside the list (0/448), which is why the two coincided numerically at L=10 and not in general |
| A6 | Semantic equivalence of paired cells | **rejected** (holds) | hand-checked: `plain/fwd` and `revlist/bwd` print different strings and both target the same item S; asserted for all formats in `test_task.py` | unchanged |
| A7 | Stale summaries / duplicate keys | **rejected** | 960 rows, 0 duplicate keys, 48 cells × 20 unique items | analysis reads one source |

## B. Statistical defects

| # | criticism | verdict | action |
|---|---|---|---|
| B1 | Bootstrap CIs degenerate at 0% / 100% | **confirmed** | Wilson intervals for absolute accuracy; cluster bootstrap by item for paired differences |
| B2 | Table 9 reports 32 rows as if 32 items | **confirmed** | 16 unique items × 2 formats; report 16, cluster the interval |
| B3 | Abstract pooling (98% vs 22%) | **to verify** | recomputed from v2 below |
| B4 | Table 3 MI exceeds its own null | **confirmed** | the "not using `k` at all" sentence is unsupported; replaced by the answered-offset distribution plus a responsiveness statistic |
| B5 | Stamping described as "did not help" while also 40%→100% | **confirmed** (text) | the split by frame is now stated in one place and the abstract matches it |

## C. Claims that need to be weakened or re-derived

| # | claim in v1 | status after audit |
|---|---|---|
| C1 | "The Position Curse is a surface-order effect" | **not established**. Reversal removes the printed-order change *and* the backward-index arithmetic in one move, so recovery under reversal cannot separate them. The `explicit_start` control (same list, same target, ordinal supplied) is the discriminating test — running now. |
| C2 | "Counting-depth limit at offset 3" | **downgraded to hypothesis**. Forward accuracy 100/100/0/40 is not monotone; offset 3 instead shows a *copy of the offset-2 answer* signature. The offset scan tests all offsets, four wordings and both lengths. |
| C3 | "The offset is represented but not used" | **narrowed**. The probe decodes `k` from a prompt that contains the ordinal `k`; at fixed L the target index is a bijection of `k`, so this is not evidence that the model computed the target position. Behavioural claims only. |
| C4 | RoPE subtraction as the paper's own mechanism | **represented as the original authors' speculation**, with our evidence neither confirming nor refuting it at frontier scale. |

## D. Executed controls and what they settled

| # | control | result | consequence |
|---|---|---|---|
| D1 | free generation vs forced choice, 128 items, aligned seed | **100% agreement** (27% vs 27% accuracy) | scorer validated. The 14% "agreement" seen earlier was my own seed mismatch (free-gen used seed 41, forced choice seed 7) — a bug in the validation script, not in the scorer |
| D2 | positional scan, forward label only, every position | L=10: 100, 100, 5, 50, 40, 35, 0, 15, 0, 35 | accuracy is a function of printed position; no monotone ceiling |
| D3 | backward cells vs positional scan at the equivalent index | observed 40/5/15/0 vs predicted 35/0/15/0; **MAD 2.5 pp** | direction adds nothing beyond position |
| D4 | same target, backward label vs forward label (index supplied) | 1/24 vs 4/24, discordant 0/3, exact p = 0.25 | no direction effect detectable; also kills "the model just needs the index computed for it" — index 9 is at floor either way |
| D5 | counting control (free generation, parsed) | L=6: 24/24; L=10: 8/24 (answers 8 or 9) | counting is better than indexing but **not intact**; the v1 sentence repeating "counting is intact" is removed |
| D6 | stamped cells with the corrected scorer | fwd k=4 8/20 → 20/20; bwd unchanged | the split result survives the harness fix |

## E. Final verdicts on the v1 claims

| claim | verdict |
|---|---|
| C1 "the curse is a surface-order effect" | **rejected**. Reversal and the positional scan are both explained by where the target sits, not by which way the list is printed. v2 no longer makes this claim. |
| C2 "counting-depth limit at offset 3" | **rejected as stated**. The pattern is 100/100/5/50/40/35/0/15/0/35 — non-monotone, with a specific unexplained collapse at position 3 that survives rewording. Reported as an unexplained anomaly. |
| C3 "offset represented but not used" | **withdrawn**. The probe decoded `k` from a prompt that states `k`; no computation was demonstrated. |
| C4 RoPE mechanism | **represented as the original authors' speculation**, not tested here. |
| v1 Tables 1–5 numbers | **superseded** by v2 Tables 1–7, regenerated with the corrected scorer (mass = 1.000, agreement = 100%). Qualitative pattern largely reproduced: fwd 100/100/0/40, bwd 40/5/15/0. |

## F. What v2 claims instead

Backward queries on a 10-item list point at printed position `11-k`. Accuracy at those positions,
measured with a forward label and no backward wording anywhere, predicts the backward condition to
within 2.5 pp on average. The model addresses the first two printed positions reliably and the interior
badly; the forward/backward asymmetry is that fact seen through a query family that mostly addresses
late positions. Reversal works because it moves the target to the front; index stamping works where the
target is already addressable and fails where it is not.


## G. Round 2: the position account itself was tested and failed

The v2 claim ("position explains the direction gap") rested on two weaknesses that the next round of
review identified, both real:

1. the backward cells and the positional scan were run on **different item seeds**, so the comparison
   was cross-sample rather than paired;
2. the one same-list direction control was at **position 9, where forward accuracy is 0** — a contrast
   at the floor cannot reveal a penalty, and equivalence there is uninformative.

Re-run as a paired design (both labels, same list, same target, every position), with the equivalence
margin (±15 pp on a 90% paired interval) fixed **before** the run:

| position | forward | backward | verdict |
|---|---|---|---|
| 1 | 100% | 0% | backward worse by > margin |
| 2 | 92% | 0% | backward worse by > margin |

At the only place where the two factors can be separated on one list — the middle of an odd length,
where "5th from the beginning" and "5th from the end" name the same ordinal and the same item — forward
12/24 vs backward 4/24, paired delta −33 pp (90% CI [−50,−17]), exact McNemar p = 0.008, all 8
discordant pairs favouring the forward label.

So **direction contributes beyond ordinal magnitude**, the v2 "position, not direction" framing is
withdrawn, and v3 reports both components with the confound stated. The v1 "surface-order" claim and the
v2 "position alone" claim are both preserved in `history/` and both superseded.


## H. Round 3: the midpoint claim, replicated and bounded

The claim retained is narrow and was tested directly: for odd L at the middle position, both labels name
the same ordinal and address the same item, so only the anchor word differs.

| cell | forward | backward | Δ (90% CI) | verdict |
|---|---|---|---|---|
| L=9, seed 71, forced choice (original) | 50% | 17% | −33 pp [−50,−17], p=0.008 | backward worse |
| L=9, seed 71, **free generation** | 50% | 17% | −33 pp [−50,−17], p=0.008 | backward worse |
| L=9, seed 101, forced (fresh lists) | 54% | 17% | −38 pp [−54,−21], p=0.004 | backward worse |
| L=7, seed 101 | 33% | 8% | −25 pp [−38,−12], p=0.031 | unresolved (CI does not clear −15 pp) |
| L=11, seed 101 | 21% | 17% | −4 pp [−21,+12] | unresolved |
| word-ordinal paraphrase | 21% | 38% | +17 pp [−4,+33] | unresolved, wrong sign |
| counting paraphrase | 12% | 12% | 0 pp [−17,+17] | no headroom |
| Qwen2.5-0.5B, L=9 | 0% | 12% | +12 pp | no headroom |

Two things follow. The midpoint effect is real, generation-validated and replicates on fresh lists at
L=9. It does **not** generalise at 24 items per cell to L=11 or to two paraphrases, and the 0.5B model
cannot test it (its forward accuracy at the midpoint is 0%).

Accordingly v4 states one claim — anchor wording changes the answer when list, target and ordinal are
held fixed, at L=9 with the baseline wording — and reports the failures to generalise in the same table.
No claim about two mechanisms, about direction in general, or about the original study's RoPE
speculation survives into v4.


## I. Round 4: interval method, interaction, and two overclaims

| item | verdict | action |
|---|---|---|
| Interaction inferred from two separate tests | **correct** — the cells share lists, so the contrast is estimable per item | computed: baseline effect −37.5 pp, paraphrase effect +16.7 pp, interaction **−54.2 pp (95% CI [−79.2,−33.3])**, within-item permutation p = 0.0004, n=24. Now §3.4 and in the abstract |
| Bootstrap interval beside p = 0.25 for the 0.5B cell | **correct** — percentile bootstrap and exact McNemar can disagree on sparse, one-sided discordance | all paired intervals switched to Newcombe's hybrid score interval; the 0.5B cell is now +12 pp [−6,+29] with p = 0.25, which agree. Boundary cells (0% or 100% arms) give boundary intervals and are flagged rather than used for equivalence |
| "The effect is tied to this length" (L=11) | **correct** — [−23,+15] still admits a meaningful penalty | reworded to "we did not establish the effect at L=11"; no claim that L=9 is special |
| "the published aggregate is partly a positional artefact" | **correct** — not established; the original evaluates all valid offsets, and with equal position weights both directions cover the same positions | claim removed from §3.6; the context table is explicitly marked as context only |
| Constant-letter baseline stated as 1/L | **correct** — gold letters are uniform over the 11-letter pool, so a fixed letter matches with probability 1/11 | fixed here and in the paper's method section |

Reproducibility pass added as §6: model and tokenizer snapshot revisions, precision (fp32, with the
bf16→fp32 conversion note), decoding settings, the exact prompt strings, the candidate-token definition
(bare ids 41–51, leading-space variants excluded), interval definitions, and paths to the raw data,
code and aggregates.

## J. Round 5: the interval routine was wrong

| item | verdict | action |
|---|---|---|
| Newcombe phi lacked the n/2 covariance correction | **confirmed** — the adjusted covariance is `max(n11*n22 − n12*n21 − n/2, 0)` when positive; the unadjusted form inflates phi and narrows the interval | routine rewritten in `code/stats_paired.py`, validated against `statsmodels.stats.proportion.confint_proportions_paired` |
| Zero-marginal handling | **confirmed** — phi must be 0 when any marginal total is 0; the old guard produced `[−100,−100]` for `[[0,0],[24,0]]` | correct value `[−100,−80.49]`; documented as a real defect, not a boundary artefact |
| Reviewer's four expected values | **independently reproduced** | `[[10,5],[2,20]]` → [−0.064393, 0.221116]; `[[4,0],[8,12]]` → [−51.23,−11.56]; `[[4,0],[9,11]]` → [−55.23,−14.84]; `[[0,0],[24,0]]` → [−100,−80.49] |
| Verdicts implied by the corrected intervals | **changed** | original and fresh midpoint no longer clear the −15 pp margin; L=7 becomes "reduction established"; word-ordinal becomes "no reduction detected" |
| McNemar p-values | **unchanged** | discordant counts unchanged (8 and 9), exact p = 0.0078125 / 0.00390625 |
| Interaction | **recomputed with plus-one** | −54.17 pp, 95% CI [−79.17,−33.33], p = 0.00048; definition, seed, resample counts and permutation operation documented; per-item terms exported |
| Chronology | **corrected** | ±15 pp margin prespecified; 90%→95% interval switch and the interaction analysis introduced after the data existed, not preregistered |

Snapshot of the superseded version: `history/v5_paper/` (paper, PDF) and `history/v5_analysis/`
(aggregates, scripts).

## K. Round 6: finalisation (methods matched to code, exact inference, packaging)

| item | verdict | action |
|---|---|---|
| Candidate set described as eleven letters | **wrong for the midpoint harness** — `midpoint.py` scores `{c for c in items}`, i.e. the L letters in that list | §2.1 and §6 rewritten; uniform baseline stated as 1/L (14.3% at L=7, 11.1% at L=9); v2's 11-letter protocol and its mass log kept separate |
| Item pool | **unstated** — `make_items` shuffles `LETTERS[:L]`, so L=7 draws J–P, L=9 J–R, L=11 J–T | §2.3 and §5 state that length is confounded with pool composition; cross-length rows marked descriptive |
| Interaction named "wording" / "word-ordinal" | **over-specific** — the paraphrase also changes "What"→"Which" and drops "at the … position" | renamed anchor × question-template interaction; no digit-versus-word claim; labelled exploratory |
| Permutation p | **Monte Carlo where exact was feasible** — 12 nonzero terms give 2¹² = 4,096 assignments | enumerated: 2 extreme, p = 0.00048828125; Monte Carlo (47 exceedances) kept only as a cross-check |
| Non-default alpha | **bug** — the hand-rolled inverse normal returned −2.5758 for α=0.01 | replaced by `statistics.NormalDist`; 90/95/99% tested against reference values and for nesting |
| Test runner | printed "SOME FAILED" but exited 0 | exits nonzero on any failure |
| Manifest listed `make_manifest.py` | **real bug found by verification** — `EXCLUDE` held bare names and was compared against relative paths, so `code/make_manifest.py` slipped in | excluded by basename; `verify` now fails if any excluded name is listed, and fails on unlisted files |
| Manuscript embedded hashes of itself | **circular** (`assemble_v6.py` hashed `paper_v6_final.md`, which it was writing) | hash table removed from the paper; hashes live only in the package manifest, generated after everything is final |
