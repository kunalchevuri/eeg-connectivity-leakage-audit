"""Apply the blueprint's §7.4 decision rules mechanically to coded fields, producing
leakage_rating for each rater, then merge into coding_sheet_FINAL.csv.

Rules (blueprint §7.4), applied in this order (first match wins):
  1. unclear      - split_unit is "unclear"
  2. likely       - split_unit == "epoch", OR any of L2-L5 == "whole-dataset"
  3. free         - split_unit == "subject" AND connectivity_scope == "within-fold"
                    AND threshold_fit, normalization_fit AND selection_fit all in {within-fold, none}
                    (ADVISOR RULING 2026-09-24, Q5: L5 belongs in the "free" definition; its omission from the
                    blueprint was an error. Before this ruling L5 was not required - deviations_log.md.)
  4. possible     - split_unit == "subject" but not all of L2-L5 are within-fold/none (i.e., any is "unclear")

This is a mechanical implementation of a genuinely ambiguous rule (see 08_Admin/advisor_questions.md,
questions 5-6, both answered 2026-09-24: Q5 adds L5 to 'free'; Q6 confirms 'likely' takes precedence). Do not hand-edit ratings; edit the
rule and rerun.

Usage:
    python score_ratings.py --a rater_A_Kunal_<date>.xlsx --b rater_B_Leah_<date>.xlsx --out ../04_Phase4_Coding
"""
import argparse
import sys
from pathlib import Path

import pandas as pd


def apply_rules(row):
    su = str(row.get("split_unit", "")).strip().lower()
    l2 = str(row.get("connectivity_scope", "")).strip().lower()
    l3 = str(row.get("threshold_fit", "")).strip().lower()
    l4 = str(row.get("normalization_fit", "")).strip().lower()
    l5 = str(row.get("selection_fit", "")).strip().lower()

    if su in ("", "unclear", "nan"):
        return "unclear"
    if su == "epoch" or "whole-dataset" in (l2, l3, l4, l5):
        return "likely"
    ok_fit = lambda v: v in ("within-fold", "none")
    if su == "subject" and l2 == "within-fold" and ok_fit(l3) and ok_fit(l4) and ok_fit(l5):
        return "free"
    if su == "subject":
        return "possible"
    return "unclear"


def read_rate_sheet(paths):
    """Read one or more workbooks for a rater (e.g. the main file plus an addendum) into one table."""
    frames = []
    for path in paths:
        frames.append(pd.read_excel(path, sheet_name="Rate" if "Rate" in pd.ExcelFile(path).sheet_names else "Code"))
    df = pd.concat(frames, ignore_index=True)
    dup = df["study_id"][df["study_id"].duplicated()].tolist()
    if dup:
        raise SystemExit(f"study_id appears in more than one file for the same rater: {dup}")
    df["leakage_rating"] = df.apply(apply_rules, axis=1)
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True, nargs="+", help="Rater A workbook(s) (Kunal)")
    ap.add_argument("--b", required=True, nargs="+", help="Rater B workbook(s) (Leah): main file plus any addendum")
    ap.add_argument("--out", default=".")
    args = ap.parse_args()

    a = read_rate_sheet(args.a)
    b = read_rate_sheet(args.b)
    a["rater"] = "KC"
    b["rater"] = "LI"
    missing = sorted(set(a["study_id"]) ^ set(b["study_id"]))
    if missing:
        raise SystemExit(f"Raters did not code the same studies (blueprint 7.4 requires both to code every study): {missing}")

    out = Path(args.out)
    a.to_csv(out / "rater_A_scored.csv", index=False)
    b.to_csv(out / "rater_B_scored.csv", index=False)

    m = a[["study_id", "leakage_rating"]].merge(
        b[["study_id", "leakage_rating"]], on="study_id", suffixes=("_a", "_b"))
    m["agree"] = m.leakage_rating_a == m.leakage_rating_b
    n_dis = (~m.agree).sum()
    print(f"{len(m)} studies scored. Agreement before resolution: {m.agree.mean():.1%} "
          f"({n_dis} disagreement{'s' if n_dis != 1 else ''}).")
    if n_dis:
        print("\nDisagreements (resolve with the advisor as tiebreaker; keep this pre-resolution table):")
        print(m[~m.agree].to_string(index=False))
    m.to_csv(out / "agreement_pre_resolution.csv", index=False)
    print(f"\nWrote rater_A_scored.csv, rater_B_scored.csv, agreement_pre_resolution.csv in {out}/")
    print("Next: resolve disagreements with the advisor, build coding_sheet_FINAL.csv "
          "(keep both pre- and post-resolution rating columns), then run "
          "05_Phase5_Analysis/analysis.py --final coding_sheet_FINAL.csv --rater-a rater_A_scored.csv --rater-b rater_B_scored.csv")


if __name__ == "__main__":
    main()
