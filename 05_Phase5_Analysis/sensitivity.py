"""Pre-specified RQ3 sensitivity analyses. WRITTEN 2026-09-24, BEFORE ANY RATING EXISTED.

Each re-runs analysis.py's own rq3() unchanged on a pre-defined subset, so nothing here can be
tuned after seeing results. Which of these the paper reports is the advisor's decision
(advisor question 21); none feed the headline macros.

  S1 one_per_group  - one study per research group (research_groups.csv). Within a group, keep
                      the study with the LOWEST WoS rank (most cited). Decided now, not after.
  S2 binary_only    - drop studies whose recorded accuracy is not a binary depression-vs-control
                      task (task_type.csv; advisor question 20).
  S3 drop_weakest   - drop the two weakest inclusions, WoS ranks 49 (EEG+speech fused, no EEG-only
                      result) and 102 (weak venue), as flagged at screening.

  S4 rule_a_abstract - ADDED 2026-09-24 ON THE ADVISOR'S RULING (Q16), after coding but before any accuracy
                      was analysed: every study, with the abstract's headline accuracy (accuracy_abstract)
                      and the INITIAL-pass rating (leakage_rating_initial), because the initial pass coded
                      the protocol behind the abstract figure. Rating and accuracy therefore refer to the
                      same protocol, as the ruling requires.

Any change to these definitions after coding starts must go in 08_Admin/deviations_log.md.

    python 05_Phase5_Analysis/sensitivity.py      (after build_results.py)
"""
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
ROOT = HERE.parent
DROP_WEAKEST = {49, 102}

spec = importlib.util.spec_from_file_location("analysis", HERE / "analysis.py")
analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)


def subsets(final):
    groups = pd.read_csv(HERE / "research_groups.csv")
    keep_from_group = groups.sort_values("wos_rank").groupby("group_id")["wos_rank"].first()
    grouped = set(groups["wos_rank"])
    s1 = final[~final["wos_rank"].isin(grouped) | final["wos_rank"].isin(keep_from_group)]

    tasks = pd.read_csv(HERE / "task_type.csv")
    non_binary = set(tasks.loc[tasks["task_type"] != "binary", "wos_rank"])
    rulings = json.loads((HERE / "advisor_rulings.json").read_text(encoding="utf-8"))
    if rulings.get("q20_binary_only_primary") and "accuracy_all_tasks" in final.columns:
        s2 = final.copy()                      # primary is already binary-only; S2 = every task (advisor Q20)
        s2["accuracy"] = s2["accuracy_all_tasks"]
    else:
        s2 = final[~final["wos_rank"].isin(non_binary)]

    s3 = final[~final["wos_rank"].isin(DROP_WEAKEST)]
    s2_name = "S2_all_tasks" if (rulings.get("q20_binary_only_primary") and "accuracy_all_tasks" in final.columns) else "S2_binary_only"
    out = {"S1_one_per_group": s1, s2_name: s2, "S3_drop_weakest": s3}
    if {"accuracy_abstract", "leakage_rating_initial"} <= set(final.columns):
        s4 = final.copy()
        s4["accuracy"] = s4["accuracy_abstract"]
        s4["leakage_rating"] = s4["leakage_rating_initial"]
        out["S4_rule_a_abstract"] = s4
    else:
        print("S4 skipped: coding_sheet_FINAL.csv has no accuracy_abstract / leakage_rating_initial column")
    return out


def main():
    final = pd.read_csv(ROOT / "04_Phase4_Coding/coding_sheet_FINAL.csv")
    key = pd.read_csv(ROOT / "04_Phase4_Coding/study_id_key_2026-09-23.csv")[["study_id", "wos_rank"]]
    final = final.merge(key, on="study_id", how="left")
    if final["wos_rank"].isna().any():
        raise SystemExit("some study_ids are missing from the study key")

    out = {}
    for name, df in subsets(final).items():
        rng = np.random.default_rng(analysis.SEED)   # same seed as the main analysis, per subset
        r = analysis.rq3(df, rng)
        out[name] = {"n_studies": len(df),
                     "dropped_wos_ranks": sorted(set(final["wos_rank"]) - set(df["wos_rank"])),
                     "strata": r["strata"].to_dict("records"),
                     "likely_vs_free": r["likely_vs_free"],
                     "kruskal_wallis_all_strata": r.get("kruskal_wallis_all_strata")}
    res = HERE / "results"
    res.mkdir(exist_ok=True)
    (res / "sensitivity.json").write_text(json.dumps(out, indent=2, default=float))
    for name, o in out.items():
        lvf = o["likely_vs_free"]
        d = lvf.get("cliffs_delta") if isinstance(lvf, dict) else None
        print(f"{name:18} n={o['n_studies']:2}  dropped={o['dropped_wos_ranks']}  "
              f"cliffs_delta={'%.2f' % d if d is not None else 'not estimable'}")
    print(f"Wrote {res / 'sensitivity.json'}")


if __name__ == "__main__":
    main()
