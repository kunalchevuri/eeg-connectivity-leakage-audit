"""POST HOC analyses added for the MLESP 2026 camera-ready, in response to the reviewers.

WRITTEN 2026-11-07, AFTER the ratings and accuracies were known. These are therefore NOT part of the
pre-specified analysis plan of analysis.py / sensitivity.py / rq4.py, and every number produced here must be
labelled in the paper as post hoc and reviewer-requested. Logged in 08_Admin/deviations_log.md.
Nothing here changes a coded field, a rating, or any pre-specified result.

What each block answers:

  A. not_reported_bound   Reviewer 1 (all three points) and Reviewer 2 (W6, Q4): "a step that is never
     mentioned was coded not performed, which is not the same as not reported". We cannot separate the two
     readings from the coded fields, because the rater sheets record one value ("none") for both. So we
     compute the WORST CASE: every "none" on L3/L4/L5 is re-read as "unclear" and the ratings are re-derived
     with the unchanged rule imported from score_ratings.py. This bounds how far the convention can inflate
     the leakage-free count.

  B. per_surface_agreement   Reviewer 2 (W4, Q3): the overall kappa is dominated by the common decisions.
     Per-surface percentage agreement and unweighted Cohen's kappa with a 10,000-resample bootstrap CI over
     studies, plus an explicit stability flag. Where a surface has no variation, kappa is undefined (the
     expected-agreement term is 1); we say so rather than printing a number.

  C. clustering   Reviewer 2 (W8, Q6): studies share datasets and research groups, so they are not
     independent. Three views: (1) counts per dataset; (2) a cluster bootstrap that resamples DATASETS (and
     separately GROUPS) rather than studies, which widens the interval for the prevalence figures;
     (3) the exact range of each prevalence over every possible one-study-per-cluster selection.

  D. rq4_exact   Reviewer 2 (W9): a Spearman rho from 18 studies is imprecise. A permutation test for the
     rank correlation and a Fisher exact test on dichotomised completeness. Reported as a hypothesis, not a
     finding. A Firth-penalised logistic regression is NOT run: with 18 observations and this few
     incomplete-reporting events it would not be better identified than the exact test.

    python 05_Phase5_Analysis/reviewer_response.py      (after run_pipeline.py)
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "04_Phase4_Coding"))
from score_ratings import apply_rules          # the UNCHANGED pre-specified rating rule

SEED, N_BOOT = 20260923, 10_000
RATINGS = ["free", "possible", "likely", "unclear"]
SURFACES = {
    "L1": "split_unit",
    "L2": "connectivity_scope",
    "L3": "threshold_fit",
    "L4": "normalization_fit",
    "L5": "selection_fit",
}
RECODED = ["threshold_fit", "normalization_fit", "selection_fit"]   # L3-L5: where "none" is ambiguous
MIN_MINORITY = 3   # a surface with fewer than this many non-modal codes is flagged unstable


def norm(s):
    return s.astype(str).str.strip().str.lower()


def kappa_ci(a, b, labels, rng):
    """Unweighted Cohen's kappa with a bootstrap CI over studies. Same method as analysis.rq2."""
    def k(x, y):
        po = np.mean(x == y)
        pe = sum(np.mean(x == c) * np.mean(y == c) for c in labels)
        return (po - pe) / (1 - pe) if pe < 1 else np.nan
    po = float(np.mean(a == b))
    point = k(a, b)
    idx = np.arange(len(a))
    boots = np.asarray([k(a[i], b[i]) for i in
                        (rng.choice(idx, len(idx), replace=True) for _ in range(N_BOOT))], float)
    finite = boots[np.isfinite(boots)]
    lo, hi = (np.percentile(finite, [2.5, 97.5]) if len(finite) else (np.nan, np.nan))
    return po, point, float(lo), float(hi), int(len(finite))


# ---------------------------------------------------------------- A. not reported vs not performed
def not_reported_bound(final):
    df = final.copy()
    for c in SURFACES.values():
        df[c] = norm(df[c])
    before = df["leakage_rating"].value_counts().reindex(RATINGS).fillna(0).astype(int)

    strict = df.copy()
    n_cells = 0
    for c in RECODED:
        n_cells += int((strict[c] == "none").sum())
        strict[c] = strict[c].replace("none", "unclear")
    strict["rating_strict"] = strict.apply(apply_rules, axis=1)
    after = strict["rating_strict"].value_counts().reindex(RATINGS).fillna(0).astype(int)

    changed = strict.loc[strict["rating_strict"] != df["leakage_rating"],
                         ["study_id", "leakage_rating", "rating_strict"]]
    return {
        "what": "every none on L3-L5 re-read as unclear (worst case); L1 and L2 untouched",
        "n_none_cells_recoded": n_cells,
        "n_studies_with_any_none": int((df[RECODED] == "none").any(axis=1).sum()),
        "rating_before": before.to_dict(),
        "rating_after": after.to_dict(),
        "n_free_before": int(before["free"]),
        "n_free_after": int(after["free"]),
        "n_likely_before": int(before["likely"]),
        "n_likely_after": int(after["likely"]),
        "n_studies_rating_changed": int(len(changed)),
        "studies_changed": changed.to_dict("records"),
        "pct_epoch_unchanged": bool((df["split_unit"] == "epoch").sum()
                                    == (strict["split_unit"] == "epoch").sum()),
    }


# ---------------------------------------------------------------- B. per-surface agreement
def per_surface_agreement(ra, rb, rng):
    cols = list(SURFACES.values())
    m = ra[["study_id"] + cols].merge(rb[["study_id"] + cols], on="study_id", suffixes=("_a", "_b"))
    rows = []
    for tag, col in SURFACES.items():
        a, b = norm(m[col + "_a"]).to_numpy(), norm(m[col + "_b"]).to_numpy()
        labels = sorted(set(a) | set(b))
        counts = pd.Series(np.concatenate([a, b])).value_counts()
        minority = int(counts.iloc[1:].sum()) if len(counts) > 1 else 0
        po, k, lo, hi, _ = kappa_ci(a, b, labels, rng)
        no_variation = len(labels) == 1
        defined = (not no_variation) and bool(np.isfinite(k))
        rows.append({
            "surface": tag, "column": col, "n_studies": int(len(a)),
            "n_agree": int((a == b).sum()), "percent_agreement": po,
            "kappa": float(k) if defined else None,
            "kappa_ci_low": lo if defined else None,
            "kappa_ci_high": hi if defined else None,
            "n_categories_observed": len(labels), "categories": labels,
            "n_non_modal_codes": minority,
            "kappa_defined": defined,
            "stable": bool(defined and minority >= MIN_MINORITY),
            "note": ("no variation: every code identical, so expected agreement is 1 and kappa is undefined"
                     if no_variation else
                     "unstable: too few non-modal codes to estimate kappa reliably" if minority < MIN_MINORITY
                     else "estimable"),
        })
    return rows


# ---------------------------------------------------------------- C. clustering by dataset / group
def cluster_bootstrap(labels, flags, rng):
    """Resample CLUSTERS with replacement; recompute the proportion over the pooled studies."""
    clusters = {c: flags[labels == c] for c in np.unique(labels)}
    keys = list(clusters)
    vals = []
    for _ in range(N_BOOT):
        pick = rng.choice(len(keys), len(keys), replace=True)
        vals.append(np.concatenate([clusters[keys[i]] for i in pick]).mean())
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return float(lo), float(hi)


def one_per_cluster_range(labels, flags):
    """Exact min and max of the proportion over every one-study-per-cluster selection."""
    per = [flags[labels == c] for c in np.unique(labels)]
    n = len(per)
    lo = sum(1 for g in per if g.all()) / n      # forced to pick a positive only where all are positive
    hi = sum(1 for g in per if g.any()) / n
    return {"n_clusters": n, "min": float(lo), "max": float(hi)}


def clustering(final, groups, rng):
    df = final.copy()
    for c in SURFACES.values():
        df[c] = norm(df[c])
    df["epoch"] = (df["split_unit"] == "epoch").to_numpy()
    df["unclear_any"] = (df[["connectivity_scope", "threshold_fit",
                             "normalization_fit", "selection_fit"]] == "unclear").any(axis=1).to_numpy()

    # research-group clusters: the studies in research_groups.csv form one cluster, every other study its own
    key = pd.read_csv(ROOT / "04_Phase4_Coding/study_id_key_2026-09-23.csv")[["study_id", "wos_rank"]]
    gmap = dict(zip(groups["wos_rank"], groups["group_id"]))
    df = df.merge(key, on="study_id", how="left")
    df["group"] = [gmap.get(r, "solo_" + str(s)) for s, r in zip(df["study_id"], df["wos_rank"])]

    out = {"per_dataset": [], "by_cluster": {}}
    for ds, d in df.groupby("dataset"):
        out["per_dataset"].append({
            "dataset": ds, "n_studies": int(len(d)),
            "n_epoch_level": int(d["epoch"].sum()),
            "n_unclear_any": int(d["unclear_any"].sum()),
            "ratings": d["leakage_rating"].value_counts().to_dict(),
        })
    for unit, col in (("dataset", "dataset"), ("research_group", "group")):
        labels = df[col].to_numpy()
        block = {"n_clusters": int(pd.unique(labels).size)}
        for metric in ("epoch", "unclear_any"):
            flags = df[metric].to_numpy()
            lo, hi = cluster_bootstrap(labels, flags, rng)
            block[metric] = {
                "proportion_all_studies": float(flags.mean()),
                "cluster_bootstrap_ci": [lo, hi],
                "one_per_cluster_range": one_per_cluster_range(labels, flags),
            }
        out["by_cluster"][unit] = block
    return out


# ---------------------------------------------------------------- D. RQ4 exact tests
def rq4_exact(final):
    key = pd.read_csv(ROOT / "04_Phase4_Coding/study_id_key_2026-09-23.csv")[["study_id", "wos_rank"]]
    wos = pd.read_csv(ROOT / "03_Phase3_Corpus/screening_log.csv", dtype=str)[["wos_rank", "year"]]
    supp = pd.read_csv(ROOT / "03_Phase3_Corpus/supplementary_records.csv", dtype=str)[["wos_rank", "year"]]
    meta = pd.concat([wos, supp]).drop_duplicates("wos_rank")
    meta["wos_rank"] = meta["wos_rank"].astype(int)
    df = final.merge(key, on="study_id").merge(meta, on="wos_rank", how="left")
    if df["year"].isna().any():
        raise SystemExit("no year for: " + str(df.loc[df["year"].isna(), "study_id"].tolist()))
    df["year"] = df["year"].astype(int)
    # completeness: exactly the pre-specified definition in rq4.py
    for c in SURFACES.values():
        df[c] = norm(df[c])
    df["completeness"] = (df[list(SURFACES.values())] != "unclear").sum(axis=1)

    rho = stats.spearmanr(df["year"], df["completeness"])
    perm = stats.permutation_test(
        (df["year"].to_numpy(float), df["completeness"].to_numpy(float)),
        lambda x, y: stats.spearmanr(x, y).statistic,
        permutation_type="pairings", n_resamples=N_BOOT, alternative="two-sided",
        random_state=np.random.default_rng(SEED))

    df["recent"] = df["year"] >= 2024
    df["incomplete"] = df["completeness"] < 5
    table = (pd.crosstab(df["recent"], df["incomplete"])
             .reindex(index=[False, True], columns=[False, True]).fillna(0).astype(int))
    fisher = stats.fisher_exact(table.to_numpy(), alternative="two-sided")
    return {
        "n_studies": int(len(df)),
        "spearman_rho": float(rho.statistic),
        "permutation_p_two_sided": float(perm.pvalue),
        "n_resamples": N_BOOT,
        "dichotomised": {
            "definition": "recent = year >= 2024; incomplete = fewer than 5 of 5 surfaces reported",
            "n_recent": int(df["recent"].sum()),
            "n_incomplete": int(df["incomplete"].sum()),
            "table_recent_by_incomplete": {str(k): {str(k2): int(v2) for k2, v2 in v.items()}
                                           for k, v in table.to_dict().items()},
            "odds_ratio": float(fisher.statistic),
            "fisher_p_two_sided": float(fisher.pvalue),
        },
        "firth_logistic": "not run: 18 observations and too few incomplete-reporting events for a penalised "
                          "regression to be better identified than the exact test above",
    }


def main():
    rng = np.random.default_rng(SEED)
    final = pd.read_csv(ROOT / "04_Phase4_Coding/coding_sheet_FINAL.csv")
    ra = pd.read_csv(ROOT / "04_Phase4_Coding/rater_A_scored.csv")
    rb = pd.read_csv(ROOT / "04_Phase4_Coding/rater_B_scored.csv")
    groups = pd.read_csv(HERE / "research_groups.csv")

    out = {
        "_provenance": {
            "status": "POST HOC, added for the camera-ready in response to the reviewers",
            "written": "2026-11-07",
            "not_part_of": "the pre-specified analysis plan (analysis.py, sensitivity.py, rq4.py)",
            "seed": SEED, "n_boot": N_BOOT,
            "rating_rule": "unchanged, imported from 04_Phase4_Coding/score_ratings.py",
        },
        "A_not_reported_bound": not_reported_bound(final),
        "B_per_surface_agreement": per_surface_agreement(ra, rb, rng),
        "C_clustering": clustering(final, groups, rng),
        "D_rq4_exact": rq4_exact(final),
    }
    res = HERE / "results"
    res.mkdir(exist_ok=True)
    (res / "reviewer_response.json").write_text(json.dumps(out, indent=2, default=float), encoding="utf-8")
    print(json.dumps(out, indent=2, default=float))


if __name__ == "__main__":
    main()
