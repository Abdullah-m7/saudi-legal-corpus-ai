#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Law of Sharia Procedure track (243 records).

Trust gate: every article MATCHES_PDF (>=0.90 vs the committed official MOJ
PDF, hash re-verified), the numbered sequence is a complete 1..242 plus one
مكرر, and every article carries an explained legal_status (اصلية/معدلة/ملغاة/
مضافة) consistent with its is_repealed/is_amended/is_added flags. This is a
consolidated amended law: repealed articles keep their full text and are
flagged, not deleted. Tatweel is banned EXCEPT the 'هـ' digraph (fifth-item
enumerator + Hijri-date abbreviation) and space-bounded enumerator dashes."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "sharia_procedure", "law", "official_source",
                   "sharia_procedure_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "sharia_procedure", "law", "verified",
                       "sharia_procedure_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "sharia_procedure_arabic_legal_llm",
                   "sharia_procedure_law_legal_llm_001_243.json")
PDF = os.path.join(ROOT, "inputs", "sharia_procedure_official_pdfs",
                   "sharia_procedure_law_moj_official_ar.pdf")
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
N = 243
SIM_FLOOR = 0.90
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 153, "معدلة": 14, "ملغاة": 75, "مضافة": 1}
AR = "ء-ي"


def _bad_tatweel(text):
    """Count tatweel runs that are NOT part of the هـ digraph and NOT space-bounded."""
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

    # [1] structure: complete 1..242 numbered + one 224-مكرر
    nums = sorted(int(re.match(r"mur_law_art_(\d{3})", k).group(1)) for k in arts
                  if not k.endswith("_mukarrar"))
    if nums != list(range(1, 243)):
        e.append("[1] numbered articles not a complete 1..242 sequence")
    muk = [k for k in arts if k.endswith("_mukarrar")]
    if muk != ["mur_law_art_224_mukarrar"]:
        e.append("[1] mukarrar keys != [224]: %s" % muk)
    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))

    # [2] trust gate: MATCHES_PDF + floor + explained status + no bad tatweel/latin
    from collections import Counter
    sc = Counter()
    for k, a in arts.items():
        if a["status"] != "MATCHES_PDF":
            e.append("[2] %s: UNTRUSTED verification status %r" % (k, a["status"]))
        if (a.get("pdf_similarity") or 0) < SIM_FLOOR:
            e.append("[2] %s: similarity below %.2f" % (k, SIM_FLOOR))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %d != %d" % (st, sc.get(st), want))
    # art 61 source typo kept verbatim
    if arts.get("mur_law_art_061", {}).get("number_label_ar") != "المادية الحادية والستون":
        e.append("[2] art 61 source-typo label not preserved verbatim")

    # [3] committed PDF hash
    if hashlib.sha256(open(PDF, "rb").read()).hexdigest() != src["provenance"]["pdf_sha256"]:
        e.append("[3] committed MOJ PDF sha256 mismatch")

    # [4] verified records: flags consistent with legal_status; verbatim; boundaries
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

    # [5] LLM layer verbatim/hashes
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
    repealed = sum(1 for r in recs if r["is_repealed"])
    if repealed != EXPECTED_COUNTS["ملغاة"]:
        e.append("[5] repealed count %d != %d" % (repealed, EXPECTED_COUNTS["ملغاة"]))

    if e:
        print("FAIL: %d error(s) in Sharia Procedure Law track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Law of Sharia Procedure — 243 records (consolidated amended text: 153 اصلية / 14 معدلة / 75 ملغاة / 1 مضافة)")
    print("  - trust gate: every article MATCHES_PDF >= %.2f; every status explained; flags consistent" % SIM_FLOOR)
    print("  - complete 1..242 + المادة (224) مكرر; committed official MOJ PDF hash verified")
    print("  - repealed articles keep full text and are flagged (not deleted), mirroring the official source")
    print("  - decorative in-word tatweel removed; هـ enumerator/Hijri + enumerator dashes kept; Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
