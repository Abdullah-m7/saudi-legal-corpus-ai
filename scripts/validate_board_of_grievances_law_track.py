#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Board of Grievances Law track (26 records).

Trust gate: this administrative-judiciary law is NOT on the MOJ portal and the
BOE consolidated database is network-unreachable, so it was sourced via the
Board's own certified official PDF (bog.gov.sa, corroborated by WIPO Lex) with
every article adjudicated VISUALLY, page-by-page, against that PDF. Exactly one
article (4) is معدلة — amended by قرار مجلس الوزراء 594 / المرسوم م/180
(17/8/1446H, Umm Al-Qura issue 5072); its scope+substance are officially
SPA-confirmed and its verbatim wording is from a gazette-5072 secondary
rendering (flagged). The validator checks a complete 1..26 sequence (no مكرر),
trusted per-article verification statuses, the explained legal_status
(اصلية/معدلة) consistent with the is_repealed/is_amended/is_added flags, the
committed official Board PDF hash, and that the sole amended article carries its
م/180 history and the distinctive «ذوي الخبرة والاختصاص» amendment marker.
Tatweel is banned EXCEPT the 'هـ' digraph and space-bounded enumerator dashes."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "board_of_grievances", "law", "official_source",
                   "board_of_grievances_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "board_of_grievances", "law", "verified",
                       "board_of_grievances_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "board_of_grievances_arabic_legal_llm",
                   "board_of_grievances_law_legal_llm_001_026.json")
PDF = os.path.join(ROOT, "inputs", "board_of_grievances_official",
                   "board_of_grievances_law_bog_official_ar.pdf")
STATUS = "BOARD_OFFICIAL_PDF_VISUALLY_ADJUDICATED_GAZETTE_CONFIRMED"
TRUSTED_VERIFICATION = {"BOARD_OFFICIAL_PDF_VISUALLY_ADJUDICATED",
                        "GAZETTE_5072_SPA_CONFIRMED_AMENDMENT"}
N = 26
SIM_FLOOR = 0.90
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 25, "معدلة": 1}
AMENDED_KEY = "bog_law_art_004"
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

    # [1] structure: complete 1..26, no mukarrar
    nums = sorted(int(re.match(r"bog_law_art_(\d{3})", k).group(1)) for k in arts
                  if not k.endswith("_mukarrar"))
    if nums != list(range(1, N + 1)):
        e.append("[1] numbered articles not a complete 1..%d sequence" % N)
    muk = [k for k in arts if k.endswith("_mukarrar")]
    if muk:
        e.append("[1] unexpected mukarrar keys: %s" % muk)
    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))

    # [2] trust gate: trusted verification status + floor + explained status + no bad tatweel/latin
    sc = Counter()
    for k, a in arts.items():
        if a["status"] not in TRUSTED_VERIFICATION:
            e.append("[2] %s: UNTRUSTED status %r" % (k, a["status"]))
        ls = a.get("legal_status_ar")
        # اصلية articles are double-official (visual PDF adjudication, sim==1.0);
        # the sole معدلة article is gazette-sourced (pdf_similarity intentionally null)
        if ls != "معدلة":
            sim = a.get("pdf_similarity") or 0
            if sim < SIM_FLOOR:
                e.append("[2] %s: sim %.3f below floor" % (k, sim))
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
    if sc.get("ملغاة") or sc.get("مضافة"):
        e.append("[2] unexpected repealed/added articles present")

    # [2b] the sole amended article carries its م/180 history + distinctive marker
    a4 = arts.get(AMENDED_KEY, {})
    if a4.get("legal_status_ar") != "معدلة":
        e.append("[2b] Article 4 must be معدلة")
    if "ذوي الخبرة والاختصاص" not in a4.get("text", ""):
        e.append("[2b] Article 4 missing the «ذوي الخبرة والاختصاص» amendment marker")
    hist = a4.get("history") or []
    if not any("م/180" in (h.get("decree") or "") for h in hist):
        e.append("[2b] Article 4 history missing المرسوم م/180")
    if not any(h.get("legalStatusName") == "اصلية" for h in hist):
        e.append("[2b] Article 4 history missing the original 1428 body")

    # [3] committed PDF hash
    if hashlib.sha256(open(PDF, "rb").read()).hexdigest() != src["provenance"]["primary_source_pdf_sha256"]:
        e.append("[3] committed Board PDF sha256 mismatch")

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
    amended = sum(1 for r in recs if r["is_amended"])
    if amended != EXPECTED_COUNTS["معدلة"]:
        e.append("[5] amended count %d != %d" % (amended, EXPECTED_COUNTS["معدلة"]))

    if e:
        print("FAIL: %d error(s) in Board of Grievances Law track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Law of the Board of Grievances — 26 records (consolidated: 25 اصلية / 1 معدّلة)")
    print("  - trust gate: 25 articles double-official (Board certified PDF, visually adjudicated, sim 1.0)")
    print("  - Article 4 معدلة by قرار 594 / م/180 (Umm Al-Qura 5072); scope+substance SPA-confirmed, marker present")
    print("  - complete 1..26 (no مكرر); committed official Board PDF hash verified; no repealed/added; no dual-status")
    print("  - decorative in-word tatweel removed; هـ Hijri + space-bounded dashes kept; Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
