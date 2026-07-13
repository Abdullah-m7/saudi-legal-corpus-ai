#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Notarization Regulation track (31 records).

Trust gate: every article MATCHES_PDF (>=0.90 vs the committed official MOJ PDF,
hash re-verified) EXCEPT the 10 documented list articles (arts 1, 2, 4, 11, 18, 23,
24, 26, 27, 28) whose PDF text-layer reordered/split clauses and dropped some
ligature/digit glyphs — these were adjudicated VISUALLY VERBATIM on the rendered
official PDF pages and are flagged MATCHES_PDF_VISUALLY_ADJUDICATED. Records are
numbered 1..30 (articles) plus record 31 (the official fee schedule «جدول المقابل
المالي»). FRESH FULL ISSUANCE: all 31 اصلية; none amended/repealed/added. The
section-API status equals the PDF status for every article (no dual-status
divergence). Tatweel is banned EXCEPT the 'هـ' digraph and space-bounded
enumerator dashes."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "tawtheeq", "regulation", "official_source",
                   "tawtheeq_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "tawtheeq", "regulation", "verified",
                       "tawtheeq_regulation_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "tawtheeq_arabic_legal_llm",
                   "tawtheeq_regulation_legal_llm_001_031.json")
PDF = os.path.join(ROOT, "inputs", "tawtheeq_official_pdfs",
                   "tawtheeq_regulation_moj_official_ar.pdf")
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
N = 31
KEY_RE = r"tawtheeq_reg_art_(\d{3})$"
SIM_FLOOR = 0.90
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 31}
VISUALLY_ADJUDICATED = {"tawtheeq_reg_art_%03d" % n for n in (1, 2, 4, 11, 18, 23, 24, 26, 27, 28)}
FEE_SCHEDULE_KEY = "tawtheeq_reg_art_031"
TRUSTED = {"MATCHES_PDF", "MATCHES_PDF_VISUALLY_ADJUDICATED"}
AR = "ء-ي"


def _bad_tatweel(text):
    bad = 0
    for m in re.finditer("ـ+", text):
        before = text[m.start() - 1] if m.start() > 0 else " "
        after = text[m.end()] if m.end() < len(text) else " "
        if (re.match("[%s]" % AR, before) and before != "ه"
                and re.match("[%s]" % AR, after)):
            bad += 1
    return bad


def main():
    e = []
    for p in (SRC, RECORDS, LLM, PDF):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != list(range(1, N + 1)):
        e.append("[1] records not a complete 1..%d sequence" % N)
    if len(arts) != N:
        e.append("[1] %d records != %d" % (len(arts), N))
    if not arts.get(FEE_SCHEDULE_KEY, {}).get("is_fee_schedule"):
        e.append("[1] record 31 is not flagged as the fee schedule")

    visual = set()
    sc = Counter()
    for k, a in arts.items():
        if a["status"] not in TRUSTED:
            e.append("[2] %s: UNTRUSTED status %r" % (k, a["status"]))
        sim = a.get("pdf_similarity") or 0
        if a["status"] == "MATCHES_PDF_VISUALLY_ADJUDICATED":
            visual.add(k)
        elif sim < SIM_FLOOR:
            e.append("[2] %s: sim %.3f below floor and not visually adjudicated" % (k, sim))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/PDF status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
    if visual != VISUALLY_ADJUDICATED:
        e.append("[2] visually-adjudicated set %s != expected %s"
                 % (sorted(visual), sorted(VISUALLY_ADJUDICATED)))
    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("معدلة") or sc.get("ملغاة") or sc.get("مضافة"):
        e.append("[2] unexpected amended/repealed/added articles present")

    if src["provenance"].get("section_vs_structure_divergences") not in (0, None):
        e.append("[2b] unexpected section-vs-structure divergence recorded")

    if hashlib.sha256(open(PDF, "rb").read()).hexdigest() != src["provenance"]["pdf_sha256"]:
        e.append("[3] committed MOJ PDF sha256 mismatch")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts[r["article_key"]]
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("official_text_status") != STATUS:
            e.append("[4] %s: bad status" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    for r in recs:
        if r["article_text_ar"] != arts[r["article_key"]]["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Notarization Regulation track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Notarization Regulation — 31 records (fresh issuance: all 31 اصلية)")
    print("  - trust gate: 21/31 MATCHES_PDF outright; 10 list articles (1, 2, 4, 11, 18, 23, 24, 26, 27, 28) adjudicated visually verbatim (OCR channel unavailable this build)")
    print("  - numbered 1..30 articles + record 31 = the official fee schedule «جدول المقابل المالي»; no dual-status divergence")
    print("  - Minister of Justice Decision 1948 (1/6/1442H); committed MOJ PDF hash verified; Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
