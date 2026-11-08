# Auditing Data Leakage and Reporting Gaps in EEG Connectivity Deep Learning for Depression Detection

Data and code for the MLESP 2026 workshop paper (IEEE BIBM 2026, Dallas, Dec 1–4, 2026).

Kunal Chevuri (Prosper High School) · Leah Ileto (St. Lucy's Priory High School) ·
Mohammed Aledhari (University of North Texas)

Paper ID **S02212**. The manuscript source is in [`06_Manuscript/`](06_Manuscript/).

---

## What this is

We define five points in an EEG functional-connectivity pipeline at which information can pass
from a test set into training — epoch partitioning (L1), connectivity scope (L2), thresholding
(L3), normalization (L4), and channel or band selection (L5) — and a four-level risk rating
(*free / possible / likely / unclear*) that can be applied **from a paper's reported methods
alone**. We then rate 18 studies from a citation-ranked corpus.

The corpus is citation-ranked, **not** systematically searched. The proportions below describe
this corpus; they are not prevalence estimates for the literature.

## What you can check here

Everything the paper's availability statement promises:

| | Where |
|---|---|
| Final coding sheet, incl. the **evidence quote** supporting each study's rating | [`04_Phase4_Coding/coding_sheet_FINAL.csv`](04_Phase4_Coding/coding_sheet_FINAL.csv) |
| **Both raters' independent codes**, as received, before any resolution | [`04_Phase4_Coding/snapshots_pre_resolution/`](04_Phase4_Coding/snapshots_pre_resolution/) |
| Pre-resolution agreement (κ = 0.91, 17/18 studies) | [`04_Phase4_Coding/agreement_pre_resolution.csv`](04_Phase4_Coding/agreement_pre_resolution.csv) |
| The one disagreement and how it was settled | [`04_Phase4_Coding/TIEBREAK_for_advisor.md`](04_Phase4_Coding/TIEBREAK_for_advisor.md), [`disagreement_resolution.csv`](04_Phase4_Coding/disagreement_resolution.csv) |
| The rating rule, as executable code | [`04_Phase4_Coding/score_ratings.py`](04_Phase4_Coding/score_ratings.py) |
| All analysis, every result file, every figure | [`05_Phase5_Analysis/`](05_Phase5_Analysis/), [`06_Manuscript/figures/`](06_Manuscript/figures/) |
| The four post-hoc analyses added in response to peer review | [`05_Phase5_Analysis/reviewer_response.py`](05_Phase5_Analysis/reviewer_response.py) |
| Screening record and PRISMA-style counts | [`03_Phase3_Corpus/screening_log.csv`](03_Phase3_Corpus/screening_log.csv), [`prisma_counts.csv`](03_Phase3_Corpus/prisma_counts.csv) |
| Every departure from the pre-specified protocol, dated | [`08_Admin/deviations_log.md`](08_Admin/deviations_log.md) |
| How AI tools were used, per task | [`08_Admin/ai_use_log.md`](08_Admin/ai_use_log.md) |

**No number in the paper is typed by hand.** Every count, percentage and interval is a LaTeX macro
generated into `06_Manuscript/macros_counts.tex` by the pipeline below. If you change a code in a
rater sheet and re-run, the paper's numbers change with it.

## Reproducing the results

```
python run_pipeline.py
```

Or step by step:

```
cd 04_Phase4_Coding
python score_ratings.py --a rater_A_Kunal_2026-09-23.xlsx --b rater_B_Leah_2026-09-23.xlsx
python build_final_coding_sheet.py
python ../05_Phase5_Analysis/build_results.py        # analysis, Fig. 3, Table I, macros
python ../05_Phase5_Analysis/sensitivity.py
python ../05_Phase5_Analysis/rq4.py
python ../05_Phase5_Analysis/reviewer_response.py    # the four post-hoc analyses
python ../06_Manuscript/make_macros.py
cd ../06_Manuscript && pdflatex paper && bibtex paper && pdflatex paper && pdflatex paper
```

Needs Python 3.11+ with `pandas`, `numpy`, `scipy`, `matplotlib`, `openpyxl`, and a LaTeX
distribution. Bootstrap and permutation results are seeded (seed 20260923), so they reproduce
exactly.

## Two things to read before citing the numbers

1. **"Not reported" is not "not performed."** A step a paper never mentions cannot be
   distinguished from one never performed. The ratings code such silence as *not performed*; both
   peer reviewers objected, and they were right. `reviewer_response.py` therefore also computes
   the strictest reading, under which **no study in the corpus can be verified leakage-free**. The
   epoch-level finding and the leakage-likely count are unaffected by the convention.
2. **Per-surface agreement is uneven.** Inter-rater κ is 0.91 for partitioning (L1) but **0.36 for
   channel/band selection (L5)**, below the 0.4 we pre-specified. Every L5 figure in the paper is
   marked provisional, and the paper says so. Treat the L5 results as weaker than the rest.

## Not included here

This is a release of the audit, not of the whole working folder. Withheld deliberately:

- the advisor's unpublished planning document, and his question-and-ruling correspondence;
- summaries written by other students in the ThinkNeuro cohort, which were never a coding source;
- peer-review correspondence and conference submission logistics.

A few comments in the code still refer to those paths. Nothing needed to reproduce a number in the
paper is missing; if you find otherwise, please open an issue.

## Study identifiers

Studies are referred to as S01–S18 throughout. The mapping from those IDs to DOIs is in
[`04_Phase4_Coding/study_id_key_2026-09-23.csv`](04_Phase4_Coding/study_id_key_2026-09-23.csv).
The paper deliberately does not name individual studies as leakage examples; the aim is to
describe reporting practice, not to single out authors.

## Citing

Please cite the paper. A `CITATION.cff` will be added once the proceedings DOI is assigned.

## License

Code: MIT. Coding sheets, ratings and other data: CC BY 4.0. Bibliographic metadata in
`source_materials/` is derived from Web of Science and remains subject to its provider's terms.
