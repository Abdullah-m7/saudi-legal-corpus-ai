#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Executive Regulation on Controls for
Preparing and Implementing Environmental Emergency and Disaster
Preparedness and Response Plans track (اللائحة التنفيذية لضوابط إعداد
وتنفيذ خطط التأهب والاستجابة لحالات الطوارئ والكوارث البيئية).

12 records: 11 numbered articles (المادة الأولى .. الحادية عشرة, no chapter
division) + 1 appendix-type record (الجدول (١) المخالفات والعقوبات، 14
rows). All 12 اصلية.

VERIFICATION TIER: TIER_1 -- see the generator docstring and the
official_source JSON's verification_methodology_note: full text fetched
directly from the Umm Al-Qura Official Gazette's own HTML rendering, the
official publication of record for Saudi laws/regulations. This validator
only checks internal self-consistency of the ingested text and that every
discrepancy is disclosed.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "environmental_emergency_response",
                   "official_source",
                   "environmental_emergency_response_reg_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "environmental_emergency_response",
                       "verified",
                       "environmental_emergency_response_reg_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "environmental_emergency_response",
                       "verified",
                       "environmental_emergency_response_reg_verified_summary.json")
LLM = os.path.join(ROOT, "data",
                   "environmental_emergency_response_reg_arabic_legal_llm",
                   "environmental_emergency_response_reg_legal_llm_001_012.json")

N_ARTICLES = 11
N_APPENDICES = 1
N_RECORDS = 12
ART_RE = r"environmental_emergency_response_reg_art_(\d{3})$"
APP_RE = r"environmental_emergency_response_reg_appendix_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 12, "معدلة": 0, "ملغاة": 0, "مضافة": 0}

FLAGGED_DISCREPANCY_KEYS = {
    "environmental_emergency_response_reg_no_decision_number",
    "environmental_emergency_response_reg_no_pdf_found",
}
AR = "ء-ي"
TASHKEEL = re.compile("[ً-ٰٟ]")  # excludes Arabic-Indic digits U+0660-0669


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
    for p in (SRC, RECORDS, SUMMARY, LLM):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    # [1] structure counts
    if len(arts) != N_RECORDS:
        e.append("[1] %d records != %d" % (len(arts), N_RECORDS))
    if src.get("article_count") != N_ARTICLES:
        e.append("[1] article_count field != %d" % N_ARTICLES)
    if src.get("appendix_count") != N_APPENDICES:
        e.append("[1] appendix_count field != %d" % N_APPENDICES)
    if src.get("record_count") != N_RECORDS:
        e.append("[1] record_count field != %d" % N_RECORDS)

    art_nums, app_nums = [], []
    for k, a in arts.items():
        ma, mp = re.match(ART_RE, k), re.match(APP_RE, k)
        if ma:
            art_nums.append(int(ma.group(1)))
            if a.get("is_appendix") is not False:
                e.append("[1] %s: article key must have is_appendix False" % k)
        elif mp:
            app_nums.append(int(mp.group(1)))
            if a.get("is_appendix") is not True:
                e.append("[1] %s: appendix key must have is_appendix True" % k)
        else:
            e.append("[1] %s: does not match article/appendix key pattern" % k)
    if sorted(art_nums) != list(range(1, N_ARTICLES + 1)):
        e.append("[1] article numbers not 1..%d: %s" % (N_ARTICLES, sorted(art_nums)))
    if sorted(app_nums) != list(range(1, N_APPENDICES + 1)):
        e.append("[1] appendix numbers not 1..%d: %s" % (N_APPENDICES, sorted(app_nums)))

    # [2] per-record content + status
    sc = Counter()
    for k, a in arts.items():
        if a.get("status") != "MATCHES_UQN_GAZETTE":
            e.append("[2] %s: expected status MATCHES_UQN_GAZETTE, got %r" % (k, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: structure_status divergence" % k)
        if ls != "اصلية":
            e.append("[2] %s: all records must be اصلية, got %r" % (k, ls))
        if a.get("history"):
            e.append("[2] %s: article-level history must be empty" % k)
        t = a.get("text", "")
        if not t.strip():
            e.append("[2] %s: empty text" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
        if not a.get("number_label_ar"):
            e.append("[2] %s: missing number_label_ar" % k)
        if TASHKEEL.search(t):
            e.append("[2] %s: residual tashkeel (should be stripped uniformly)" % k)
        if _bad_tatweel(t):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if "\xa0" in t:
            e.append("[2f] %s: residual non-breaking-space artifact" % k)
        if "​" in t or "‏" in t or "‎" in t:
            e.append("[2f] %s: residual zero-width/bidi artifact" % k)
        if "“" in t or "”" in t:
            e.append("[2f] %s: residual curly-quote artifact" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %d != %d" % (st, sc.get(st, 0), want))

    # [2c] chapter_structure coverage (articles 1-11, appendices 1-1)
    chs = src.get("chapter_structure") or []
    art_cov, app_cov = set(), set()
    for ch in chs:
        if "articles" in ch:
            lo, hi = (int(x) for x in ch["articles"].split("-"))
            art_cov |= set(range(lo, hi + 1))
        if "appendices" in ch:
            lo, hi = (int(x) for x in ch["appendices"].split("-"))
            app_cov |= set(range(lo, hi + 1))
    if art_cov != set(range(1, N_ARTICLES + 1)):
        e.append("[2c] chapter_structure article coverage != 1..%d: %s" % (N_ARTICLES, sorted(art_cov)))
    if app_cov != set(range(1, N_APPENDICES + 1)):
        e.append("[2c] chapter_structure appendix coverage != 1..%d: %s" % (N_APPENDICES, sorted(app_cov)))

    # [2d] methodology + discrepancies
    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))

    # [2j] anchor facts
    if src.get("decree") != "المرسوم الملكي رقم (م/165)" \
            or src.get("decree_date_hijri") != "19/11/1441":
        e.append("[2j] decree/decree_date_hijri mismatch with verified M/165, 19/11/1441H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("base_law_track") != "environmental_law":
        e.append("[2j] base_law_track must be 'environmental_law'")
    if src.get("gazette_publication_date_hijri") != "7/7/1445":
        e.append("[2j] gazette_publication_date_hijri must be 7/7/1445")

    art3 = arts.get("environmental_emergency_response_reg_art_003", {})
    if "الخطط الوطنية" not in art3.get("text", ""):
        e.append("[2j] Article 3 must address national plans (الخطط الوطنية)")
    penalties = arts.get("environmental_emergency_response_reg_appendix_001", {})
    if "5,000,000" not in penalties.get("text", ""):
        e.append("[2j] Penalties table must contain the 5,000,000-riyal maximum fine")

    # [4] verified records
    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N_RECORDS:
        e.append("[4] %d verified records != %d" % (len(ver), N_RECORDS))
    for r in ver:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[4] %s: article_key not in source" % r["article_key"]); continue
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N_RECORDS:
        e.append("[4b] summary record_count != %d" % N_RECORDS)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")

    # [5] LLM layer
    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N_RECORDS or len(recs) != N_RECORDS:
        e.append("[5] llm count != %d" % N_RECORDS)
    for r in recs:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[5] %s: article_key not in source" % r["article_key"]); continue
        if r["article_text_ar"] != a["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("text_summarized_or_paraphrased") is not False:
            e.append("[5] %s: text_summarized_or_paraphrased must be False" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Environmental Emergency Response Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Executive Regulation on Environmental Emergency/Disaster Preparedness and Response Plans")
    print("  - 12 records: 11 articles (no chapters) + 1 appendix (14-row penalties table);")
    print("    all 12 اصلية")
    print("  - Full text fetched directly from the Umm Al-Qura Official Gazette's own HTML")
    print("    rendering (the official publication of record for Saudi laws)")
    print("  - VERIFICATION TIER: TIER_1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
