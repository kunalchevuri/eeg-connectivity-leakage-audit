"""Write 06_Manuscript/macros_counts.tex from generated data files - the ONLY way numbers enter the manuscript.

Sources: 03_Phase3_Corpus/prisma_counts.json (screening) and, once coding is done,
05_Phase5_Analysis/results/summary.json + CSVs (RQ1-RQ3). Any result not yet computed renders as a
visible bold [PENDING] so an unfinished number can never be submitted by accident.

    python 06_Manuscript/make_macros.py
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = json.loads((ROOT / "03_Phase3_Corpus/prisma_counts.json").read_text(encoding="utf-8"))
W, S = P["wos"], P["supplementary"]
M = {
    "NincludedTotal": P["included_total"], "NincludedWos": W["included"], "NincludedSupp": S["included"],
    "NwosScreened": W["records_screened"], "NwosExclTA": W["excluded_title_abstract"],
    "NwosSought": W["reports_sought"], "NwosNotRetrieved": W["reports_not_retrieved"],
    "NwosAssessed": W["reports_assessed"], "NwosExclFT": W["excluded_full_text"],
    "NexclGeometric": W["excluded_full_text_reasons"].get("no signal-derived connectivity", 0),
    "NsuppSought": S["reports_sought"], "NsuppNotRetrieved": S["reports_not_retrieved"],
    "NsuppAssessed": S["reports_assessed"],
}
PENDING = r"\textbf{[PENDING: run build\_results.py]}"
res = ROOT / "05_Phase5_Analysis/results/summary.json"
R = json.loads(res.read_text(encoding="utf-8")) if res.exists() else {}
rq2, rq3 = R.get("rq2", {}), R.get("rq3", {})


# Once results exist, a missing value means the statistic could not be estimated (e.g. no study was
# rated leakage-free) - the prose around it must change, so say that, never print "nan".
MISSING = r"\textbf{[NOT ESTIMABLE: empty stratum - rewrite this sentence]}" if R else PENDING


def ok(x):
    return isinstance(x, (int, float)) and not math.isnan(x)


def pct(x):
    return f"{100 * x:.0f}" if ok(x) else MISSING


def num(x, fmt="{:.2f}"):
    return fmt.format(x) if ok(x) else MISSING


M.update({
    "Kappa": num(rq2.get("kappa")), "KappaLo": num(rq2.get("kappa_ci_low")), "KappaHi": num(rq2.get("kappa_ci_high")),
    "PctAgree": pct(rq2.get("percent_agreement")),
    "MedLikely": num(rq3.get("median_likely"), "{:.1f}"), "MedFree": num(rq3.get("median_free"), "{:.1f}"),
    "CliffDelta": num(rq3.get("cliffs_delta")),
})
# Results-prose numbers (build_results.py text_numbers). Always defined, so the paper compiles before results exist.
TEXT_KEYS = ["Nstudies", "NFree", "NPossible", "NLikely", "NUnclear", "PctFree", "PctPossible", "PctLikely", "PctUnclear",
             "Ntiebreak", "PctSubject",
             "PctUnclearSplit", "PctUnclearScope", "PctUnclearThresh", "PctUnclearNorm", "PctUnclearSelect",
             "PctWholeScope", "PctWholeThresh", "PctWholeNorm", "PctWholeSelect",
             "PctWithinScope", "PctWithinThresh", "PctWithinNorm", "PctWithinSelect",
             "PctNoneThresh", "PctNoneNorm", "PctNoneSelect",
             "AgreeSplit", "AgreeScope", "AgreeThresh", "AgreeNorm", "AgreeSelect", "NdisagreeInitial",
             "Nrecoded", "AgreeRecoded",
             "NsubjMedian", "NsubjMin", "NsubjMax", "NsubjMissing",
             "DataMumtaz", "DataMODMA", "DataPREDCT", "DataPrivate", "DataOther",
             "ConnPLV", "ConnPLI", "ConnCoh", "ConnCorr", "ConnGranger", "ConnOther",
             "ArchCNN", "ArchGNN", "ArchTransformer", "ArchOther", "YearMin", "YearMax"]
T = R.get("text", {})
for key in TEXT_KEYS:
    v = T.get(key)
    M[key] = str(v) if isinstance(v, int) and not isinstance(v, bool) else (PENDING if not R else MISSING)
# Formatted statistics (build_results.py text_stats) and sensitivity analyses (sensitivity.py). Strings, verbatim.
FMT_KEYS = ["PctEpochLo", "PctEpochHi", "PctUnclearAnyLo", "PctUnclearAnyHi",
            "PctFreeLo", "PctFreeHi", "PctPossibleLo", "PctPossibleHi", "PctLikelyLo", "PctLikelyHi",
            "PctUnclearLo", "PctUnclearHi",
            "NaccStudies", "NaccFree", "NaccPossible", "NaccLikely", "NaccUnclear",
            "MedFreeFmt", "MedPossibleFmt", "MedLikelyFmt", "MedUnclearFmt",
            "IQRFree", "IQRPossible", "IQRLikely", "IQRUnclear", "AccFreeValues",
            "MWU", "MWp", "CliffLo", "CliffHi", "MedDiff", "MedDiffLo", "MedDiffHi", "SESOIverdict",
            "KWH", "KWp", "KWk",
            "NLikelySmall", "NLikelyMedium", "NLikelyLarge", "NFreeSmall", "NFreeMedium", "NFreeLarge"]
F = R.get("text_fmt", {})
for key in FMT_KEYS:
    v = F.get(key)
    M[key] = v.replace("%", r"\%") if isinstance(v, str) else (PENDING if not R else MISSING)
sens_path = ROOT / "05_Phase5_Analysis/results/sensitivity.json"
SENS = json.loads(sens_path.read_text(encoding="utf-8")) if sens_path.exists() else {}
for name, tag in (("S1_one_per_group", "One"), ("S2_binary_only", "Two"), ("S3_drop_weakest", "Three"), ("S4_rule_a_abstract", "Four")):
    o = SENS.get(name) or (SENS.get("S2_all_tasks", {}) if tag == "Two" else {})
    lvf = o.get("likely_vs_free") if isinstance(o, dict) else None
    M["Sens" + tag + "N"] = str(o["n_studies"]) if "n_studies" in o else PENDING
    if isinstance(lvf, dict):
        M["Sens" + tag + "Delta"] = f"{lvf['cliffs_delta']:.2f}"
        M["Sens" + tag + "MedDiff"] = f"{lvf['median_diff_pp']:.1f}"
        M["Sens" + tag + "Null"] = "smaller than" if lvf["within_SESOI_report_null"] else "at least as large as"
    else:
        for k in ("Delta", "MedDiff", "Null"):
            M["Sens" + tag + k] = PENDING if not SENS else MISSING
for name, tag in (("S1_one_per_group", "One"), ("S2_binary_only", "Two"), ("S3_drop_weakest", "Three"), ("S4_rule_a_abstract", "Four")):
    o = SENS.get(name) or (SENS.get("S2_all_tasks", {}) if tag == "Two" else {})
    lvf = o.get("likely_vs_free") if isinstance(o, dict) else None
    for k in ("n_free", "n_likely"):
        M["Sens" + tag + ("Nfree" if k == "n_free" else "Nlikely")] = str(lvf[k]) if isinstance(lvf, dict) else (PENDING if not SENS else MISSING)
# RQ4 (rq4.py) and the research-group count (research_groups.csv)
rq4_path = ROOT / "05_Phase5_Analysis/results/rq4.json"
RQ4 = json.loads(rq4_path.read_text(encoding="utf-8")) if rq4_path.exists() else {}
yt = RQ4.get("year_trend", {})
for key, field in (("RqFourRho", "spearman_rho"), ("RqFourLo", "ci_low"), ("RqFourHi", "ci_high")):
    M[key] = num(yt.get(field)) if RQ4 else PENDING
import csv as _csv
_groups = list(_csv.DictReader(open(ROOT / "05_Phase5_Analysis/research_groups.csv", encoding="utf-8")))
M["NgroupStudies"] = str(len(_groups))
for key in ("PctUnclearAny", "PctEpoch"):   # filled by build_results.py from the RQ1 tables
    M[key] = num(R.get("abstract", {}).get(key), "{:.0f}")

# POST HOC reviewer-response analyses (05_Phase5_Analysis/reviewer_response.py, written 2026-11-07).
# These are NOT pre-specified; every sentence that uses them must say so. See 08_Admin/deviations_log.md.
rr_path = ROOT / "05_Phase5_Analysis/results/reviewer_response.json"
RR = json.loads(rr_path.read_text(encoding="utf-8")) if rr_path.exists() else {}
RR_MISSING = r"\textbf{[PENDING: run reviewer\_response.py]}"


def rpct(x):
    return f"{100 * x:.0f}" if ok(x) else RR_MISSING


if RR:
    A = RR["A_not_reported_bound"]
    M.update({
        "StrictNfree": str(A["n_free_after"]), "StrictNfreeBefore": str(A["n_free_before"]),
        "StrictNpossible": str(A["rating_after"]["possible"]),
        "StrictNlikely": str(A["n_likely_after"]), "StrictNchanged": str(A["n_studies_rating_changed"]),
        "StrictNcells": str(A["n_none_cells_recoded"]),
    })
    # LaTeX command names may not contain digits, so L1..L5 become Lone..Lfive.
    WORD = {"L1": "Lone", "L2": "Ltwo", "L3": "Lthree", "L4": "Lfour", "L5": "Lfive"}
    for row in RR["B_per_surface_agreement"]:
        tag = WORD[row["surface"]]
        if row["kappa_defined"]:
            M["Kap" + tag] = f"{row['kappa']:.2f}"
            M["Kap" + tag + "Lo"] = f"{row['kappa_ci_low']:.2f}"
            M["Kap" + tag + "Hi"] = f"{row['kappa_ci_high']:.2f}"
        else:
            for suf in ("", "Lo", "Hi"):
                M["Kap" + tag + suf] = "undefined"
        M["Agree" + tag + "Pct"] = rpct(row["percent_agreement"])
    C = RR["C_clustering"]
    ds, gr = C["by_cluster"]["dataset"], C["by_cluster"]["research_group"]
    M.update({
        "ClDatasetN": str(ds["n_clusters"]), "ClGroupN": str(gr["n_clusters"]),
        "ClEpochDsLo": rpct(ds["epoch"]["cluster_bootstrap_ci"][0]),
        "ClEpochDsHi": rpct(ds["epoch"]["cluster_bootstrap_ci"][1]),
        "ClEpochGrLo": rpct(gr["epoch"]["cluster_bootstrap_ci"][0]),
        "ClEpochGrHi": rpct(gr["epoch"]["cluster_bootstrap_ci"][1]),
        "ClUnclearDsLo": rpct(ds["unclear_any"]["cluster_bootstrap_ci"][0]),
        "ClUnclearDsHi": rpct(ds["unclear_any"]["cluster_bootstrap_ci"][1]),
    })
    top = max(C["per_dataset"], key=lambda r: r["n_studies"])
    M.update({"TopDataset": str(top["dataset"]), "TopDatasetN": str(top["n_studies"]),
              "TopDatasetEpoch": str(top["n_epoch_level"]),
              "NepochTotal": str(sum(r["n_epoch_level"] for r in C["per_dataset"]))})
    D = RR["D_rq4_exact"]
    M.update({
        "RqFourPermP": f"{D['permutation_p_two_sided']:.3f}",
        "RqFourOR": f"{D['dichotomised']['odds_ratio']:.1f}",
        "RqFourFisherP": f"{D['dichotomised']['fisher_p_two_sided']:.2f}",
        "RqFourNrecent": str(D["dichotomised"]["n_recent"]),
        "RqFourNincomplete": str(D["dichotomised"]["n_incomplete"]),
    })
else:
    for k in ("StrictNfree", "StrictNfreeBefore", "StrictNpossible", "StrictNlikely", "StrictNchanged",
              "StrictNcells", "ClDatasetN", "ClGroupN", "ClEpochDsLo", "ClEpochDsHi", "ClEpochGrLo",
              "ClEpochGrHi", "ClUnclearDsLo", "ClUnclearDsHi", "TopDataset", "TopDatasetN",
              "TopDatasetEpoch", "NepochTotal", "RqFourPermP", "RqFourOR", "RqFourFisherP", "RqFourNrecent",
              "RqFourNincomplete"):
        M[k] = RR_MISSING
    for tag in ("Lone", "Ltwo", "Lthree", "Lfour", "Lfive"):
        for suf in ("", "Lo", "Hi"):
            M["Kap" + tag + suf] = RR_MISSING
        M["Agree" + tag + "Pct"] = RR_MISSING

M = {k: ("$-$" + v[1:] if isinstance(v, str) and v.startswith("-") and v[1:2].isdigit() else v) for k, v in M.items()}
lines = ["% GENERATED by make_macros.py - do not edit. Re-run after any screening or analysis change."]
lines += ["\\newcommand{\\" + k + "}{" + str(v) + "}" for k, v in M.items()]
(ROOT / "06_Manuscript/macros_counts.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
