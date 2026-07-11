#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Model Work Organization Regulation track (Annex 1).

Trust gate: 72 articles (complete 1..72, all ACTIVE, OCR floor cleared) + the
3 violation tables (50 rows, expected row counts per section, linearization
byte-reproducible from the committed table cells). Also re-checks the adoption
link: regulation article (3) must actually reference الملحق رقم 1."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "labor", "annex1", "official_source",
                   "labor_annex1_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "labor", "annex1", "verified",
                       "labor_annex1_verified_records.jsonl")
LLM_ART = os.path.join(ROOT, "data", "labor_arabic_legal_llm", "labor_annex1_legal_llm_001_072.json")
LLM_TAB = os.path.join(ROOT, "data", "labor_arabic_legal_llm", "labor_annex1_violation_tables_llm.json")
REG_RECORDS = os.path.join(ROOT, "sources", "labor", "regulation", "verified",
                           "labor_regulation_verified_records.jsonl")
STATUS = "HRSD_OFFICIAL_PDF_OCR_IMAGE_CROSS_CHECKED"
N_ART = 72
TABLE_ROWS = [16, 18, 16]
OCR_FLOOR = 0.85


def _table_text(t):
    cols = t["columns"]
    notes = t.get("row_notes", {})
    lines = [t["section_ar"]]
    for row in t["rows"]:
        cells = ["%s: %s" % (cols[i], row[i]) for i in range(len(cols)) if str(row[i]).strip()]
        line = " | ".join(cells)
        note = notes.get(str(row[0]))
        if note:
            line += " | " + note
        lines.append(line)
    return "\n".join(lines)


def main():
    e = []
    for p in (SRC, RECORDS, LLM_ART, LLM_TAB, REG_RECORDS):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    tables = src["violation_tables"]

    # [1] structure: complete 1..72, all ACTIVE, OCR floor, sections present
    nums = sorted(int(re.match(r"labor_annex1_art_(\d{3})", k).group(1)) for k in arts)
    if nums != list(range(1, N_ART + 1)):
        e.append("[1] articles not a complete 1..%d sequence" % N_ART)
    for k, a in arts.items():
        if a["status"] != "ACTIVE":
            e.append("[1] %s: unexpected status %r" % (k, a["status"]))
        if not a["text"].strip() or re.search(r"[A-Za-z]", a["text"]):
            e.append("[1] %s: empty text or latin chars" % k)
        if (a.get("ocr_similarity") or 0) < OCR_FLOOR:
            e.append("[1] %s: OCR similarity below %.2f" % (k, OCR_FLOOR))
        if not a.get("section_ar", "").strip():
            e.append("[1] %s: missing section heading" % k)
    if not src.get("preamble", {}).get("text", "").strip():
        e.append("[1] preamble missing")

    # [2] violation tables: 3 sections, expected row counts, 6 cells per row
    if len(tables) != 3:
        e.append("[2] expected 3 violation tables, found %d" % len(tables))
    for i, t in enumerate(tables):
        if len(t["rows"]) != TABLE_ROWS[i]:
            e.append("[2] table %d: %d rows != %d" % (i + 1, len(t["rows"]), TABLE_ROWS[i]))
        if len(t["columns"]) != 6:
            e.append("[2] table %d: expected 6 columns" % (i + 1))
        for row in t["rows"]:
            if len(row) != 6:
                e.append("[2] table %d row %s: %d cells" % (i + 1, row[0], len(row)))
            if not str(row[1]).strip():
                e.append("[2] table %d row %s: empty violation text" % (i + 1, row[0]))
    if sum(len(t["rows"]) for t in tables) != sum(TABLE_ROWS):
        e.append("[2] total rows != %d" % sum(TABLE_ROWS))

    # [3] adoption link: regulation art 3 references الملحق رقم 1
    reg3 = None
    for line in open(REG_RECORDS, encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            if r["article_number"] == 3 and not r["is_mukarrar"]:
                reg3 = r["article_text_verified"]
    if not reg3 or "الملحق رقم 1" not in reg3.replace("(", "").replace(")", ""):
        e.append("[3] regulation art 3 does not reference الملحق رقم 1")

    # [4] verified records + [5] LLM layers verbatim/hashes/linearization
    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N_ART + 3:
        e.append("[4] %d verified records != %d" % (len(ver), N_ART + 3))
    for r in ver:
        if r.get("official_text_status") != STATUS:
            e.append("[4] %s: bad status" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))
    vmap = {r["article_key"]: r for r in ver}
    for k, a in arts.items():
        if vmap.get(k, {}).get("article_text_verified") != a["text"]:
            e.append("[4] %s: text != source" % k)
    for i, t in enumerate(tables, start=1):
        k = "labor_annex1_violation_table_%d" % i
        if vmap.get(k, {}).get("article_text_verified") != _table_text(t):
            e.append("[4] %s: linearization not byte-reproducible from source cells" % k)

    for path, count, kind in ((LLM_ART, N_ART, "articles"), (LLM_TAB, 3, "tables")):
        llm = json.load(open(path, encoding="utf-8"))
        recs = llm.get("records", [])
        if llm.get("record_count") != count or len(recs) != count:
            e.append("[5] %s layer count != %d" % (kind, count))
        for r in recs:
            if r["article_text_ar"] != vmap[r["article_key"]]["article_text_verified"]:
                e.append("[5] %s: llm text != verified" % r["article_key"])
            if r["article_text_hash_sha256"] != hashlib.sha256(
                    r["article_text_ar"].encode("utf-8")).hexdigest():
                e.append("[5] %s: hash mismatch" % r["article_key"])
            if not r.get("keywords_ar") or not r.get("search_queries_ar"):
                e.append("[5] %s: missing retrieval metadata" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Labor Annex 1 track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Model Work Organization Regulation track — 75 records (72 articles + 3 violation tables, 50 rows)")
    print("  - articles complete 1..72, all ACTIVE, OCR floor %.2f cleared; sections attached" % OCR_FLOOR)
    print("  - tables 16/18/16 rows, 6 cells each; linearization byte-reproducible from committed cells")
    print("  - adoption link verified: regulation art (3) references الملحق رقم 1")
    print("  - texts verbatim vs committed source; hashes consistent; Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
