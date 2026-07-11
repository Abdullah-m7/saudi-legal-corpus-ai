#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Labor Annex 2 track (accessibility tables).

Trust gate: 8 tables / 40 rows with the expected per-section row counts,
2 columns everywhere, non-empty cells, linearization byte-reproducible from
the committed cells, verbatim/hash consistency across layers, and the
regulation linkage (regulation article (9) implements law art 28 — the
disability-accommodation article this annex serves)."""
from __future__ import annotations

import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "labor", "annex2", "official_source",
                   "labor_annex2_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "labor", "annex2", "verified",
                       "labor_annex2_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "labor_arabic_legal_llm",
                   "labor_annex2_accessibility_tables_llm.json")
STATUS = "HRSD_OFFICIAL_PDF_ACTUALTEXT_OCR_IMAGE_CROSS_CHECKED"
EXPECTED_ROWS = [4, 4, 2, 5, 6, 5, 5, 9]  # 8 tables, 40 rows total
SECTION_PREFIXES = ["أولاً", "أولاً", "أولاً", "ثانيًا", "ثالثًا", "رابعًا", "خامسًا", "سادسًا"]


def _table_text(t):
    cols = t["columns"]
    lines = [t["section_ar"] + ((" — " + t["sub_section_ar"]) if t.get("sub_section_ar") else "")]
    for row in t["rows"]:
        lines.append(" | ".join("%s: %s" % (cols[i], row[i]) for i in range(len(cols))
                                if str(row[i]).strip()))
    return "\n".join(lines)


def main():
    e = []
    for p in (SRC, RECORDS, LLM):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    tables = src["tables"]

    # [1] structure: 8 tables, expected rows, 2 columns, non-empty cells
    if len(tables) != len(EXPECTED_ROWS):
        e.append("[1] expected %d tables, found %d" % (len(EXPECTED_ROWS), len(tables)))
    for i, t in enumerate(tables):
        if len(t["rows"]) != EXPECTED_ROWS[i]:
            e.append("[1] table %d: %d rows != %d" % (i + 1, len(t["rows"]), EXPECTED_ROWS[i]))
        if len(t["columns"]) != 2:
            e.append("[1] table %d: expected 2 columns" % (i + 1))
        if not t["section_ar"].startswith(SECTION_PREFIXES[i]):
            e.append("[1] table %d: unexpected section %r" % (i + 1, t["section_ar"][:20]))
        for j, row in enumerate(t["rows"]):
            if len(row) != 2 or not str(row[0]).strip() or not str(row[1]).strip():
                e.append("[1] table %d row %d: malformed/empty cells" % (i + 1, j + 1))
    if sum(len(t["rows"]) for t in tables) != sum(EXPECTED_ROWS):
        e.append("[1] total rows != %d" % sum(EXPECTED_ROWS))
    if not src.get("notes"):
        e.append("[1] title-page notes missing")

    # [2] verified records: linearization byte-reproducible; boundary fields
    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != len(EXPECTED_ROWS):
        e.append("[2] %d verified records != %d" % (len(ver), len(EXPECTED_ROWS)))
    vmap = {r["article_key"]: r for r in ver}
    for i, t in enumerate(tables, start=1):
        k = "labor_annex2_table_%d" % i
        r = vmap.get(k, {})
        if r.get("article_text_verified") != _table_text(t):
            e.append("[2] %s: linearization not byte-reproducible from source cells" % k)
        if r.get("official_text_status") != STATUS:
            e.append("[2] %s: bad status" % k)
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[2] %s: %s must be False" % (k, f))

    # [3] LLM layer verbatim/hashes
    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != len(EXPECTED_ROWS) or len(recs) != len(EXPECTED_ROWS):
        e.append("[3] llm count != %d" % len(EXPECTED_ROWS))
    for r in recs:
        if r["article_text_ar"] != vmap[r["article_key"]]["article_text_verified"]:
            e.append("[3] %s: llm text != verified" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[3] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[3] %s: missing retrieval metadata" % r["article_key"])

    # [4] linkage: the regulation's accessibility article (implements law art 28,
    #     the provision this annex serves) exists in the committed regulation track
    reg_p = os.path.join(ROOT, "sources", "labor", "regulation", "verified",
                         "labor_regulation_verified_records.jsonl")
    linked = False
    for line in open(reg_p, encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            if 28 in r.get("implements_law_articles", []) and "التيسيرية" in r["article_text_verified"]:
                linked = True
    if not linked:
        e.append("[4] no regulation article implementing law art 28 mentions الترتيبات التيسيرية")

    if e:
        print("FAIL: %d error(s) in Labor Annex 2 track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Labor Annex 2 track — 8 accessibility tables (40 rows across 6 disability sections)")
    print("  - expected per-section row counts; 2 verbatim cells per row; no empty cells")
    print("  - linearization byte-reproducible from committed cells; hashes consistent")
    print("  - linkage verified: the regulation's law-art-28 accessibility article references الترتيبات التيسيرية")
    print("  - Arabic governs; recovered from the PDF's own /ActualText, OCR+image verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
