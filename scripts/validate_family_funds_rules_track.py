#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the القواعد التنظيمية للصناديق العائلية track.

36 records: 36 numbered articles, no appendix records. All اصلية.

VERIFICATION TIER: TIER_1 -- full text fetched directly from the Umm Al-Qura
Official Gazette's own server-rendered HTML page. This validator only checks
internal self-consistency of the ingested text and that every discrepancy is
disclosed.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "family_funds_rules", "official_source",
                   "family_funds_rules_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "family_funds_rules", "verified",
                       "family_funds_rules_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "family_funds_rules", "verified",
                       "family_funds_rules_verified_summary.json")
LLM = os.path.join(ROOT, "data", "family_funds_rules_arabic_legal_llm",
                   "family_funds_rules_legal_llm_001_036.json")

N_ARTICLES = 36
N_RECORDS = 36
ART_RE = r"family_funds_rules_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
FLAGGED_DISCREPANCY_KEYS = {"family_funds_rules_no_decision_number_in_source", "family_funds_rules_source_is_gazette_html_only"}
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
    for f, want in (("article_count", N_ARTICLES), ("appendix_count", 0),
                    ("record_count", N_RECORDS)):
        if src.get(f) != want:
            e.append("[1] %s field != %d" % (f, want))
    nums = []
    for k, a in arts.items():
        m = re.match(ART_RE, k)
        if not m:
            e.append("[1] %s: does not match article key pattern" % k); continue
        nums.append(int(m.group(1)))
        if a.get("is_appendix") is not False:
            e.append("[1] %s: is_appendix must be False" % k)
    EXPECTED_NUMBERS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
    MISSING_IN_SOURCE = []
    if sorted(nums) != EXPECTED_NUMBERS:
        e.append("[1] article numbers differ from the source's own numbering")
    if src.get("missing_article_numbers") != MISSING_IN_SOURCE:
        e.append("[1] declared missing_article_numbers != %s" % MISSING_IN_SOURCE)

    # [2] per-record content + status
    sc = Counter()
    for k, a in arts.items():
        if a.get("status") != "MATCHES_UQN_GAZETTE":
            e.append("[2] %s: expected status MATCHES_UQN_GAZETTE" % k)
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: structure_status divergence" % k)
        if ls != "اصلية":
            e.append("[2] %s: all records must be اصلية" % k)
        if a.get("history"):
            e.append("[2] %s: article-level history must be empty" % k)
        t = a.get("text", "")
        if not t.strip():
            e.append("[2] %s: empty text" % k)
        if len(t.strip()) < 15:
            e.append("[2] %s: suspiciously short text" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
        if not a.get("number_label_ar"):
            e.append("[2] %s: missing number_label_ar" % k)
        if TASHKEEL.search(t):
            e.append("[2] %s: residual tashkeel" % k)
        if _bad_tatweel(t):
            e.append("[2] %s: in-word decorative tatweel" % k)
        for bad, lbl in (("\xa0", "non-breaking space"), ("\u200b", "zero-width"),
                         ("\u200f", "bidi mark"), ("\u200e", "bidi mark"),
                         ("“", "curly quote"), ("”", "curly quote")):
            if bad in t:
                e.append("[2f] %s: residual %s artifact" % (k, lbl))
        if "نسخة تجريبية" in t or "الرئيسية القرارات" in t:
            e.append("[2f] %s: site navigation boilerplate leaked into article text" % k)
        if re.search(r"(?<!\sفي)(?<!\sمن)(?<!\sعلى)(?<!\sإلى)(?<!\sالى)(?<!\sوفق)(?<!\sحسب)"
                 r"(?<!\sضمن)(?<!\sوفقا)(?<!\sبحسب)(?<!\sوفقاً)(?<!\sبموجب)"
                 r"\s(الباب|الفصل)\s+(الأول|الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع|العاشر"
                 r"|(?:الحادي|الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع)\s+عشر"
                 r"|العشرون|التمهيدي)\s*:?\s*[^\n]{0,90}$", t):
            e.append("[2f] %s: trailing chapter heading leaked into article text" % k)
    if sc.get("اصلية", 0) != N_RECORDS:
        e.append("[2] اصلية count %d != %d" % (sc.get("اصلية", 0), N_RECORDS))

    # [2c] chapter_structure coverage
    cov = set()
    for ch in src.get("chapter_structure") or []:
        spec = ch.get("articles", "")
        if "-" in spec:
            lo, hi = (int(x) for x in spec.split("-"))
        elif spec.isdigit():
            lo = hi = int(spec)
        else:
            continue
        cov |= set(range(lo, hi + 1))
    if set(EXPECTED_NUMBERS) - cov:
        e.append("[2c] chapter_structure does not cover articles %s"
                 % sorted(set(EXPECTED_NUMBERS) - cov))

    # [2d] methodology + disclosed discrepancies
    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note")
    disc = src.get("known_unresolved_discrepancies") or []
    missing = FLAGGED_DISCREPANCY_KEYS - {d["article_key"] for d in disc}
    if missing:
        e.append("[2e] expected discrepancy entries missing: %s" % sorted(missing))

    # [2j] anchor facts
    if src.get("gazette_publication_date_hijri") != "12/7/1444":
        e.append("[2j] gazette_publication_date_hijri must be 12/7/1444")
    if src.get("gazette_publication_date_gregorian") != "2023-02-03":
        e.append("[2j] gazette_publication_date_gregorian must be 2023-02-03")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("document") != "القواعد التنظيمية للصناديق العائلية":
        e.append("[2j] document title mismatch")

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
        e.append("[4b] summary status_counts != source")

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
        print("FAIL: %d error(s) in Regulatory Rules for Family Funds track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Regulatory Rules for Family Funds")
    print("  - 36 records: 36 articles, no appendices; all 36 اصلية")
    print("  - Full text fetched directly from the Umm Al-Qura Official Gazette's own")
    print("    server-rendered HTML (the official publication of record for Saudi laws)")
    print("  - VERIFICATION TIER: TIER_1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
