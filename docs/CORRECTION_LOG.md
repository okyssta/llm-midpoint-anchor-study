# Correction log: v5 → v6

**Subject.** *Changing One Word: a paired test of anchor direction in list indexing.*
**Scope.** Statistical implementation and everything derived from it. No new model runs; all numbers
regenerated from the same raw records.

## 1. The defect

The v5 paired intervals used a mis-specified Newcombe method 10:

1. **Missing covariance correction.** Newcombe's phi uses an n/2 adjustment of a *positive* covariance
   term:

   ```
   cov = n11*n22 - n12*n21
   if cov > 0: cov = max(cov - n/2, 0)
   phi = cov / sqrt((n11+n12)(n21+n22)(n11+n21)(n12+n22))
   ```

   v5 used the unadjusted `(n11*n22 - n12*n21)/sqrt(marginal products)`, which inflates phi and
   therefore makes the interval too narrow.

2. **Zero marginals.** When a marginal total is zero the correlation is undefined; Newcombe sets
   phi = 0. v5 reached phi = 0 only through a division guard, and the guard also produced the
   degenerate `[-100,-100]` interval for a perfectly one-sided 2×2 table, which v5 described as an
   unavoidable boundary result. It is not: the correct interval for `[[0,0],[24,0]]` is
   `[-100%, -80.49%]`.

## 2. Independent validation

The corrected routine (`code/stats_paired.py`) reproduces
`statsmodels.stats.proportion.confint_proportions_paired` (main branch), whose docstring is itself
verified against R `ratesci::moverpairci` and `PropCIs`:

| case | table (bwd × fwd) | expected 95% CI | obtained |
|---|---|---|---|
| reference example | `[[10,5],[2,20]]` | `[-0.0643926050711, 0.2211160178958]` | matches to 1e-9 |
| original midpoint | `[[4,0],[8,12]]` | `[-51.23, -11.56]` pp | `[-51.23, -11.56]` |
| fresh midpoint | `[[4,0],[9,11]]` | `[-55.23, -14.84]` pp | `[-55.23, -14.84]` |
| perfect discordance | `[[0,0],[24,0]]` | `[-100, -80.49]` pp | `[-100.00, -80.49]` |

`code/test_stats_paired.py` also checks transpose symmetry (swapping classifications negates and
reverses the interval), concordant tables (interval has positive width: ±13.8 pp at n=24), all-correct
and all-wrong tables, and the exact McNemar values. All pass.

## 3. What changed in the numbers

| cell | v5 | v6 (corrected) | verdict change |
|---|---|---|---|
| original midpoint, forced | −33.3 [−50,−17] | −33.3 [−51.2,−11.6] | margin cleared → not cleared |
| original midpoint, generation | −33.3 [−53,−17] | −33.3 [−51.2,−11.6] | same as above |
| fresh midpoint | −37.5 [−54,−21] | −37.5 [−55.2,−14.8] | margin cleared → not cleared |
| L=7 | −25.0 [−38,−12] | −25.0 [−44.3,−5.0] | unresolved → reduction established |
| word-ordinal | +16.7 [−4,+33] | +16.7 [−7.2,+38.2] | wrong sign → no reduction detected |
| L=11 | −4.2 [−21,+12] | −4.2 [−24.5,+16.3] | unchanged |
| counting | 0.0 [−17,+17] | 0.0 [−21.3,+21.3] | unchanged (no headroom) |
| 0.5B, L=9 | +12.5 [−6,+29] | +12.5 [−3.5,+31.0] | consistent with p = 0.25 |
| interaction | −54.2, p = 0.0004 (Monte Carlo) | −54.17, p = 2/4096 = 0.00048828125 (exact) | same conclusion |

Exact McNemar p-values are unchanged: the discordant counts are unchanged (8 and 9 pairs), and the
correction affects only the interval construction. p = 0.0078125 and p = 0.00390625.

## 4. What survives

* The midpoint reduction is real in the tested setting: four cells have intervals entirely below zero
  (original forced, original generation, fresh forced, L=7), with exact p from 0.0039 to 0.031.
* Forced choice and free generation give the identical 2×2 table on the original lists.
* The interaction is large and clear: −54.17 pp, 95% CI [−79.17, −33.33], exact permutation
  p = 2/4096 = 0.00048828125. Sensitivity to the question template is demonstrated within item, not
  inferred from separate tests. It is an anchor × question-template interaction: the paraphrase changes
  "What"/"Which" and the position phrase as well as the numeral, so no digit-versus-word claim is made.
  The analysis is exploratory.
* The published aggregate is not shown to be a positional artefact; no claim about it survives.

## 5. What does not survive

* Any statement that the reduction exceeds the 15-point practical margin. The upper ends are −11.6,
  −11.6, −14.8 and −5.0 points. "Reduces accuracy" is supported; "reduces it by more than 15 points"
  is not.
* "Costs about a third of the accuracy." Replaced by "reduces accuracy by 33–38 percentage points".
* "Newcombe throughout." Paired binary contrasts use Newcombe method 10; the interaction uses an item
  bootstrap and a within-item permutation test.
* The degenerate `[−100,−100]` boundary interval and its justification.

## 6. Chronology

| version | interval method | interaction analysis | status |
|---|---|---|---|
| v1–v4 | 90% percentile bootstrap | absent | superseded |
| v5 | 95% Newcombe (mis-specified) | added | superseded, kept in `history/v5_paper/` |
| v6 | 95% Newcombe method 10, validated | exact enumeration, documented | current |

The ±15 pp margin and the 24-item cells were fixed before the midpoint runs. The interval method and
the interaction analysis were **not** prespecified: both were introduced after the data existed. No
dated protocol supports describing them as preregistered.

## 7. Still exploratory

L=7, the counting paraphrase, both 0.5B cells, the positional scan and the index-stamping probe. The
grid is uncorrected for multiplicity (nine cells); a p-value near 0.03 would not survive a
Bonferroni-style adjustment.

## 8. Finalisation corrections (v6, before release)

1. **Candidate set.** `midpoint.py` scores only the L letters present in the list
   (`{c for c in items}`), not all eleven pool letters. The uniform-choice baseline for those cells is
   1/L (14.3% at L=7, 11.1% at L=9). The earlier v2 protocol (`score_positions.py`) scored all eleven
   letters J–T and logged candidate mass; those mass figures belong to v2 only.
2. **Item pool.** `task.py::make_items` shuffles `LETTERS[:L]`, so L=7 draws from J–P, L=9 from J–R and
   L=11 from J–T. Length is confounded with pool composition; the within-list midpoint contrasts are
   unaffected, but cross-length rows are descriptive only.
3. **Interaction naming.** The paraphrase differs from the baseline in more than the ordinal: "What"
   becomes "Which" and "at the … position" is dropped. The result is therefore named an anchor ×
   question-template interaction, and no digit-versus-word claim is made.
4. **Exact permutation.** The 24 interaction terms are twelve 0s, eleven −1s and one −2. Zeros are
   invariant under sign flips, so the exact distribution is over 2¹² = 4,096 assignments; two are as
   extreme as observed, giving p = 2/4096 = 0.00048828125. The Monte Carlo run (47 exceedances in
   100,000, plus-one p = 0.00048) is retained only as a cross-check.
5. **Non-default confidence levels.** The hand-rolled inverse normal returned a negative value for
   α = 0.01; replaced by `statistics.NormalDist`. 90%, 95% and 99% intervals now match reference values
   and nest correctly.
6. **Test runner** exits nonzero if any check fails.
7. **Packaging.** Environment metadata is separated from valid requirement files; the analysis path
   needs no third-party packages. `SHA256SUMS` excludes itself, the manuscript no longer embeds hashes
   of itself, and every manifest entry is verified with `sha256sum -c`.
