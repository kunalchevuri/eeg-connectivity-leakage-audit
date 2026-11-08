# Flag: three included studies come from one research group, on one sample

**Status:** observation for the Discussion (Section VII) and possibly RQ3. Not a problem with any paper.
**Raised:** 2026-09-24.

| Rank | Study | Group | Sample construction |
|---|---|---|---|
| R023 | Dang et al. 2020, *Nonlinear Dynamics* (PLV + multilayer CNN) | Gao / Dang, Tianjin University | Mumtaz dataset, EC + EO, first 180 s, 2-s windows → 5,580 MDD + 5,130 HC samples |
| R086 | Yu, Yang & Dang 2022, *EPL* (mutual information + attention CNN) | Dang | same → 5,580 + 5,130 |
| R104 | Sun et al. 2022, *IEEE TIM* (PLV + GCN) | Gao / Dang, Tianjin University | same → 5,580 + 5,130 |

These are three different models, so this is **not** duplication (compare `FLAG_R089_R092_overlap.md`). But they share
a lab, a dataset, and an identical segmentation and evaluation pipeline, so their pipeline codings are likely to be
identical too.

**Why it matters:** RQ3 compares accuracy across leakage strata with N ≈ 16–18. Three studies with one shared
pipeline act more like one observation than three, and could pull one stratum's median on their own.

**Suggested handling (advisor to confirm):** keep all three — each meets the criteria and each is a separate
published claim — but state the clustering in Section VII, and as a sensitivity check re-run RQ3 with one study
per group. Neither study should be named in the manuscript as an example of anything.

More broadly, several included studies use the same public Mumtaz dataset (R001, R019, R023, R040, R086, R103, R104).
That is expected for this literature and worth one sentence in V-A, since dataset size is the confounder the
blueprint's §8 names.
