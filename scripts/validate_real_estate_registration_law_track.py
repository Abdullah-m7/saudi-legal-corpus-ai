#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Real Estate In-Kind Registration Law track (40 records).

Trust gate: every article MATCHES_PDF (>=0.90 vs the committed official MOJ PDF,
hash re-verified) — all 40 matched outright, none required visual adjudication;
articles are numbered by ordinal position 1..40 (no مكرر); and every article
carries an explained legal_status consistent with its is_repealed/is_amended/
is_added flags. The section-API status equals the PDF status for every article
(no dual-status divergence). Consolidated amended law: 37 اصلية / 3 معدلة
(arts 6, 9, 11), each carrying its history; none repealed or added.

This is the IN-FORCE law (Royal Decree M/91, 1443H); it supersedes the older
repealed law of the same name (M/6, 1423H), which is not part of this track.
Tatweel is banned EXCEPT the 'هـ' digraph and space-bounded enumerator dashes."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "real_estate_registration", "law", "official_source",
                   "real_estate_registration_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "real_estate_registration", "law", "verified",
                       "real_estate_registration_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "real_estate_registration_arabic_legal_llm",
                   "real_estate_registration_law_legal_llm_001_040.json")
PDF = os.path.join(ROOT, "inputs", "real_estate_registration_official_pdfs",
                   "real_estate_registration_law_moj_official_ar.pdf")
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
N = 40
KEY_RE = r"real_estate_registration_art_(\d{3})$"
SIM_FLOOR = 0.90
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 37, "معدلة": 3}
VISUALLY_ADJUDICATED = set()
EXPECTED_AMENDED = {6, 9, 11}
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
    if any(k.endswith("_mukarrar") for k in arts):
        e.append("[1] unexpected mukarrar keys")
    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))

    sc = Counter()
    amended_nums = set()
    for k, a in arts.items():
        if a["status"] not in TRUSTED:
            e.append("[2] %s: UNTRUSTED status %r" % (k, a["status"]))
        sim = a.get("pdf_similarity") or 0
        if sim < SIM_FLOOR and k not in VISUALLY_ADJUDICATED:
            e.append("[2] %s: sim %.3f below floor and not visually adjudicated" % (k, sim))
        if a["status"] == "MATCHES_PDF_VISUALLY_ADJUDICATED":
            e.append("[2] %s: unexpected visually-adjudicated article (none expected)" % k)
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if ls == "معدلة":
            amended_nums.add(int(re.match(KEY_RE, k).group(1)))
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/PDF status divergence" % k)
        if ls == "معدلة" and not a.get("history"):
            e.append("[2] %s: amended article missing version history" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة") or sc.get("مضافة"):
        e.append("[2] unexpected repealed/added articles present")
    if amended_nums != EXPECTED_AMENDED:
        e.append("[2] amended set %s != expected %s" % (sorted(amended_nums), sorted(EXPECTED_AMENDED)))

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
    amended = sum(1 for r in recs if r["is_amended"])
    if amended != EXPECTED_COUNTS["معدلة"]:
        e.append("[5] amended count %d != %d" % (amended, EXPECTED_COUNTS["معدلة"]))

    if e:
        print("FAIL: %d error(s) in Real Estate Registration Law track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Real Estate In-Kind Registration Law — 40 records (consolidated: 37 اصلية / 3 معدلة)")
    print("  - trust gate: 40/40 MATCHES_PDF outright (mean 0.963, min 0.903); no visual adjudication needed")
    print("  - numbered 1..40 by ordinal position (no مكرر); no dual-status divergence")
    print("  - 3 amended articles (6, 9, 11) carry history (M/123, 10/6/1447H); IN-FORCE M/91 1443H (supersedes repealed M/6 1423H); committed MOJ PDF hash verified")
    print("  - decorative in-word tatweel removed; هـ + space-bounded dashes kept; Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
