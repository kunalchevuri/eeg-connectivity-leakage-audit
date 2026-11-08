# Tiebreak needed: 1 study (blueprint §7.4, advisor as tiebreaker)

Both raters finished coding all 18 studies independently on 2026-09-24. Both workbooks were scored mechanically by `score_ratings.py`, with no hand edits, and snapshotted unchanged in `snapshots_pre_resolution/` (SHA-256 in `SHA256SUMS.txt`).

**Pre-resolution agreement: 17/18 (94.4%), Cohen's κ = 0.91 (bootstrap 95% CI 0.66 to 1.00; seed 20260923, 10,000 resamples).** This is well above the 0.4 stop threshold. It comes from `analysis.py`'s own `rq2()`, and `build_results.py` regenerates it.

## The one disagreement: S11 (WoS rank 55)

| Surface | Kunal | Leah |
|---|---|---|
| L1 split_unit | unclear | **epoch** |
| L2 connectivity_scope | within-fold | within-fold |
| L3 threshold_fit | none | none |
| L4 normalization_fit | none | none |
| L5 selection_fit | none | **unclear** |
| **Rating (mechanical)** | **unclear** | **likely** |

- **Kunal's evidence:** "The model is then trained and monitored for validation accuracy using loss as "binary cross-entropy", optimizer as "adam", and metrics as "accuracy"." His note: no sentence describes how participants or session files were divided; PCA was fit before model input, and its scope is not reported.
- **Leah's evidence:** "The sample bias problem is addressed by using each of the trials as an input to the learning models." Her note: individual trials were model inputs, and subject-level separation was not reported. The same point about PCA.

**The question for you:** does "each of the trials as an input", with no statement of how trials were split, count as partitioning by epoch (rating: likely), or as not reported (rating: unclear)? The rating changes only through L1. The L5 difference does not affect the rating either way.

Please enter your decision in `disagreement_resolution.csv` (study_id, resolved_rating, resolved_by, date, notes), or reply by email and Kunal will enter it.

## Surface-level disagreements where the overall rating still agreed (for Q19)

These do not change any rating, but they do affect the per-surface figure (Fig. 3, RQ1). Question 19 asks whose code feeds it.

| Surface | Agreement | Studies that differ |
|---|---|---|
| L1 split_unit | 17/18 | S11 |
| L2 connectivity_scope | 18/18 | none |
| L3 threshold_fit | 17/18 | S12 |
| L4 normalization_fit | 15/18 | S10, S13, S14 |
| L5 selection_fit | 12/18 | S06, S09, S10, S11, S16, S18 |

Selection (L5) is where the raters diverged most (surface κ = 0.36). That is worth a sentence in Results (V-C asks which surfaces the disagreements concentrated on).
