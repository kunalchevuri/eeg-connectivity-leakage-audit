"""Pre-submission checks on the compiled paper.pdf (blueprint Phases 8-9 and the pre-submission checklist).
It reports; it never edits. Run after run_pipeline.py:

    python 06_Manuscript/tools/preflight.py                      # double-blind submission build
    python 06_Manuscript/tools/preflight.py paper.pdf --camera-ready --max-pages 9

FAIL items block submission; CHECK items need a human look.

--camera-ready inverts the anonymity rules, because review is over: the author names and affiliations must now
be PRESENT, and their absence is the failure. --max-pages raises the limit to 8 plus however many extra pages
were actually purchased (MLESP: up to two at $100 each, bought during registration). Never raise it on the
assumption that a page will be bought; raise it only once the registration receipt shows it.
"""
import re
import sys
from pathlib import Path

import pymupdf

MAN = Path(__file__).resolve().parents[1]
PAGE_LIMIT = 8
# In camera-ready mode every one of these must appear, or the paper is still anonymized.
REQUIRED_CR = ["Chevuri", "Ileto", "Aledhari"]
MARKERS = ["PENDING", "[CITE", "UNVERIFIED", "NOT ESTIMABLE", "AUTHOR:", "TODO", "??"]
BANNED = ["first", "novel", "unprecedented"]                      # blueprint Sec 15
IDENTITY = ["Kunal", "Chevuri", "Leah", "Ileto", "Aledhari", "George Mason", "GMU", "North Texas", "UNT",
            "Denton", "ThinkNeuro", "ckchevuri", "kunalchevuri", "digi-web-png", "github.com/kunal"]  # double-blind
UK_US = {r"analys(?:e|ed|ing)\b": "analyz", "favour": "favor", "behaviour": "behavior", "normalis": "normaliz", "organis": "organiz",
         r"characteris(?:e|ed|es|ing|ation)\b": "characteriz", "colour": "color", "modell": "model", "labell": "label", "centre": "center",
         "optimis": "optimiz", "minimis": "minimiz", "recognis": "recogniz", "summaris": "summariz", "emphasis": None,
         "randomis": "randomiz", "standardis": "standardiz", "generalis": "generaliz", "utilis": "utiliz"}


def body_text(doc):
    """Text before the reference list (reference titles are other authors' words and are exempt)."""
    t = " ".join(p.get_text() for p in doc)
    i = t.rfind("REFERENCES")
    return t[:i] if i > 0 else t, t


def main():
    args = sys.argv[1:]
    camera_ready = "--camera-ready" in args
    limit = PAGE_LIMIT
    if "--max-pages" in args:
        limit = int(args[args.index("--max-pages") + 1])
    positional = [a for i, a in enumerate(args)
                  if not a.startswith("--") and (i == 0 or args[i - 1] != "--max-pages")]
    pdf = Path(positional[0]) if positional else MAN / "paper.pdf"   # e.g. the PDF downloaded from Overleaf
    doc = pymupdf.open(pdf)
    body, full = body_text(doc)
    flat = re.sub(r"\s+", " ", body)
    fails, checks = [], []

    if len(doc) > limit:
        extra = f" (limit raised to {limit}; {limit - PAGE_LIMIT} extra page(s) must be paid for)" if limit > PAGE_LIMIT else ""
        fails.append(f"{len(doc)} pages; MLESP allows {PAGE_LIMIT} including references{extra}")
    elif len(doc) > PAGE_LIMIT:
        checks.append(f"{len(doc)} pages: {len(doc) - PAGE_LIMIT} extra page(s) beyond the 8-page limit. "
                      f"Confirm {len(doc) - PAGE_LIMIT} extra page(s) were PURCHASED during registration "
                      f"($100 each) before uploading.")
    for m in MARKERS:
        n = full.count(m)
        if n:
            fails.append(f"'{m}' appears {n} time(s)")
    for w in BANNED:
        for mt in re.finditer(rf"\b{w}\b", flat, re.I):
            checks.append(f"banned word '{w}': ...{flat[max(0, mt.start() - 60):mt.end() + 40]}...")
    if camera_ready:
        for w in REQUIRED_CR:
            if not re.search(rf"\b{re.escape(w)}\b", full):
                fails.append(f"camera-ready: author '{w}' is MISSING; the paper is still anonymized")
        for w in ("ThinkNeuro", "ckchevuri", "digi-web-png"):   # private handles never belong in the PDF
            if re.search(rf"\b{re.escape(w)}\b", full, re.I):
                fails.append(f"private identifier '{w}' in the PDF; remove it")
    else:
        for w in IDENTITY:
            flags = 0 if w.isupper() else re.I     # acronyms (GMU, UNT) case-sensitive, as whole words
            if re.search(rf"\b{re.escape(w)}\b", full, flags):
                fails.append(f"identifying string '{w}' in the PDF (double-blind)")
    for uk, us in UK_US.items():
        if us is None:
            continue
        for mt in re.finditer(rf"\b\w*{uk}\w*", flat, re.I):
            word = mt.group(0)
            checks.append(f"UK spelling '{word}' (US: {us}...)")
    meta = doc.metadata or {}
    if meta.get("author") and not camera_ready:
        checks.append(f"PDF metadata: author={meta.get('author')!r} creator={meta.get('creator')!r} (double-blind)")

    if camera_ready:
        # IEEE PDF eXpress requirements, quoted in 08_Admin/camera_ready_requirements.md (STEP 5).
        bare = set()
        for pno in range(len(doc)):
            for xref, ext, _type, basefont, *_ in doc.get_page_fonts(pno):
                if not ext:
                    bare.add(basefont)
        if bare:
            fails.append("fonts NOT embedded (IEEE Xplore requires every font embedded and subset): "
                         + ", ".join(sorted(bare)))
        sizes = {(round(p.rect.width), round(p.rect.height)) for p in doc}
        if sizes != {(612, 792)}:
            fails.append(f"page size {sorted(sizes)} is not US Letter 612x792 pt, which IEEE PDF eXpress requires")
    abstract = flat[flat.find("Abstract"):flat.find("Index Terms")] if "Index Terms" in flat else ""
    if "[" in abstract and "]" in abstract:
        fails.append("the abstract contains a bracketed placeholder or citation (automatic desk rejection, blueprint Sec 5)")

    print(f"{pdf.name}: {len(doc)} pages")
    for f in fails:
        print("FAIL  ", f)
    for c in sorted(set(checks)):
        print("CHECK ", c)
    if not fails and not checks:
        print("All checks passed.")
    print("\nNot automatable (do by hand, blueprint Phase 8): every reference opened and verified; every number in the "
          "abstract matches Results; no study named as a leakage example in prose; read the paper aloud once; "
          "figures legible in grayscale at print size.")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
