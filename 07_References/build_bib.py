"""Build 06_Manuscript/references.bib from Crossref records - never from memory.

Every entry carries note = {UNVERIFIED ...}, which prints in the bibliography until Kunal has opened the
original and marked it checked in REFERENCE_CHECK_SHEET.xlsx (blueprint Sec 12). An entry whose Crossref title does not match the expected
title is REJECTED and reported, not written.

    python 07_References/build_bib.py
"""
import csv, json, re, sys, time, unicodedata, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.stdout.reconfigure(encoding="utf-8")


def fetch(doi):
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi)
    rq = urllib.request.Request(url, headers={"User-Agent": "EEG-audit-bib-builder/1.0"})
    for i in range(3):
        try:
            with urllib.request.urlopen(rq, timeout=30) as r:
                return json.load(r)["message"]
        except Exception as e:
            err = e; time.sleep(2)
    raise err


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def tex(s):
    s = s or ""
    s = re.sub(r"<[^>]+>", "", s)  # strip JATS/MathML tags Crossref sometimes includes
    for a, b in [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("_", r"\_"), ("#", r"\#"), ("$", r"\$")]:
        s = s.replace(a, b)
    return s


# (group, doi, expected-title fragment used to check the Crossref record)
TARGETS = []
wos = {r["DOI"].strip().lower(): r for r in csv.DictReader(open(ROOT / "source_materials/thinkneuro_drive/WoS_Top100_Updated_Extraction_2026-09-23.csv", encoding="utf-8"))}
supp = {r["doi"].strip().lower(): r for r in csv.DictReader(open(ROOT / "03_Phase3_Corpus/supplementary_records.csv", encoding="utf-8"))}
for r in csv.DictReader(open(ROOT / "03_Phase3_Corpus/screening_log.csv", encoding="utf-8")):
    if r["decision (include/exclude)"].strip() in ("include", "include?"):
        d = r["doi"].strip().lower()
        TARGETS.append(("corpus R%03d" % int(r["wos_rank"]), d, r["title"]))
for r in csv.DictReader(open(ROOT / "07_References/reference_verification_log.csv", encoding="utf-8")):
    if r["ref_no"].startswith("R") and r["doi"]:
        TARGETS.append(("prior " + r["ref_no"], r["doi"].strip().lower(), r["citation"].split(").")[1].split(".")[0] if ")." in r["citation"] else ""))
METHODS = [  # connectivity-measure original sources (blueprint Sec 12: 3-4 methods references)
    ("method PLV", "10.1002/(sici)1097-0193(1999)8:4<194::aid-hbm4>3.0.co;2-c", "Measuring phase synchrony in brain signals"),
    ("method PLI", "10.1002/hbm.20346", "Phase lag index"),
    ("method coherence", "10.1016/s0013-4694(97)00066-7", "EEG coherency"),
]
TARGETS += METHODS

# Keys Kunal has recorded as checked (REFERENCE_CHECK_SHEET.xlsx: opened, metadata, supports all "y") get no UNVERIFIED note.
import html  # REVIEW 2026-09-27
import openpyxl
_ws = openpyxl.load_workbook(ROOT / "07_References/REFERENCE_CHECK_SHEET.xlsx").active
_h = [c.value for c in _ws[1]]
VERIFIED = {r[0] for r in _ws.iter_rows(min_row=2, values_only=True) if r[0] and all(
    str(r[_h.index(c)] or "").strip().lower() == "y" for c in
    ("opened original? (y/n)", "metadata correct? (y/n)", "supports EVERY sentence? (y/n)"))}

entries, log, seen_keys, seen_dois = [], [], set(), set()
for group, doi, expect in TARGETS:
    if doi in seen_dois:      # the verification log repeats corpus and method DOIs; one entry each
        continue
    seen_dois.add(doi)
    try:
        m = fetch(doi)
    except Exception as e:
        log.append((group, doi, "FETCH FAILED", str(e)[:60])); continue
    title = (m.get("title") or [""])[0]
    exp_words = [w for w in norm(expect).split() if len(w) > 4][:6]
    ok = all(w in norm(title) for w in exp_words) if exp_words else True
    if not ok:
        log.append((group, doi, "REJECTED - title mismatch", title[:70])); continue
    authors = m.get("author", [])
    # REVIEW 2026-09-27: skip empty Crossref author records (jia2025 printed ", ,")
    au = " and ".join(tex((a.get("family", "") + ", " + a.get("given", "")).strip(", ")) for a in authors if (a.get("family") or a.get("given")))  or tex((m.get("editor") or [{}])[0].get("family", ""))
    year = ((m.get("published-print") or m.get("published-online") or m.get("issued") or {}).get("date-parts") or [[None]])[0][0]
    first = norm(authors[0].get("family", "anon")).replace(" ", "") if authors else "anon"
    key = f"{first}{year}"
    while key in seen_keys:
        key += "b" if not key[-1].isalpha() or key[-1] == str(year)[-1] else chr(ord(key[-1]) + 1)
    seen_keys.add(key)
    typ = m.get("type")
    btype = "inproceedings" if typ in ("proceedings-article",) else "article"
    fields = {"author": au, "title": "{" + tex(title) + "}", "year": str(year), "doi": m.get("DOI", doi),
              ("booktitle" if btype == "inproceedings" else "journal"): tex(html.unescape((m.get("container-title") or [""])[0])),  # REVIEW 2026-09-27: html.unescape, Crossref returns "&amp;"
              "volume": m.get("volume", ""), "number": m.get("issue", ""),
              "pages": (m.get("page") or m.get("article-number") or "").replace("-", "--"),
              "note": "{UNVERIFIED -- open and check the original (blueprint Sec. 12)}"}  # inner braces keep IEEEtran from lowercasing U
    if key in VERIFIED:
        del fields["note"]
    body = ",\n".join(f"  {k} = {{{v}}}" for k, v in fields.items() if v)
    entries.append(f"% {group}\n@{btype}{{{key},\n{body}\n}}")
    log.append((group, doi, "OK", key))
    time.sleep(0.3)

# 2026-09-27: references.bib now holds entries added by hand in review (sahuc2026 has a DataCite DOI that Crossref
# cannot return). Refuse to write if any existing entry would disappear.
_old = (ROOT / "06_Manuscript/references.bib").read_text(encoding="utf-8")
_lost = set(re.findall(r"^@\w+\{([^,]+),", _old, re.M)) - {e.split("{", 1)[1].split(",", 1)[0] for e in entries}
if _lost:
    sys.exit(f"NOT WRITTEN: rebuilding would drop {sorted(_lost)} from references.bib. Edit that file by hand instead.")
(ROOT / "06_Manuscript/references.bib").write_text(
    "% GENERATED by 07_References/build_bib.py from Crossref. Do not hand-edit metadata; delete the UNVERIFIED note\n"
    "% of an entry only after opening the original and filling its row in reference_verification_log.csv.\n\n"
    + "\n\n".join(entries) + "\n", encoding="utf-8")
with open(ROOT / "07_References/bib_keys.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["group", "doi", "status", "key_or_detail"]); w.writerows(log)
for g, d, s, k in log:
    print(f"{s:28s} {g:16s} {k}")
