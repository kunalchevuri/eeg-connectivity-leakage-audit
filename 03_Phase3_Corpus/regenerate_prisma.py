"""Regenerate the PRISMA counts from screening_log.csv and supplementary_candidates.csv.

Blueprint standing rule: never report a number you cannot regenerate from the coding sheet.
Run this after every screening change; Fig. 1 and Section IV-A read its output, never hand-typed counts.

    python 03_Phase3_Corpus/regenerate_prisma.py

Writes prisma_counts.csv (human-readable) and prisma_counts.json (read by make_fig1_prisma.py).
Structure follows PRISMA 2020: identification -> screening -> retrieval -> eligibility -> included,
with the Web of Science top-100 and the Section 7.1 supplementary search as two separate arms.
"""
import csv
import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "screening_log.csv")
SUPP = os.path.join(HERE, "supplementary_candidates.csv")

with open(LOG, newline="", encoding="utf-8") as fh:
    rows = list(csv.DictReader(fh))
C = list(rows[0].keys())
RANK, EXAS, DEC, STAGE = C[0], C[12], C[13], C[14]


def v(r, k):
    return (r.get(k) or "").strip()


def rank(r):
    return int(v(r, RANK))


def is_incl(r):
    return v(r, DEC) in ("include", "include?")


def is_excl(r):
    return v(r, DEC).startswith("exclude")


def ids(rs):
    return ", ".join("R%03d" % rank(r) for r in sorted(rs, key=rank))


def reasons(rs):
    c = Counter(v(r, EXAS) or "(reason not recorded)" for r in rs)
    return dict(sorted(c.items(), key=lambda kv: -kv[1]))


# ---------------- Arm 1: WoS top-100 ----------------
base = [r for r in rows if rank(r) <= 100]
ta_excl = [r for r in base if is_excl(r) and v(r, STAGE) == "title-abstract"]
sought = [r for r in base if r not in ta_excl]
not_retrieved = [r for r in sought if v(r, DEC) in ("to full-text", "not retrieved")]
assessed = [r for r in sought if r not in not_retrieved]
ft_excl = [r for r in assessed if is_excl(r)]
base_incl = [r for r in assessed if is_incl(r)]
assert len(ta_excl) + len(not_retrieved) + len(ft_excl) + len(base_incl) == len(base), "WoS arm does not reconcile"

# ---------------- Arm 2: supplementary search (blueprint 7.1) ----------------
supp_rows = [r for r in rows if rank(r) > 100]
with open(SUPP, newline="", encoding="utf-8") as fh:
    cands = list(csv.DictReader(fh))
supp_sought = len(cands)
supp_not_retrieved = sum(1 for c in cands if c["status"].startswith("NOT RETRIEVED"))
supp_assessed = len(supp_rows)
supp_excl = [r for r in supp_rows if is_excl(r)]
supp_incl = [r for r in supp_rows if is_incl(r)]
assert supp_sought - supp_not_retrieved == supp_assessed, (
    "supplementary_candidates.csv and screening_log.csv disagree on how many supplementary reports were assessed")

included = base_incl + supp_incl
firm = [r for r in included if v(r, DEC) == "include"]
prov = [r for r in included if v(r, DEC) == "include?"]

data = {
    "wos": {"records_screened": len(base), "excluded_title_abstract": len(ta_excl),
            "excluded_title_abstract_reasons": reasons(ta_excl),
            "reports_sought": len(sought), "reports_not_retrieved": len(not_retrieved),
            "reports_assessed": len(assessed), "excluded_full_text": len(ft_excl),
            "excluded_full_text_reasons": reasons(ft_excl), "included": len(base_incl)},
    "supplementary": {"reports_sought": supp_sought, "reports_not_retrieved": supp_not_retrieved,
                      "reports_assessed": supp_assessed, "excluded_full_text": len(supp_excl),
                      "included": len(supp_incl)},
    "included_total": len(included), "included_firm": len(firm), "included_provisional": len(prov),
    "included_ids": ids(included), "provisional_ids": ids(prov),
    "exit_condition_met": len(included) >= 15,
    "wos_query_recovered": False,
}
with open(os.path.join(HERE, "prisma_counts.json"), "w", encoding="utf-8") as fh:
    json.dump(data, fh, indent=2)

w, s = data["wos"], data["supplementary"]
lines = [
    ("stage", "count", "notes"),
    ("WoS records identified (original search)", "not yet recovered", "query string/date/hit count needed for Section IV-A and Fig 1 - advisor question 11"),
    ("WoS: records screened (top-100 set)", w["records_screened"], ""),
    ("WoS: excluded at title/abstract", w["excluded_title_abstract"], "; ".join("%s: %d" % kv for kv in w["excluded_title_abstract_reasons"].items())),
    ("WoS: reports sought for retrieval", w["reports_sought"], ""),
    ("WoS: reports not retrieved", w["reports_not_retrieved"], "never attempted under an unplanned stopping rule (23; advisor Q22) or unobtainable (R010): " + ids(not_retrieved)),
    ("WoS: reports assessed for eligibility", w["reports_assessed"], ""),
    ("WoS: excluded at full text", w["excluded_full_text"], "; ".join("%s: %d" % kv for kv in w["excluded_full_text_reasons"].items()) + ". Provisional (exclude?): " + (ids([r for r in ft_excl if v(r, DEC) == "exclude?"]) or "none")),
    ("WoS: included", w["included"], ids(base_incl)),
    ("Supplementary (Sec 7.1): reports sought", s["reports_sought"], "eligible-looking candidates from OpenAlex + PubMed, see supplementary_candidates.csv"),
    ("Supplementary: reports not retrieved", s["reports_not_retrieved"], "advisor question 13 (availability bias)"),
    ("Supplementary: reports assessed", s["reports_assessed"], ""),
    ("Supplementary: excluded at full text", s["excluded_full_text"], ""),
    ("Supplementary: included", s["included"], ids(supp_incl)),
    ("INCLUDED TOTAL", data["included_total"], "firm %d (%s); provisional %d (%s)" % (len(firm), ids(firm), len(prov), ids(prov))),
    ("Exit condition (>=15 included)", "MET" if data["exit_condition_met"] else "NOT MET", ""),
]
with open(os.path.join(HERE, "prisma_counts.csv"), "w", newline="", encoding="utf-8") as fh:
    csv.writer(fh).writerows(lines)
for a, b, c in lines[1:]:
    print("%-48s %-6s %s" % (a, b, (str(c)[:70] + "...") if len(str(c)) > 70 else c))
