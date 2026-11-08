# Phase 2 — the three databases that need you, not me

**Updated 2026-09-23.** PubMed is done (8/8). OpenAlex and Semantic Scholar were run as substitutes
and are logged as such in `search_log.csv`. Three databases still need a human session:

| Database | Why I can't | What you do |
|---|---|---|
| IEEE Xplore | Needs a subscribed session; blocks scripts | GMU library → IEEE Xplore → paste each string below |
| Scopus / Web of Science | Same | GMU library → Scopus → paste each string |
| Google Scholar | Blocks all automated access by design | scholar.google.com → paste each string |

For each: record **hit count**, the **date**, and whether anything is *an audit of connectivity-pipeline
leakage in EEG depression deep learning*. That last column is the one that matters — it is the gap claim.
Then paste the numbers into `search_log.csv`, or send them to me and I'll enter them.

## The 8 strings (blueprint §6)

**IEEE Xplore** — paste into the *Command Search* box (not the basic one):

1. `("All Metadata":"data leakage" OR "All Metadata":"information leakage") AND "All Metadata":EEG AND "All Metadata":connectivity`
2. `"All Metadata":"connectivity matrix" AND "All Metadata":EEG AND ("All Metadata":"cross-validation" OR "All Metadata":"train test split") AND "All Metadata":leakage`
3. `("All Metadata":"leave-one-subject-out" OR "All Metadata":"subject-independent") AND "All Metadata":EEG AND "All Metadata":connectivity AND "All Metadata":depression`
4. `"All Metadata":EEG AND "All Metadata":"functional connectivity" AND "All Metadata":depression AND "All Metadata":review AND "All Metadata":validation`
5. `"All Metadata":EEG AND "All Metadata":connectivity AND ("All Metadata":"reporting checklist" OR "All Metadata":"reporting standards" OR "All Metadata":reproducibility)`
6. `"All Metadata":EEG AND "All Metadata":depression AND "All Metadata":classification AND ("All Metadata":revisited OR "All Metadata":replication OR "All Metadata":overestimated)`
7. `"All Metadata":"machine learning" AND "All Metadata":neuroimaging AND "All Metadata":"data leakage"`
8. `"All Metadata":"graph neural network" AND "All Metadata":EEG AND "All Metadata":depression AND ("All Metadata":generalization OR "All Metadata":leakage)`

**Scopus** — paste into Advanced Search:

1. `TITLE-ABS-KEY(("data leakage" OR "information leakage") AND EEG AND connectivity)`
2. `TITLE-ABS-KEY("connectivity matrix" AND EEG AND ("cross-validation" OR "train test split") AND leakage)`
3. `TITLE-ABS-KEY(("leave-one-subject-out" OR "subject-independent") AND EEG AND connectivity AND depression)`
4. `TITLE-ABS-KEY(EEG AND "functional connectivity" AND depression AND review AND validation)`
5. `TITLE-ABS-KEY(EEG AND connectivity AND ("reporting checklist" OR "reporting standards" OR reproducibility))`
6. `TITLE-ABS-KEY(EEG AND depression AND classification AND (revisited OR replication OR overestimat*))`
7. `TITLE-ABS-KEY("machine learning" AND neuroimaging AND "data leakage")`
8. `TITLE-ABS-KEY("graph neural network" AND EEG AND depression AND (generalization OR leakage))`

**Google Scholar** — paste as-is, and only read the first 2 pages:

1. `"data leakage" EEG connectivity`
2. `"connectivity matrix" EEG leakage cross-validation`
3. `"leave-one-subject-out" EEG connectivity depression`
4. `EEG "functional connectivity" depression review validation`
5. `EEG connectivity "reporting standards" reproducibility`
6. `EEG depression classification replication overestimated`
7. `"machine learning" neuroimaging "data leakage"`
8. `"graph neural network" EEG depression leakage`

## What the substitute runs already found

The gap holds. Nothing in OpenAlex, PubMed or Semantic Scholar is an audit of connectivity-pipeline
leakage in EEG-based depression deep learning. The closest remains Rosenblatt et al. 2024
(*Nat Commun*, connectome-based ML, fMRI not EEG) — already in `closest_prior_art.md`.

**One new item to check before you write Section II-C:**
*"Are AI Neuroimaging Models Ready for Clinical Use? A Systematic Methodological Review"* (2026),
`10.3390/jcm15093441`. Open access. It is a methodological review of neuroimaging AI and may overlap
the framing. Read it and add it to `closest_prior_art.md` either way.
