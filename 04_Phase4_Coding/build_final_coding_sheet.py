"""Merge scored ratings into coding_sheet_FINAL.csv (blueprint Section 8 input).

Run this AFTER score_ratings.py and AFTER every disagreement it reports has been
resolved with the advisor as tiebreaker (blueprint 7.4). This script never guesses a
resolution: any disagreement missing from disagreement_resolution.csv stops the run.

Descriptive fields (accuracy, n_subjects, dataset, ...) are not coded by Leah (she only
codes the five leakage columns), so they are taken from rater A's sheet, which coded the
full field set. AI never fills leakage_rating or evidence_quote here - only rearranges
what the two raters and the advisor's tiebreak already produced.

RQ1 (Section V-B) needs the raw per-surface codes (split_unit, connectivity_scope,
threshold_fit, normalization_fit, selection_fit), not just the aggregate leakage_rating.
Only the aggregate rating goes through advisor tiebreak here, so the per-surface columns
are taken from rater A's sheet too, same as the other descriptive fields - NOT a resolved
consensus. This is logged in 08_Admin/deviations_log.md and flagged for the advisor
(no per-surface tiebreak process exists yet); the two *_scored.csv files still preserve
both raters' independent per-surface codes if a different rule is needed later.

Q16 RECODE (advisor ruling 2026-09-24): if apply_recode.py has produced rater_*_scored_recoded.csv and
agreement_recoded.csv, those are used for the final rating, the surface codes and the tiebreak list, and
the initial pass is kept as leakage_rating_initial (for the rule-(a) sensitivity analysis, S4). A study that
disagrees in both passes can take a different resolution per pass: disagreement_resolution.csv may carry an
optional column "pass" = initial | recode | both (blank means both).

Usage (from 04_Phase4_Coding):
    python score_ratings.py --a rater_A_Kunal_2026-09-23.xlsx \
                             --b rater_B_Leah_2026-09-23.xlsx rater_B_Leah_ADDENDUM_2026-09-24.xlsx
    python build_final_coding_sheet.py
"""
import argparse
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
DESCRIPTIVE_FIELDS = ["citation", "doi", "dataset", "n_subjects", "n_mdd", "n_control",
                       "connectivity_measure", "frequency_bands", "architecture", "epoching",
                       "epochs_per_subject", "split_strategy", "accuracy", "accuracy_abstract", "other_metrics"]
# Raw per-surface codes for RQ1 - from rater A's sheet only (see docstring: not a resolved consensus).
SURFACE_FIELDS = ["split_unit", "connectivity_scope", "threshold_fit", "normalization_fit", "selection_fit"]


def main():
    ap = argparse.ArgumentParser()
    recoded = (HERE / "agreement_recoded.csv").exists()
    ap.add_argument("--a-scored", default="rater_A_scored_recoded.csv" if recoded else "rater_A_scored.csv")
    ap.add_argument("--b-scored", default="rater_B_scored_recoded.csv" if recoded else "rater_B_scored.csv")
    ap.add_argument("--agreement", default="agreement_recoded.csv" if recoded else "agreement_pre_resolution.csv")
    ap.add_argument("--agreement-initial", default="agreement_pre_resolution.csv")
    ap.add_argument("--resolution", default="disagreement_resolution.csv")
    ap.add_argument("--out", default="coding_sheet_FINAL.csv")
    args = ap.parse_args()

    for f in (args.a_scored, args.b_scored, args.agreement):
        if not (HERE / f).exists():
            raise SystemExit(f"{f} not found - run score_ratings.py first.")

    a = pd.read_csv(HERE / args.a_scored)
    b = pd.read_csv(HERE / args.b_scored)
    agree = pd.read_csv(HERE / args.agreement)
    agree_init = pd.read_csv(HERE / args.agreement_initial)
    print(f"Using {args.a_scored}, {args.b_scored}, {args.agreement}")

    disagreements = sorted(set(agree.loc[~agree["agree"], "study_id"]) | set(agree_init.loc[~agree_init["agree"], "study_id"]))
    resolved = {}
    if disagreements:
        res_path = HERE / args.resolution
        if not res_path.exists():
            raise SystemExit(
                f"{len(disagreements)} disagreement(s) need advisor resolution but "
                f"{args.resolution} does not exist yet: {disagreements}\n"
                f"Create it with columns study_id,resolved_rating,resolved_by,date,notes "
                f"(one row per study_id above), then rerun.")
        res = pd.read_csv(res_path)
        missing = sorted(set(disagreements) - set(res["study_id"]))
        if missing:
            raise SystemExit(
                f"{args.resolution} exists but is missing a resolution for: {missing}\n"
                f"Every disagreement must be resolved before coding_sheet_FINAL.csv can be built.")
        bad = res.loc[~res["resolved_rating"].str.strip().str.lower().isin(
            ["free", "possible", "likely", "unclear"]), "study_id"].tolist()
        if bad:
            raise SystemExit(f"resolved_rating must be one of free/possible/likely/unclear, "
                              f"got something else for: {bad}")
        if "pass" not in res.columns:
            res["pass"] = "both"
        res["pass"] = res["pass"].fillna("both").astype(str).str.strip().str.lower().replace("", "both")
        for _, r in res.iterrows():
            for p in (["initial", "recode"] if r["pass"] == "both" else [r["pass"]]):
                resolved[(r["study_id"], p)] = r["resolved_rating"].strip().lower()

    def settle(tab, pass_name):
        tab = tab.set_index("study_id")
        rating, src = {}, {}
        for sid in tab.index:
            if tab.loc[sid, "agree"]:
                rating[sid], src[sid] = tab.loc[sid, "leakage_rating_a"], "agreement"
            elif (sid, pass_name) in resolved:
                rating[sid], src[sid] = resolved[(sid, pass_name)], "advisor_tiebreak"
            else:
                raise SystemExit(f"{sid} disagrees in the {pass_name} pass but has no resolution for that pass.")
        return tab, rating, src

    agree, final_rating, source = settle(agree, "recode" if args.agreement != args.agreement_initial else "initial")
    _, initial_rating, _ = settle(agree_init, "initial")

    desc = a.set_index("study_id")
    wanted = DESCRIPTIVE_FIELDS + SURFACE_FIELDS
    keep = [c for c in wanted if c in desc.columns]
    if len(keep) < len(wanted):
        missing_cols = sorted(set(wanted) - set(keep))
        print(f"warning: rater A sheet is missing columns (left blank): {missing_cols}")
    out = desc[keep].copy()
    out["leakage_rating"] = pd.Series(final_rating)
    out["rating_source"] = pd.Series(source)
    out["leakage_rating_a"] = agree["leakage_rating_a"]
    out["leakage_rating_b"] = agree["leakage_rating_b"]
    out["leakage_rating_initial"] = pd.Series(initial_rating)   # abstract-protocol pass: sensitivity S4
    if "recoded" in a.columns:
        out["recoded"] = a.set_index("study_id")["recoded"]
        out["protocol_coded"] = a.set_index("study_id")["protocol_coded"]
    out = out.reset_index().rename(columns={"index": "study_id"})

    # Q20 (task type): every study keeps its recorded accuracy in accuracy_all_tasks; if the advisor rules that
    # primary RQ3 uses binary depression-vs-control tasks only, `accuracy` is blanked for the other tasks so every
    # downstream script (analysis.py, Fig. 4, sensitivity S1/S3/S4) uses the primary set without further edits.
    import json
    rulings = json.loads((HERE.parent / "05_Phase5_Analysis/advisor_rulings.json").read_text(encoding="utf-8"))
    key = pd.read_csv(HERE / "study_id_key_2026-09-23.csv")[["study_id", "wos_rank"]]
    tasks = pd.read_csv(HERE.parent / "05_Phase5_Analysis/task_type.csv")[["wos_rank", "task_type"]]
    tt = key.merge(tasks, on="wos_rank", how="left").set_index("study_id")["task_type"].fillna("binary")
    out["task_type"] = out["study_id"].map(tt)
    if "accuracy" in out.columns:
        out["accuracy_all_tasks"] = out["accuracy"]
        q20 = rulings.get("q20_binary_only_primary")
        if q20 is None:
            print("NOTE: advisor Q20 not yet ruled - primary RQ3 uses every task (pre-specified default).")
        elif q20:
            nb = out["task_type"] != "binary"
            out.loc[nb, "accuracy"] = float("nan")
            print(f"Q20 ruling applied: accuracy blanked for non-binary tasks {out.loc[nb, 'study_id'].tolist()} "
                  f"(kept in accuracy_all_tasks).")

    n_studies = len(out)
    n_tiebreak = (out["rating_source"] == "advisor_tiebreak").sum()
    missing_acc = out["accuracy"].isna().sum() if "accuracy" in out.columns else n_studies
    out.to_csv(HERE / args.out, index=False)
    print(f"Wrote {args.out}: {n_studies} studies, {n_tiebreak} resolved by advisor tiebreak, "
          f"{missing_acc} missing an accuracy value.")
    print("Next: python ../05_Phase5_Analysis/build_results.py")


if __name__ == "__main__":
    main()
