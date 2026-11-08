# Word budget for MLESP (8 pages IEEE two-column, INCLUDING references)

**Updated 2026-09-24 from a compile test, replacing the earlier ≈5,900-word estimate, which was wrong.**

## What was measured

A scratch copy of `paper.tex` was compiled in the real IEEEtran template with:
- every section padded to a given share of its budget, using words drawn from our own drafted prose (so word lengths are realistic);
- all six display items at final size: Fig. 1–4 from the real generator scripts, Table I with 18 rows, Table II;
- 40 references (the blueprint's 35–45 target), without the temporary UNVERIFIED notes.

| Share of the old 5,900 budget | Total words (incl. Contributions and Conclusion) | Pages |
|---|---|---|
| 100% | ≈5,900 | **11** |
| 75% | ≈4,400 | 8 (last page full) |
| 80% | ≈4,650 | 9 |

**Capacity is about 4,400 words. Target: about 4,250**, leaving margin for paragraph breaks, headings and float placement.

The old estimate assumed figures and tables were "already priced into" the blueprint's 8 pages. They were not: six display items plus 40 references take roughly 3 of the 8 pages.

## Current draft (2026-09-24, evening; counted with page_fill_test.py's own counter, which skips LaTeX markup, figures, tables and placeholders)

| § | Section | Old budget | Option B target | Drafted now |
|---|---|---|---|---|
| I | Introduction (I-A, I-B) | 540 | 380 | 374 |
| — | Contributions list (fixed wording) | 225 | 130 | ≈130 |
| II | Related Work | 770 | 380 | 414 |
| III | Leakage in Connectivity Pipelines | 1,045 | 760 | 646 |
| IV | Methods | 1,135 | 760 | 766 |
| V | Results | 1,180 | 1,000 | 56 (placeholders) |
| VI | Checklist prose (around Table II) | 455 | 220 | 196 |
| VII | Discussion and Limitations | 410 | 380 | 274 (interpretation paragraph pending) |
| VIII | Conclusion | 135 | 100 | 81 (draft; one clause pending) |
| | **Total** | **≈5,900** | **≈4,110** | **≈2,940** |

About 1,170 words remain for Results (~945), the Section VII interpretation paragraph (~100) and small fills, so the draft lands near 4,100 with **no cuts needed** under option B. Under option A, II and IV would still need cutting (see below).

## Two ways to reach ≈4,250 (advisor question 2 decides)

§9 says: "If the paper runs long, cut from Sections I and II, never from III or V." At 4,250 words that rule cannot be applied to I and II alone: III–VIII at their old budgets already come to about 4,100.

| § | (A) Literal §9: III and V at full budget | (B) Keep all drafted text, release unused III/V budget |
|---|---|---|
| I | 300 | 380 |
| Contributions | 130 | 130 |
| II | 300 | 380 |
| III | 1,045 | 760 |
| IV | 620 | 760 |
| V | 1,180 | 1,000 |
| VI | 220 | 220 |
| VII | 300 | 380 |
| VIII | 100 | 100 |
| **Total** | **≈4,195** | **≈4,110** |

- **(A)** deletes about 80 words from I, 115 from II and 210 from IV, all already drafted. VII can barely hold the interpretation paragraph plus both required limitations (§14).
- **(B)** cuts nothing already written in III or V; it only declines to grow III from 701 to 1,045. I, II and IV lose 0–75 words each. Results gets 1,000 words, enough for V-A to V-D.

**Recommendation: (B)**, pending the advisor.

## Re-running the measurement

`python 06_Manuscript/tools/page_fill_test.py 0.75 40` rebuilds the projection (scale, reference count); it works on a temp copy and never touches the manuscript. Re-run it after any change to figure sizes, Table I's columns or the reference count, since each shifts capacity.
