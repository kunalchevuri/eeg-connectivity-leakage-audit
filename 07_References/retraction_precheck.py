"""Automated retraction/correction PRE-check for every DOI in bib_keys.csv, via Crossref.

Crossref records retractions, corrections and expressions of concern as update notices
(including Retraction Watch data). This flags any notice attached to a reference. It does NOT
satisfy blueprint Sec 12: KC still opens each original and ticks retraction_checked himself
in reference_verification_log.csv. Output: retraction_precheck.csv (rerun before submission).

    python 07_References/retraction_precheck.py
"""
import csv
import json
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
UA = {"User-Agent": "eeg-leakage-audit-reference-check (mailto:ckchevuri@gmail.com)"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["message"]


def check(doi):
    q = urllib.parse.quote(doi, safe="")
    w = get(f"https://api.crossref.org/works/{q}")
    notices = [f"{u.get('type')}:{u.get('DOI')}" for u in w.get("updated-by", [])]
    upd = get(f"https://api.crossref.org/works?filter=updates:{q}&rows=20")
    for it in upd.get("items", []):
        for u in it.get("update-to", []):
            if u.get("DOI", "").lower() == doi.lower():
                notices.append(f"{u.get('type')}:{it.get('DOI')}")
    title = (w.get("title") or [""])[0]
    if title.upper().startswith(("RETRACTED", "WITHDRAWN")):
        notices.append("title-flag:" + title[:60])
    return sorted(set(notices))


def main():
    rows = list(csv.DictReader((HERE / "bib_keys.csv").open(encoding="utf-8")))
    out = []
    for r in rows:
        doi = r["doi"].strip()
        try:
            notes = check(doi)
            status = "NOTICE FOUND - open it" if notes else "no notice in Crossref"
        except Exception as e:  # network or 404 - never silently pass
            notes, status = [str(e)[:80]], "CHECK FAILED - check by hand"
        out.append({"key": r["key_or_detail"], "doi": doi, "status": status,
                    "notices": "; ".join(notes), "checked_on": date.today().isoformat()})
        print(f"{r['key_or_detail']:<14} {status} {'; '.join(notes)}")
        time.sleep(0.3)
    with (HERE / "retraction_precheck.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    flagged = [o for o in out if o["status"] != "no notice in Crossref"]
    print(f"\n{len(out)} checked; {len(flagged)} need attention. Wrote retraction_precheck.csv")


if __name__ == "__main__":
    main()
