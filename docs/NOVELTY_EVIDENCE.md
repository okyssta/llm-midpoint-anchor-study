# Evidence register

Page numbers are **PDF page numbers** (as printed by `pdftotext -f N -l N`), not the journal's printed
folios. Section numbers are as in each paper. Quotes are verbatim except for `[…]` elisions.

Files: `sources/2605.07127.pdf` (Zhang et al.), `sources/leidinger.pdf` (Leidinger et al.),
`sources/2310.11324.pdf` (Sclar et al.), `sources/lostmiddle.pdf` (Liu et al.),
`sources/reversal.pdf` (Berglund et al.).

---

## A. Zhang et al., *The Position Curse* (arXiv:2605.07127v1, 8 May 2026)

**A1 — the task family and the four axes.** p2, §1 contributions:
> "two query directions (position→item … and item→position …), two anchor types (relative to the
> start/end of the list, and relative to a given item), two indexing directions (forward and backward),
> and two types of items (single-token letters and multi-token words)."

**A2 — formal operators.** p3, §3.2:
> "The four index operators are End+ : S[n], End− : S[−n], Rel+ : S[r+n], Rel− : S[r−n], with
> S[−n] ≡ sL−n+1"

This is the closest thing to a midpoint: at odd L and n = (L+1)/2, `End+` and `End−` return the same
element. Nothing in the paper singles out that case for analysis, but at L=5 the specification does
instantiate it.

**A3 — evaluation protocol; sequences are sampled per condition, pairing not documented.** p13, §C.3:
> "Each condition fixes the query type, anchor type, indexing direction, item type, prompt variant, and
> sequence length L ∈ {5, 10, 20}. We sample 50 independent sequences per condition and instantiate the
> valid offsets for each sequence, yielding deterministic targets while preserving variation in the list
> content."

Consequences for this audit. (i) The paper does not report a paired midpoint analysis: results are
condition-level aggregates. The published methods state that sequences are sampled per condition and do
not document cross-condition pairing; this audit did not verify list reuse from code or data, so "does
not document" is the strongest claim made here. (ii) Only L=5 in their grid is odd — at L=10 and
L=20 there is no exact midpoint ordinal. (iii) At L=5 the protocol instantiates the valid offsets,
which includes n=3 in both directions, so the two midpoint queries are already present in their data
even though no paired analysis of them is reported.

**A4 — per-position curves exist.** p18, Fig. 10 caption:
> "Per-query-position accuracy at L=20 for the four position-retrieval tasks […] Backward-query panels
> are ordered by absolute position (decreasing left-to-right), matching the directional convention used
> in Fig. 2b,d."

This is the nearest prior artefact: a reader can compare forward and backward curves at a matched
*absolute position*. It is not a paired contrast: the published methods do not document cross-condition
pairing, and the paper does not report a paired midpoint analysis. At a given absolute position p the
forward query names ordinal p while the backward query names ordinal L−p+1.

**A5 — phrasing is randomised in training data, not manipulated at evaluation.** p13, §C.2:
> "We randomize list formatting and query phrasing, and include a small number of multi-turn list
> conversations so that the model sees positional queries in more natural dialogue contexts."

**A6 — the mechanism is explicitly speculative.** p8, §4:
> "We speculate on a possible mechanistic interpretation of why counting succeeds while backward
> position-based retrieval fails. […] Backward retrieval, in contrast, requires a position subtraction
> rather than a direct readout. […] Under rotary position embeddings (RoPE) …, position information
> enters only through the rotation of attention keys and queries; it is never written into the value
> projection and therefore never appears in the residual stream itself."

**A7 — counting control.** p3, §3.1:
> "Given a sequence, the model was asked 'How many items are in the sequence?' […] counting here does
> not require retrieving items at specific positions, but still requires tracking sequence length,
> isolating general counting from positional retrieval."

**A8 — related-work boundary the authors themselves draw.** p2, §2:
> "Lost in the Middle [14] measures how the position of the target in a long context affects retrieval
> accuracy, reporting a characteristic U-shape positional effect in retrieval. However, its retrieval
> remains content-based rather than position-based retrieval studied here. OpenAI's MRCR [16] … does not
> systematically vary direction (forward vs. backward), anchor …"

**A9 — citation status.** Semantic Scholar graph API returned 0 citing papers on 2026-10-27; a
bibliographic mirror listed "Citations: 0". Searches for follow-ups surfaced only summaries and mirrors
of the paper itself.

---

## B. Sclar et al., *Quantifying LM Sensitivity to Spurious Features in Prompt Design* (ICLR 2024; arXiv:2310.11324v2)

**B1 — headline claim.** p1, abstract:
> "several widely used open-source LLMs are extremely sensitive to subtle changes in prompt formatting
> in few-shot settings, with performance differences of up to 76 accuracy points when evaluated using
> LLaMA-2-13B."

**B2 — what varies.** p3, §3:
> "Each basic field consists of a descriptor (e.g. 'Passage'), a separator (e.g. ': '), and a text
> placeholder to replace with each data point."

Separators, spacing, casing, itemisation — the grammar of the template, not the content of the question.

**B3 — task family.** p5, §4.1:
> "We use a subset of 53 tasks from Super-NaturalInstructions (Wang et al., 2022) with diverse
> human-written formats and instructions, comprising 19 multiple-choice tasks and 34 classification
> tasks with {2, 3, 4} basic fields."

No positional-retrieval task appears in this list.

**B4 — spread magnitude.** p8, §4.2:
> "with 25% of tasks having a spread of 0.310 and a maximum of 0.841."

**B5 — citation status.** 100 citing papers sampled via Semantic Scholar on 2026-10-27; titles are
prompt-sensitivity, judge-robustness, harness and evaluation-methodology work. None matched positional
retrieval or list indexing.

---

## C. Leidinger et al., *The language of prompting* (Findings of EMNLP 2023; 2023.findings-emnlp.618)

**C1 — what varies.** p1, abstract:
> "We investigate both grammatical properties such as mood, tense, aspect and modality, as well as
> lexico-semantic variation through the use of synonyms."

**C2 — headline magnitude.** p5, §5:
> "On QA (Table 3) and NLI (Table 4) datasets, we find numerous examples of drops in accuracy by up to
> 5 percentage points."

**C3 — length is not the driver.** p2, §1:
> "Further, we find no correlation between performance and prompt length"

**C4 — task family.** p3–5: Boolean question answering (BoolQ), NLI (RTE, CB), multiple-choice science
(ARC-E), sentiment (SST, IMDB). No positional or list-indexing task.

---

## D. Adjacent established results (different axes)

**D1 — Liu et al., *Lost in the Middle* (arXiv:2307.03172v3), p1, abstract:**
> "We analyze the performance of language models on two tasks that require identifying relevant
> information in their input contexts: multi-document question answering and key-value retrieval."

U-shaped accuracy as a function of where the evidence sits in the context. The axis is *where the
evidence is*, not *which end the ordinal counts from*; retrieval is content-based.

**D2 — Berglund et al., *The Reversal Curse* (arXiv:2309.12288v4), p1, abstract:**
> "We expose a surprising failure of generalization in auto-regressive large language models […]"

A model trained on "A is B" does not generalise to "B is A". Direction asymmetry in *parametric
factual recall*, not in-context ordinal indexing.

---

## E. Search log (what was looked for, and where)

| query | venue | result |
|---|---|---|
| `abs:"position-based retrieval"` | arXiv API, all dates | only 2605.07127 |
| `abs:"backward indexing"` | arXiv API | unrelated (information theory, 2010) |
| `abs:"list indexing" AND abs:"language model"` | arXiv API | query returned 503; retried via S2 search, no positional hits |
| `"from the end" "from the beginning" same item … control` | web | no positional-retrieval hit; PC and mirrors only |
| `midpoint / same target / matched position` in PC full text | local | no occurrences of "middle position", "same item", "pairs" |
| PC citations | Semantic Scholar | 0 |
| Sclar citations | Semantic Scholar | 100 sampled, none positional |
| Leidinger citations | — | prompt-sensitivity follow-ups; not positional |

**Limits of the search.** Absence of a hit is not proof of absence. Semantic Scholar lags recent arXiv
papers; institutional search (Google Scholar, Scopus, ACL Anthology full text) was not available from
this host. The Position Curse is five months old with no indexed citations, so the space may simply not
have been explored yet rather than having been explored and found negative.
