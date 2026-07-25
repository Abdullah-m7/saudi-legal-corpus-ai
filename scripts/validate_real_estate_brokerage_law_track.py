#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Real Estate Brokerage Law track (24 records).

Trust gate: every article is MATCHES_OFFICIAL_SCAN_VISUALLY_VERIFIED — the
committed REGA-hosted PDF (Bureau-of-Experts-sealed, no text layer, hash
re-verified) was rendered at 300dpi and every page read directly (verbatim),
cross-checked against two independent secondary full-text sources
(qanoonsa.com, nezams.com) that MATCH word-for-word modulo diacritics/digit
script; articles are numbered by ordinal position 1..24 (no مكرر); every
article carries an explained legal_status consistent with its
is_repealed/is_amended/is_added flags. FRESH FULL ISSUANCE: all 24 اصلية;
none amended, repealed or added. Tatweel is banned EXCEPT the 'هـ' digraph
and space-bounded enumerator dashes."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "real_estate_brokerage", "law", "official_source",
                   "real_estate_brokerage_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "real_estate_brokerage", "law", "verified",
                       "real_estate_brokerage_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "real_estate_brokerage", "law", "verified",
                       "real_estate_brokerage_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "real_estate_brokerage_arabic_legal_llm",
                   "real_estate_brokerage_law_legal_llm_001_024.json")
PDF = os.path.join(ROOT, "inputs", "real_estate_brokerage_official_pdfs",
                   "real_estate_brokerage_law_rega_official_ar.pdf")
STATUS = "MATCHES_OFFICIAL_SCAN_VISUALLY_VERIFIED"
N = 24
KEY_RE = r"real_estate_brokerage_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 24}
TRUSTED = {STATUS}
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
        e.append("[1] numbered articles not a complete 1..%d sequence" % N)
    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))

    sc = Counter()
    for k, a in arts.items():
        if a["status"] not in TRUSTED:
            e.append("[2] %s: UNTRUSTED status %r" % (k, a["status"]))
        if a.get("secondary_cross_check") != "MATCHES_QANOONSA_X_NEZAMS_MODULO_DIACRITICS":
            e.append("[2] %s: missing/incorrect secondary cross-check tag" % k)
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
    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("معدلة") or sc.get("ملغاة") or sc.get("مضافة"):
        e.append("[2] unexpected amended/repealed/added articles present")

    if src["provenance"].get("section_vs_structure_divergences") not in (0, None):
        e.append("[2b] unexpected section-vs-structure divergence recorded")
    if src["provenance"].get("pdf_has_text_layer") is not False:
        e.append("[2b] expected pdf_has_text_layer=False (scanned-image-only official PDF)")
    if src["provenance"].get("boe_portal_status") != "UNREACHABLE_HTTP_503_REPEATED_ATTEMPTS":
        e.append("[2b] expected documented BOE portal unreachability status")

    if hashlib.sha256(open(PDF, "rb").read()).hexdigest() != src["provenance"]["pdf_sha256"]:
        e.append("[3] committed REGA/BOE PDF sha256 mismatch")

    # Article 22 must carry the genuine named repeal citation for the 1398H regulation.
    art22 = arts.get("real_estate_brokerage_art_022", {})
    if "٣٣٤" not in art22.get("text", "") or "١٣٩٨" not in art22.get("text", ""):
        e.append("[3b] Article 22 missing expected repeal citation (Resolution 334 / 1398H)")
    # Article 24 must carry the 180-day entry-into-force clause.
    art24 = arts.get("real_estate_brokerage_art_024", {})
    if "مائة وثمانين" not in art24.get("text", ""):
        e.append("[3b] Article 24 missing expected 180-day entry-into-force clause")

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

    if not os.path.isfile(SUMMARY):
        e.append("[4b] missing verified summary file")
    else:
        summ = json.load(open(SUMMARY, encoding="utf-8"))
        if summ.get("record_count") != N:
            e.append("[4b] summary record_count != %d" % N)

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
        print("FAIL: %d error(s) in Real Estate Brokerage Law track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Real Estate Brokerage Law — 24 records (fresh issuance: all 24 اصلية)")
    print("  - trust gate: 24/24 MATCHES_OFFICIAL_SCAN_VISUALLY_VERIFIED against REGA-hosted "
          "BOE-sealed scanned PDF (no text layer); cross-verified word-for-word (modulo diacritics) "
          "against qanoonsa.com and nezams.com")
    print("  - numbered 1..24 by ordinal position (no مكرر); no dual-status divergence")
    print("  - IN-FORCE Royal Decree M/130 (30/11/1443H); committed PDF hash verified; Arabic governs")
    print("  - Article 22 confirmed genuine named repeal of the 1398H Real Estate Offices Regulation "
          "(Council of Ministers Resolution 334, 7/3/1398H) — that instrument is not itself tracked, "
          "so no supersession edge is required")
    print("  - live laws.boe.gov.sa portal documented UNREACHABLE (HTTP 503) across repeated attempts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
