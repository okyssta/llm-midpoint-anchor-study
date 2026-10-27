# Novelty audit: the midpoint contrast and the anchor × template interaction

**Subject.** *Changing One Word* (v6), frozen at `releases/v6-final/`.
**Status of the work audited.** An exploratory controlled extension of the forward–backward asymmetry
literature, not a discovery claim.
**Question.** Which parts of that study are already established, which are specific to our design, and
what remains unresolved.
**Sources.** Primary PDFs only, page-anchored in `EVIDENCE.md`: Zhang et al. (arXiv:2605.07127),
Sclar et al. (ICLR 2024, arXiv:2310.11324), Leidinger et al. (Findings EMNLP 2023), plus Liu et al.
(*Lost in the Middle*) and Berglund et al. (*Reversal Curse*) as adjacent results.
**Date of search.** 2026-10-27.

---

## 1. Summary

1. **The direction asymmetry is not ours.** Zhang et al. establish that backward positional retrieval
   lags forward retrieval across model families, anchors, query types and item types (p1–2, p5).
   Our baseline cells replicate that asymmetry.
2. **Prompt sensitivity is not ours either.** Sclar et al. show formatting changes worth up to 76
   accuracy points on 53 classification and multiple-choice tasks (p1, p5); Leidinger et al. show
   grammatical and lexical variation worth up to 5 points on QA and NLI (p1, p5). Neither concerns
   ordinal indexing.
3. **The midpoint queries are already in Zhang's protocol, at L=5.** Their operators are `End+ : S[n]`
   and `End− : S[−n]` (p3) instantiated over the valid offsets (p13), so at L=5 the ordinal n=3 makes
   the two queries address the same item. What the paper does not report is an analysis built on that
   coincidence: the results are condition-level aggregates, the published methods do not document
   pairing, and no template manipulation is reported. Our contribution is the explicit same-list, same-item, same-ordinal
   *analysis*, plus the anchor × template estimate — not the existence of the queries.
4. **The interaction is motivated by prior prompt-sensitivity research.** That an anchor effect might
   depend on the question template follows from Sclar and Leidinger at the level of "templates matter";
   we did not find a within-item estimate in positional retrieval in the sources reviewed. Ours uses one paraphrase, so it
   quantifies an interaction between these two templates, not a general law.
5. **What remains genuinely open** is narrow: mechanism, behaviour at larger scales, and whether the
   midpoint difference is anchor-specific or an instance of template noise. Our data settle none of
   these.

---

## 2. Comparison matrix

### 2.1 Established findings we inherit

| # | Finding | Source, page | Scope of the evidence |
|---|---|---|---|
| E1 | Backward positional retrieval substantially lags forward retrieval | Zhang p1–2, p5; Fig. 2c | 2 query types × 2 directions (four tasks) × 2 anchors × 2 item types, L ∈ {5,10,20}; open and closed models |
| E2 | The gap is not explained by counting | Zhang p3, §3.1; Fig. 2 row 1 | Counting near-ceiling (78–100%) on the same short lists |
| E3 | Per-position accuracy curves are available for both directions | Zhang p18, Fig. 10; p14, Fig. 7 | L=20, backward panels ordered by absolute position |
| E4 | Position of evidence in a long context gives a U-shaped curve | Liu p1 | Content-based retrieval, multi-document QA and KV retrieval |
| E5 | Prompt *formatting* changes accuracy by tens of points | Sclar p1, p5, p8 | 53 Super-NaturalInstructions tasks: 19 multiple-choice, 34 classification |
| E6 | Semantically equivalent *grammatical/lexical* variation changes accuracy | Leidinger p1, p5 | BoolQ, RTE, CB, ARC-E, SST, IMDB; drops up to 5 pp |
| E7 | Direction asymmetry also appears in parametric factual recall | Berglund p1 | "A is B" vs "B is A" after training, not in-context indexing |

### 2.2 Our exact experimental differences

| # | Our design choice | What it changes relative to the sources | Where it matters |
|---|---|---|---|
| D1 | **Same list, same item, same ordinal.** At odd L the midpoint satisfies p = L−p+1, so "k-th from the beginning" and "k-th from the end" are the same query up to the anchor word | Zhang's protocol contains both midpoint queries only at L=5 (n=3); elsewhere the two directions address different items at the same ordinal, and different ordinals for the same item | Makes the anchor the only difference between the two arms of a pair (E1) |
| D2 | **Within-list pairing.** Each item contributes a forward and a backward outcome | The published methods do not document cross-condition pairing, and the paper does not report a paired midpoint analysis. (p13) | Holds list identity constant and enables a paired statistic (Newcombe, exact McNemar); the precision gain depends on within-pair covariance; see §2.4 |
| D3 | **Odd lengths only** (7, 9, 11) | Zhang's grid is 5, 10, 20 — the midpoint ordinal exists only at L=5 | The contrast is expressible at every length we run |
| D4 | **Two templates × two anchors, crossed** | Zhang randomises phrasing only in SFT data (p13); evaluation uses a fixed template per condition | Allows an interaction estimate rather than a main effect |
| D5 | **Forced-choice scoring with generation cross-check** | Zhang uses 3-shot generation, temperature 0.7, exact match | Removes decoding noise and parser sensitivity from the contrast; both modes gave identical 2×2 tables |
| D6 | **Nine cells, one position, 24 items, uncorrected** | Much smaller than any source here | Bounds what can be claimed |

### 2.3 Genuinely unresolved novelty

| # | Claim | Status after the audit | Why it is not already covered |
|---|---|---|---|
| N1 | A **paired, same-item, same-ordinal** estimate of the anchor effect | Not reported in any source we could find | Requires D1 + D2. Zhang's protocol contains the two midpoint queries at L=5, but the paper does not report a paired midpoint analysis |
| N2 | The estimated anchor effect **differs between the two tested templates**, measured within item (−54.17 pp, exact p = 2/4096) | Not reported in positional retrieval; measured here | Sclar and Leidinger establish template sensitivity in other task families, but not an anchor × template interaction in positional retrieval |
| N3 | Mechanism of the midpoint difference | Open | Zhang explicitly speculates (p8, "We speculate…"); no test in either paper |
| N4 | Behaviour at larger models and longer odd lengths | Open | Our cells are 0.5B and 1.5B at L ≤ 11; Zhang's models are larger but his grid has no odd length above 5 |

### 2.4 On independent samples and pairing

Independent and paired designs estimate the same population contrast only under matched experimental
conditions: the same position set, the same aggregation rule, the same item pool. That condition does
not hold between the two studies here. Zhang's reported quantity averages over all valid offsets, so
its estimand is a position-averaged anchor effect; ours is the anchor effect at the midpoint only.
These are different population quantities, and the difference is one of estimand rather than of
statistical efficiency. A design that samples lists independently and one that pairs lists within
items both target an all-position quantity if they use the same offsets and aggregation rule; neither
equals a midpoint-only contrast.

Within that caveat, independent samples are a valid way to estimate a contrast. The published methods do not document cross-condition pairing, and the paper does not report a
paired midpoint analysis; nothing in this audit verifies list reuse from code or data. Our design does
not show that theirs is wrong, and their aggregate is not invalidated by the absence of a reported
pairing.

Pairing holds list identity constant and enables paired analysis; its precision benefit depends on
within-pair covariance. When the two arms of a pair are strongly correlated, the paired difference has
smaller variance than the difference of independent means; when they are not, the benefit shrinks.
What pairing guarantees is the design property — the anchor is the sole within-pair difference, with
item-level tests (exact McNemar, Newcombe) available — not a given gain in precision.

---

## 3. What the matrix rules out claiming

- **Not "first to show backward indexing is hard."** E1 is Zhang's contribution, replicated by us.
- **Not "first to show prompts matter."** E5 and E6 predate this work, with larger effects and larger
  task suites.
- **Not "the effect is a positional artefact."** Our own v6 retracted that; Zhang evaluates all valid
  offsets, so their aggregate is position-balanced even though the paper does not report a paired
  midpoint analysis.
- **Not "the interaction isolates digit-versus-word ordinals."** The paraphrase also changes "What" to
  "Which" and drops "at the … position". Sclar's grammar (B2) is a reminder that several formatting
  dimensions move together unless crossed.
- **Not "Zhang's design is inadequate."** Independent samples can estimate either a midpoint-only or an
  all-position contrast. The estimand depends on the positions and aggregation used; pairing determines
  the relationship between observations. The differences between the studies are estimand and pairing
  structure, not validity.
- **Not "first".** No search establishes priority, and this audit does not attempt to.

---

## 4. Search limitations

Missing citations, absent search hits and failed queries are limitations of this audit, not evidence of
originality. Semantic Scholar returned zero citations for the Position Curse and 100 (sampled) for
Sclar; arXiv API searches for `abs:"position-based retrieval"` returned only the Position Curse itself.
Google Scholar, Scopus and ACL Anthology full-text search were not reachable from this host, and
Semantic Scholar lags recent arXiv deposits. A zero citation count reflects indexing lag as much as the
state of the literature, and this audit draws no inference from it.

The statements in §2.3 are accordingly of the form "not reported in any source we could find" and "the
paper does not report" — not "does not exist" and not "was never done". Nothing here is a priority
claim.

---

## 5. What a reviewer could still object to, and the answer

| Objection | Answer | Where it is answered |
|---|---|---|
| "Fig. 10 already compares forward and backward at matched positions." | Those panels order by *absolute position*; at position p the forward query names ordinal p and the backward query names L−p+1. The published methods do not document cross-condition pairing, and the paper does not report a paired midpoint analysis, so it is a visual comparison rather than an item-level contrast. | EVIDENCE A3, A4 |
| "Independent samples are equally valid." | Yes. Independent samples can estimate a midpoint-only or an all-position contrast. Zhang's reported all-position aggregate differs from our midpoint-only estimand; pairing separately holds list identity constant and enables paired analysis. | §2.4 |
| "Prompt sensitivity is well known." | Yes — for formatting (Sclar) and grammar (Leidinger), in classification tasks. It is not reported in the sources reviewed whether the estimated anchor effect differs between templates in positional retrieval; across the two templates we tested, it does. | EVIDENCE B1–B3, C1–C4 |
| "One paraphrase is not a template sample." | Correct, and stated as a limit. It supports an interaction estimate between these two templates, not a distribution over templates. | v6 §5 |
| "24 items per cell." | Correct. The intervals are wide by construction, and the margin verdicts reflect that. | v6 §3.1, §5 |
| "The effect could be a length effect, since pools differ." | Length is confounded with pool (J–P / J–R / J–T), stated in v6 §2.3; only the within-list contrasts are used for claims. | v6 §2.3, §5 |

---

## 6. Contribution statement

An exploratory controlled extension of the forward–backward asymmetry literature: a same-list,
same-item, same-ordinal paired estimate of the anchor effect in one small model, and evidence that the
estimated effect differs between the two question templates tested. The asymmetry itself, and prompt
sensitivity in general, are prior results. This study adds the paired midpoint analysis and its
within-item interaction estimate, at the scale and with the limits reported in v6, and makes no
priority claim.
