"""RQ4 (blueprint Sec 3/8): does reporting completeness vary by publication year, venue type, or
architecture family? Secondary, descriptive, run only after RQ1-RQ3 are complete.
WRITTEN 2026-09-24, BEFORE ANY RATING EXISTED. Changes after coding go in deviations_log.md.

Pre-specified definitions:
  completeness   per study, the number of the five surfaces (L1 split_unit, L2-L5) NOT coded "unclear" (0-5).
  year trend     Spearman rho between publication year and completeness, with a 10,000-resample bootstrap
                 95% CI and no p-value (blueprint: RQ4 is descriptive, CIs rather than p-values).
  year groups    2020-2021 / 2022-2023 / 2024 and later (fixed now).
  venue type     conference if the source title names a conference, symposium, workshop or proceedings;
                 otherwise journal.
  architecture   CNN-family (CNN, LSTM, CNN-LSTM), GNN-family (GCN, GAT), other.
  Any group with fewer than 3 studies is reported as "not estimable", not compared.

    python 05_Phase5_Analysis/rq4.py      (after build_results.py)
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).parent
ROOT = HERE.parent
SEED, N_BOOT, MIN_GROUP = 20260923, 10_000, 3
SURFACES = ["split_unit", "connectivity_scope", "threshold_fit", "normalization_fit", "selection_fit"]
CONF_WORDS = ("CONFERENCE", "SYMPOSIUM", "WORKSHOP", "PROCEEDINGS", "ICASSP", "IJCNN", "EMBC")
ARCH = {"cnn": "CNN-family", "lstm": "CNN-family", "cnn-lstm": "CNN-family", "gcn": "GNN-family", "gat": "GNN-family"}


def wilson(k, n, z=1.959964):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    d = 1 + z ** 2 / n
    c = (p + z ** 2 / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def year_group(y):
    return "2020-2021" if y <= 2021 else "2022-2023" if y <= 2023 else "2024+"


def by_group(df, col):
    rows = []
    for g, d in df.groupby(col):
        n = len(d)
        k = int((d["split_unit"] != "unclear").sum())
        lo, hi = wilson(k, n)
        rows.append({"group": g, "n": n, "estimable": n >= MIN_GROUP,
                     "median_completeness": float(d["completeness"].median()) if n >= MIN_GROUP else None,
                     "prop_split_unit_stated": k / n if n >= MIN_GROUP else None,
                     "ci_low": lo if n >= MIN_GROUP else None, "ci_high": hi if n >= MIN_GROUP else None})
    return rows


def main():
    final = pd.read_csv(ROOT / "04_Phase4_Coding/coding_sheet_FINAL.csv")
    key = pd.read_csv(ROOT / "04_Phase4_Coding/study_id_key_2026-09-23.csv")[["study_id", "wos_rank"]]
    wos = pd.read_csv(ROOT / "03_Phase3_Corpus/screening_log.csv", dtype=str)[["wos_rank", "year", "source"]]
    supp = pd.read_csv(ROOT / "03_Phase3_Corpus/supplementary_records.csv", dtype=str)[["wos_rank", "year", "source"]]
    meta = pd.concat([wos, supp]).drop_duplicates("wos_rank")
    meta["wos_rank"] = meta["wos_rank"].astype(int)
    df = final.merge(key, on="study_id").merge(meta, on="wos_rank", how="left")
    if df["year"].isna().any():
        raise SystemExit(f"no year for: {df.loc[df['year'].isna(), 'study_id'].tolist()}")

    for c in SURFACES:
        df[c] = df[c].astype(str).str.strip().str.lower()
    df["completeness"] = sum((df[c] != "unclear").astype(int) for c in SURFACES)
    df["year"] = df["year"].astype(int)
    df["year_group"] = df["year"].map(year_group)
    df["venue_type"] = df["source"].str.upper().map(
        lambda s: "conference" if any(w in s for w in CONF_WORDS) else "journal")
    df["arch_family"] = df["architecture"].astype(str).str.strip().str.lower().map(ARCH).fillna("other")

    rng = np.random.default_rng(SEED)
    y, c = df["year"].to_numpy(), df["completeness"].to_numpy()
    rho = stats.spearmanr(y, c).statistic
    boots = []
    for _ in range(N_BOOT):
        i = rng.integers(0, len(df), len(df))
        boots.append(stats.spearmanr(y[i], c[i]).statistic)
    lo, hi = np.nanpercentile(boots, [2.5, 97.5])

    out = {"n_studies": len(df),
           "year_trend": {"spearman_rho": rho, "ci_low": lo, "ci_high": hi, "years": [int(y.min()), int(y.max())]},
           "by_year_group": by_group(df, "year_group"),
           "by_venue_type": by_group(df, "venue_type"),
           "by_architecture_family": by_group(df, "arch_family")}
    res = HERE / "results"
    res.mkdir(exist_ok=True)
    (res / "rq4.json").write_text(json.dumps(out, indent=2, default=float))
    print(f"RQ4: rho(year, completeness) = {rho:.2f} [{lo:.2f}, {hi:.2f}], n = {len(df)}")
    for k in ("by_year_group", "by_venue_type", "by_architecture_family"):
        print(k, [(r["group"], r["n"], r["median_completeness"]) for r in out[k]])
    print(f"Wrote {res / 'rq4.json'}")


if __name__ == "__main__":
    main()
