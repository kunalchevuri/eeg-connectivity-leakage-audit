# Closest prior work found so far (Phase 2)

Source: PubMed, 8 blueprint queries, run 2026-09-23 through the E-utilities API (`search_log.csv`, `pubmed_results.csv`).
Abstracts are in `closest_items_abstracts_pubmed.txt`. **Kunal must open each original before anything is cited (§12).**

| PMID | Item | What it does | Why it doesn't close our gap |
|---|---|---|---|
| 37789047 | Lee et al., *Sci Rep* 2023, "Risk of data leakage in estimating the diagnostic performance of a deep-learning-based CAD system for psychiatric disorders" (erratum: *Sci Rep* 2024) | Empirical: trial-wise vs subject-wise CV with CNNs on resting EEG in **PTSD**; trial-wise CV inflates accuracy | One dataset and one disorder (not MDD); covers only the partition (**L1**); not a literature audit; doesn't address L2–L5. **Cite as direct evidence for L1.** |
| 38418819 | Rosenblatt et al., *Nat Commun* 2024, "Data leakage inflates prediction performance in connectome-based machine learning models" | Empirical: five leakage forms in **fMRI** connectome models; feature selection and repeated subjects inflate performance most; small samples make it worse | fMRI, not EEG; experiments, not an audit. **Strongest framing source** (the blueprint says fMRI connectivity leakage is a developed literature). Supports L1/L5 and the sample-size confounding point. |
| 42197874 | Ugail et al., *Sensors* 2026, "Subject-wise depression screening from eight-channel resting-state EEG…" | New model built under a subject-wise protocol; states that many EEG results are weakened by segment-level leakage | Not an audit; mainly spectral features and classical ML |
| 34799630 | Yagis et al., *Sci Rep* 2021, "Effect of data leakage in brain MRI classification using 2D CNNs" | Empirical: slice-level splitting inflates CNN accuracy in MRI | MRI, not EEG; an L1 analogue |
| 41449395 | *BMC Psychiatry* 2025, "Systematic review of EEG-based biomarkers for depression, anxiety, and bipolar disorder: trends in XAI" | Review | Focuses on XAI; check whether it covers validation |
| — | Corpus rank 83: Kaur, Aggarwal & Goel, *Neuroscience* 2025 (systematic review, EEG MDD prediction) | Review of pipelines and validation | Check what it audits (split vs pipeline) → Section II-B |
| — | Corpus rank 62: Zhang … Xiang, *Neurosci Biobehav Rev* 2025 (meta-analysis, ML for MDD) | Meta-analysis; validation procedure as a moderator | Audits the split and moderators, not the pre-split pipeline → Section II-B |

**Still to run (Kunal, in a browser):** the same 8 queries in IEEE Xplore, Scopus or Web of Science, and Google Scholar. Log date and hit count in `search_log.csv`. Per the blueprint, stop when two consecutive queries return nothing new.
