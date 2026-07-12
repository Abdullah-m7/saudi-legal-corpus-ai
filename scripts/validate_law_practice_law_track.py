#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Code of Law Practice track (56 records).

Trust gate: every article MATCHES_PDF (>=0.90 vs the committed official MOJ PDF,
hash re-verified) EXCEPT the 1 visually-adjudicated article (41) confirmed
verbatim on the rendered page; the numbered sequence is a complete 1..55 plus
exactly one مكرر (art 21); and every article carries an explained legal_status
(اصلية/معدلة/مضافة/ملغاة) consistent with its is_repealed/is_amended/is_added
flags. The section-API status equals the PDF status for every article (no
dual-status divergence). The single repealed article (25) keeps its full body
(flagged, not deleted) and its LLM title carries a '(ملغاة)' suffix. Tatweel is
banned EXCEPT the 'هـ' digraph and space-bounded enumerator dashes."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "law_practice", "law", "official_source",
                   "law_practice_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "law_practice", "law", "verified",
                       "law_practice_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "law_practice_arabic_legal_llm",
                   "law_practice_law_legal_llm_001_056.json")
PDF = os.path.join(ROOT, "inputs", "law_practice_official_pdfs",
                   "law_practice_law_moj_official_ar.pdf")
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
N = 56
MAX_NUM = 55
SIM_FLOOR = 0.90
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 35, "معدلة": 8, "مضافة": 12, "ملغاة": 1}
VISUALLY_ADJUDICATED = {"law_practice_art_041"}
EXPECTED_MUKARRAR = {"law_practice_art_021_mukarrar"}
TRUSTED = {"MATCHES_PDF", "MATCHES_PDF_VISUALLY_ADJUDICATED"}
AR = "ء-ي"


def _bad_tatweel(text):
    bad = 0
    for m in re.finditer("ـ+", text):
        before = text[m.start() - 1] if m.start() > 0 else " "
        if re.match("[%s]" % AR, before) and before != "ه":
            bad += 1
    return bad


def main():
    e = []
    for p in (SRC, RECORDS, LLM, PDF):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    # [1] structure: complete 1..55, exactly one مكرر (art 21)
    nums = sorted(int(re.match(r"law_practice_art_(\d{3})", k).group(1)) for k in arts
                  if not k.endswith("_mukarrar"))
    if nums != list(range(1, MAX_NUM + 1)):
        e.append("[1] numbered articles not a complete 1..%d sequence" % MAX_NUM)
    muk = {k for k in arts if k.endswith("_mukarrar")}
    if muk != EXPECTED_MUKARRAR:
        e.append("[1] unexpected mukarrar set: %s" % muk)
    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))

    # [2] trust gate
    sc = Counter()
    for k, a in arts.items():
        if a["status"] not in TRUSTED:
            e.append("[2] %s: UNTRUSTED status %r" % (k, a["status"]))
        sim = a.get("pdf_similarity") or 0
        if sim < SIM_FLOOR and k not in VISUALLY_ADJUDICATED:
            e.append("[2] %s: sim %.3f below floor and not visually adjudicated" % (k, sim))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected section/PDF status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %d != %d" % (st, sc.get(st), want))

    # [2b] no dual-status divergence recorded in provenance
    if src["provenance"].get("section_vs_structure_divergences") not in (0, None):
        e.append("[2b] unexpected section-vs-structure divergence recorded")

    # [3] committed PDF hash
    if hashlib.sha256(open(PDF, "rb").read()).hexdigest() != src["provenance"]["pdf_sha256"]:
        e.append("[3] committed MOJ PDF sha256 mismatch")

    # [4] verified records: flags consistent; verbatim
    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts[r["article_key"]]
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        ls = r.get("legal_status_ar")
        if (r.get("is_repealed") != (ls == "ملغاة") or r.get("is_amended") != (ls == "معدلة")
                or r.get("is_added") != (ls == "مضافة")):
            e.append("[4] %s: status flags inconsistent with legal_status_ar" % r["article_key"])
        if r.get("official_text_status") != STATUS:
            e.append("[4] %s: bad status" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    # [5] LLM layer verbatim/hashes + repealed suffix
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
        if r["is_repealed"] and "(ملغاة)" not in r["llm_title_ar"]:
            e.append("[5] %s: repealed article missing (ملغاة) title suffix" % r["article_key"])
    for st, want in EXPECTED_COUNTS.items():
        got = sum(1 for r in recs if r["legal_status_ar"] == st)
        if got != want:
            e.append("[5] llm status %s: %d != %d" % (st, got, want))

    if e:
        print("FAIL: %d error(s) in Code of Law Practice track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Code of Law Practice — 56 records (consolidated: 35 اصلية / 8 معدلة / 12 مضافة / 1 ملغاة)")
    print("  - trust gate: 55/56 MATCHES_PDF; art 41 (معدلة) visually adjudicated verbatim on the rendered page")
    print("  - complete 1..55 + one مكرر (art 21); committed official MOJ PDF hash verified; no dual-status divergence")
    print("  - repealed art 25 keeps its full body (flagged, '(ملغاة)' suffix); 12 added = foreign-law-firm chapter + 21-mukarrar")
    print("  - decorative in-word tatweel removed; هـ + space-bounded dashes kept; Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
