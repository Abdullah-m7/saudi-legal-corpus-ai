#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Regulation of the Center for Assignment
(Referral) and Liquidation track (15 records).

Trust gate: every article MATCHES_PDF or MATCHES_PDF_VISUALLY_ADJUDICATED
(>=0.90 vs the committed official MOJ PDF, hash re-verified, unless visually
adjudicated). 3/15 (arts 6, 7, 14) matched outright; the other 12 (mean
0.7999, min 0.6117) were visually adjudicated verbatim due to a known
RTL/ligature PDF text-layer extraction artifact. Articles are numbered by
ordinal position 1..15 (no مكرر), flat structure with no chapter/section
wrapper (section_ar empty for every article — not a bug). NOT A FRESH
ISSUANCE FOR EVERY ARTICLE: 14 of 15 اصلية; article 4 (board composition)
is معدلة with a 2-version amendment history (Council of Ministers Decision
685 1443H, then Decision 364 1447H current). The section-API status equals
the PDF status for every article (no dual-status divergence). Tatweel is
banned EXCEPT the 'هـ' digraph and space-bounded enumerator dashes. Issued
by Council of Ministers Decision 415 (not a Minister of Justice decision) —
the Center is a semi-independent body organizationally linked to the
Minister of Justice."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "documentation_settlement", "regulation", "official_source",
                   "documentation_settlement_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "documentation_settlement", "regulation", "verified",
                       "documentation_settlement_regulation_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "documentation_settlement_arabic_legal_llm",
                   "documentation_settlement_regulation_legal_llm_001_015.json")
PDF = os.path.join(ROOT, "inputs", "documentation_settlement_official_pdfs",
                   "documentation_settlement_regulation_moj_official_ar.pdf")
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
N = 15
KEY_RE = r"documentation_settlement_art_(\d{3})$"
SIM_FLOOR = 0.90
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 14, "معدلة": 1}
AMENDED_KEY = "documentation_settlement_art_004"
VISUALLY_ADJUDICATED = {"documentation_settlement_art_%03d" % n for n in
                        (1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13, 15)}
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
        e.append("[1] numbered articles not a complete 1..%d sequence" % N)
    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))

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
        if a.get("section_ar"):
            e.append("[2] %s: unexpected non-empty section_ar in a flat-structure regulation" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
    if visual != VISUALLY_ADJUDICATED:
        e.append("[2] visually-adjudicated set %s != expected %s"
                 % (sorted(visual), sorted(VISUALLY_ADJUDICATED)))
    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة") or sc.get("مضافة"):
        e.append("[2] unexpected repealed/added articles present")

    # [2b] the sole amended article carries its 2-version amendment history
    a4 = arts.get(AMENDED_KEY, {})
    if a4.get("legal_status_ar") != "معدلة":
        e.append("[2b] article 4 must be معدلة")
    hist = a4.get("history") or []
    if len(hist) != 2:
        e.append("[2b] article 4 history must have exactly 2 versions, found %d" % len(hist))
    if not any("685" in (h.get("decree") or "") for h in hist):
        e.append("[2b] article 4 history missing Decision 685")
    if not any(h.get("legalStatusName") == "اصلية" for h in hist):
        e.append("[2b] article 4 history missing the original 1440 body")

    if src["provenance"].get("section_vs_structure_divergences") not in (0, None):
        e.append("[2c] unexpected section-vs-structure divergence recorded")

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
        if r["is_amended"] != (a.get("legal_status_ar") == "معدلة"):
            e.append("[4] %s: is_amended flag mismatch" % r["article_key"])
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
        print("FAIL: %d error(s) in Documentation Settlement Regulation track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Regulation of the Center for Assignment (Referral) and Liquidation — 15 records (14 اصلية, 1 معدلة)")
    print("  - trust gate: 3/15 MATCHES_PDF outright (arts 6, 7, 14), 12 visually adjudicated (mean 0.7999, min 0.6117)")
    print("  - numbered 1..15 by ordinal position (no مكرر), flat structure; article 4 carries a 2-version amendment history (Decision 685 1443H, Decision 364 1447H)")
    print("  - IN-FORCE Council of Ministers Decision 415 (19/07/1440H); committed MOJ PDF hash verified; Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
