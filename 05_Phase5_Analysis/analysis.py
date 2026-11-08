"""Pre-specified analysis for the connectivity-pipeline leakage audit (blueprint Section 8).

Written 2026-09-23, before any study was coded, so the analysis cannot drift toward
whatever shows an effect. Do not edit the tests after the accuracy column is filled;
any change must be logged in 08_Admin/deviations_log.md with the reason.

Usage:
    python analysis.py --final ../04_Phase4_Coding/coding_sheet_FINAL.csv \
                       --rater-a ../04_Phase4_Coding/rater_A.csv \
                       --rater-b ../04_Phase4_Coding/rater_B.csv \
                       --out results/

RQ1, RQ2 and RQ4 are descriptive: proportions with Wilson 95% CIs, no hypothesis tests.
RQ3 is the only confirmatory analysis: rank-based test, two-sided, with Cliff's delta
and a bootstrap CI. No t-tests. No p-value without its effect size and CI.
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

SEED = 20260923
N_BOOT = 10_000
SESOI = 3.0  # smallest effect of interest, percentage points of median accuracy

RATINGS = ["free", "possible", "likely", "unclear"]
SURFACES = {  # leakage surface -> coding-sheet column (blueprint 7.3)
    "L1 epoch-level partitioning": "split_unit",
    "L2 connectivity estimation scope": "connectivity_scope",
    "L3 threshold selection": "threshold_fit",
    "L4 feature normalization": "normalization_fit",
    "L5 channel/band selection": "selection_fit",
}


def wilson(k, n, z=1.959964):
    """Wilson score 95% CI for a proportion k/n."""
    if n == 0:
        return (np.nan, np.nan, np.nan)
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return (p, max(0.0, centre - half), min(1.0, centre + half))


def proportions(series, categories=None):
    s = series.astype(str).str.strip().str.lower()
    n = len(s)
    cats = categories or sorted(s.unique())
    rows = []
    for c in cats:
        k = int((s == c).sum())
        p, lo, hi = wilson(k, n)
        rows.append({"category": c, "k": k, "n": n, "prop": p, "ci_low": lo, "ci_high": hi})
    return pd.DataFrame(rows)


def cohen_kappa(a, b, labels):
    a, b = np.asarray(a), np.asarray(b)
    n = len(a)
    po = np.mean(a == b)
    pe = sum(np.mean(a == c) * np.mean(b == c) for c in labels)
    kappa = (po - pe) / (1 - pe) if pe < 1 else np.nan
    return po, pe, kappa


def cliffs_delta(x, y):
    """P(X > Y) - P(X < Y); x = leakage-likely, y = leakage-free."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    gt = (x[:, None] > y[None, :]).sum()
    lt = (x[:, None] < y[None, :]).sum()
    return (gt - lt) / (len(x) * len(y))


def bootstrap_ci(fn, *samples, rng):
    vals = []
    for _ in range(N_BOOT):
        resampled = [s[rng.integers(0, len(s), len(s))] for s in samples]
        vals.append(fn(*resampled))
    return np.nanpercentile(vals, [2.5, 97.5])


def rq1(final):
    out = {"overall_rating": proportions(final["leakage_rating"], RATINGS)}
    for name, col in SURFACES.items():
        out[name] = proportions(final[col])
    return out


def rq2(ra, rb, rng):
    m = ra[["study_id", "leakage_rating"]].merge(
        rb[["study_id", "leakage_rating"]], on="study_id", suffixes=("_a", "_b"))
    a = m["leakage_rating_a"].str.strip().str.lower().to_numpy()
    b = m["leakage_rating_b"].str.strip().str.lower().to_numpy()
    po, pe, k = cohen_kappa(a, b, RATINGS)
    # CI by bootstrap over studies (resampling paired ratings)
    idx = np.arange(len(a))
    boots = []
    for _ in range(N_BOOT):
        i = rng.choice(idx, len(idx), replace=True)
        boots.append(cohen_kappa(a[i], b[i], RATINGS)[2])
    lo, hi = np.nanpercentile(boots, [2.5, 97.5])
    return {"n_studies": len(a), "percent_agreement": po, "p_expected": pe,
            "kappa": k, "kappa_ci_low": lo, "kappa_ci_high": hi,
            "below_0.4_stop_rule": bool(k < 0.4)}


def rq3(final, rng):
    df = final.copy()
    df["leakage_rating"] = df["leakage_rating"].str.strip().str.lower()
    df["accuracy"] = pd.to_numeric(df["accuracy"], errors="coerce")
    df = df.dropna(subset=["accuracy"])

    strata = []
    for r in RATINGS:
        acc = df.loc[df["leakage_rating"] == r, "accuracy"]
        strata.append({"rating": r, "n": len(acc),
                       "median": acc.median() if len(acc) else np.nan,
                       "q1": acc.quantile(0.25) if len(acc) else np.nan,
                       "q3": acc.quantile(0.75) if len(acc) else np.nan})
    strata = pd.DataFrame(strata)

    likely = df.loc[df["leakage_rating"] == "likely", "accuracy"].to_numpy()
    free = df.loc[df["leakage_rating"] == "free", "accuracy"].to_numpy()
    res = {"strata": strata}
    if len(likely) and len(free):
        u = stats.mannwhitneyu(likely, free, alternative="two-sided")
        d = cliffs_delta(likely, free)
        d_lo, d_hi = bootstrap_ci(cliffs_delta, likely, free, rng=rng)
        med_diff = np.median(likely) - np.median(free)
        md_lo, md_hi = bootstrap_ci(lambda x, y: np.median(x) - np.median(y), likely, free, rng=rng)
        res["likely_vs_free"] = {
            "n_likely": len(likely), "n_free": len(free),
            "mann_whitney_U": u.statistic, "p_two_sided": u.pvalue,
            "cliffs_delta": d, "cliffs_delta_ci": [d_lo, d_hi],
            "median_diff_pp": med_diff, "median_diff_ci": [md_lo, md_hi],
            # Falsification rule: medians within 3 points -> report a null. No subgroup search.
            "within_SESOI_report_null": bool(abs(med_diff) < SESOI),
        }
    else:
        res["likely_vs_free"] = "not estimable: a stratum is empty"

    groups = [df.loc[df["leakage_rating"] == r, "accuracy"].to_numpy() for r in RATINGS]
    groups = [g for g in groups if len(g) > 0]
    if len(groups) > 2:
        kw = stats.kruskal(*groups)
        res["kruskal_wallis_all_strata"] = {"H": kw.statistic, "p": kw.pvalue, "k_groups": len(groups)}
    return res


def confounding(final):
    """Accuracy by rating stratified by sample-size tercile (blueprint 8, mandatory)."""
    df = final.copy()
    df["leakage_rating"] = df["leakage_rating"].str.strip().str.lower()
    df["accuracy"] = pd.to_numeric(df["accuracy"], errors="coerce")
    df["n_subjects"] = pd.to_numeric(df["n_subjects"], errors="coerce")
    df = df.dropna(subset=["n_subjects"])
    df["size_tercile"] = pd.qcut(df["n_subjects"], 3, labels=["small", "medium", "large"], duplicates="drop")
    rating_by_size = pd.crosstab(df["size_tercile"], df["leakage_rating"])
    acc_by_both = (df.dropna(subset=["accuracy"])
                     .groupby(["size_tercile", "leakage_rating"], observed=True)["accuracy"]
                     .agg(["count", "median"]).reset_index())
    return {"rating_by_size_tercile": rating_by_size, "median_accuracy_by_tercile_and_rating": acc_by_both}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--final", required=True)
    ap.add_argument("--rater-a")
    ap.add_argument("--rater-b")
    ap.add_argument("--out", default="results")
    args = ap.parse_args()

    rng = np.random.default_rng(SEED)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    final = pd.read_csv(args.final)

    for name, table in rq1(final).items():
        table.to_csv(out / f"rq1_{name.split()[0].lower()}.csv", index=False)

    summary = {}
    if args.rater_a and args.rater_b:
        summary["rq2"] = rq2(pd.read_csv(args.rater_a), pd.read_csv(args.rater_b), rng)

    r3 = rq3(final, rng)
    r3["strata"].to_csv(out / "rq3_accuracy_by_rating.csv", index=False)
    summary["rq3"] = {k: v for k, v in r3.items() if k != "strata"}

    conf = confounding(final)
    conf["rating_by_size_tercile"].to_csv(out / "confounding_rating_by_size_tercile.csv")
    conf["median_accuracy_by_tercile_and_rating"].to_csv(out / "confounding_accuracy_by_tercile.csv", index=False)

    (out / "summary.json").write_text(json.dumps(summary, indent=2, default=float))
    print(json.dumps(summary, indent=2, default=float))


if __name__ == "__main__":
    main()
