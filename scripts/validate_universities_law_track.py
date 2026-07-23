#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Universities Law track (نظام الجامعات,
Royal Decree M/27, 2/3/1441H -- the fresh higher-education/universities law that
by its own Article 57 replaces/repeals-conflicting-provisions of the older
نظام مجلس التعليم العالي والجامعات, M/8, 4/6/1414H, phased in transitionally).

58 records: 58 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة (the Law has had no amendments);
14 chapters (فصول).

VERIFICATION TIER -- TIER_3. See the generator docstring and the source artifact's
verification_methodology_note for the full account: laws.boe.gov.sa was checked
FIRST (per standard methodology) but is unreachable this pass (HTTP 503 / connection
reset) and Wayback is egress-blocked (not circumvented); the verbatim text of all 58
articles was extracted from bibliotdroit.com (a clean born-digital HTML page) and
cross-verified article-by-article against the administering authority's own official
edition (cua.gov.sa PDF), with the 58-article/14-chapter structure re-confirmed by
moe.gov.sa. This validator does not re-adjudicate provenance; it only checks internal
self-consistency of the ingested text and that every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "universities", "law", "official_source",
                   "universities_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "universities", "law", "verified",
                       "universities_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "universities", "law", "verified",
                       "universities_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "universities_arabic_legal_llm",
                   "universities_law_legal_llm_001_058.json")
N = 58
KEY_RE = r"universities_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 58, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 14

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY = {}
for k in AMENDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_AMENDED
for k in ADDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_ADDED
FLAGGED_DISCREPANCY_KEYS = {
    "universities_law_boe_dedicated_page_exists_but_unreachable",
    "universities_law_named_repeal_of_predecessor_with_transitional_survival",
    "universities_law_fulltext_two_independent_sources_tier3",
    "universities_law_preamble_not_ingested_verbatim",
    "universities_law_second_shura_resolution_number_unconfirmed",
    "universities_law_tashkeel_stripped_display_layer",
    "universities_law_gregorian_date_not_pinpointed",
    "universities_law_chapter_division_is_fasl_not_bab",
    "universities_law_implementing_regulations_out_of_scope",
}
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


def _iter_chapter_ranges(chs):
    for ch in chs:
        lo, hi = (int(x) for x in ch["articles"].split("-"))
        yield (lo, hi)


def main():
    e = []
    for p in (SRC, RECORDS, SUMMARY, LLM):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))
    if src.get("article_count") != N:
        e.append("[1] article_count field != %d" % N)
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)

    chs = src.get("chapter_structure") or []
    n_top = len(chs)
    if n_top != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d chapters, got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

    covered = set()
    for lo, hi in _iter_chapter_ranges(chs):
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] article %d covered by more than one chapter range" % n)
            covered.add(n)
    if covered != set(range(1, N + 1)):
        missing = sorted(set(range(1, N + 1)) - covered)
        extra = sorted(covered - set(range(1, N + 1)))
        if missing:
            e.append("[1c] chapter_structure missing article(s): %s" % missing[:20])
        if extra:
            e.append("[1c] chapter_structure covers out-of-range article(s): %s" % extra[:20])
    # every chapter label must be a فصل (not باب) -- governing division term
    for ch in chs:
        if not str(ch.get("label_ar", "")).startswith("الفصل"):
            e.append("[1c] chapter label not a فصل: %r" % ch.get("label_ar"))

    sc = Counter()
    for k, a in arts.items():
        expected_status = EXPECTED_STATUS_BY_KEY.get(k, STATUS_UNCHANGED)
        if a.get("status") != expected_status:
            e.append("[2] %s: expected status %r, got %r" % (k, expected_status, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected structure_status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if k in (AMENDED_KEYS | ADDED_KEYS) and not a.get("history"):
            e.append("[2] %s: amended/added article missing amendment_history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if k not in (AMENDED_KEYS | ADDED_KEYS) and a.get("history"):
            e.append("[2i] %s: non-amended/added article must have empty history[]" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        if re.search(r"[ً-ٰٟ]", a["text"]):
            e.append("[2g] %s: residual tashkeel/diacritics not stripped" % k)
        if re.search(r"[کیے]", a["text"]):
            e.append("[2g] %s: non-standard Arabic-presentation letter (Farsi yeh/keheh) present" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the distinct tier")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))

    if not src.get("amendment_history"):
        e.append("[2k] missing amendment_history (must record the founding M/27 decree)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "م/27" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/27")

    # spot-checks anchoring key facts established this pass
    if src.get("decree") != "المرسوم الملكي رقم (م/27)" \
            or src.get("decree_date_hijri") != "2/3/1441":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Decree M/27, 2/3/1441H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (the Law has no amendments)")
    if not src.get("council_of_ministers_decision") \
            or "183" not in src.get("council_of_ministers_decision", ""):
        e.append("[2j] council_of_ministers_decision must record Resolution 183")
    if not src.get("supersedes_ar") or "م/8" not in src.get("supersedes_ar", "") \
            or "التعليم العالي والجامعات" not in src.get("supersedes_ar", ""):
        e.append("[2j] supersedes_ar must record replacement of نظام مجلس التعليم العالي والجامعات (م/8)")
    if not src.get("preamble_ar") or "م/27" not in src.get("preamble_ar", ""):
        e.append("[2j] preamble_ar (issuing-context metadata) must be present and reference M/27")
    art1 = arts.get("universities_law_art_001", {})
    if "مجلس شؤون الجامعات" not in art1.get("text", "") \
            or "يقصد بالألفاظ والعبارات" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected definitions content")
    if art1.get("number_label_ar") != "المادة الأولى":
        e.append("[2j] Article 1 number_label_ar must be 'المادة الأولى'")
    art3 = arts.get("universities_law_art_003", {})
    if "شخصية اعتبارية مستقلة" not in art3.get("text", ""):
        e.append("[2j] Article 3 missing expected university-legal-personality content")
    art57 = arts.get("universities_law_art_057", {})
    art57_txt = art57.get("text", "")
    if "يحل هذا النظام محل" not in art57_txt or "التعليم العالي والجامعات" not in art57_txt \
            or "8" not in art57_txt or "1414" not in art57_txt:
        e.append("[2j] Article 57 must contain the named replace/repeal clause for نظام مجلس "
                 "التعليم العالي والجامعات (م/8, 4/6/1414هـ)")
    if art57.get("number_label_ar") != "المادة السابعة والخمسون":
        e.append("[2j] Article 57 number_label_ar must be 'المادة السابعة والخمسون', got %r"
                 % art57.get("number_label_ar"))
    art58 = arts.get("universities_law_art_058", {})
    art58_txt = art58.get("text", "")
    if "مائة وثمانين" not in art58_txt or "الجريدة الرسمية" not in art58_txt:
        e.append("[2j] Article 58 must contain the 180-day effectiveness clause")
    if art58.get("number_label_ar") != "المادة الثامنة والخمسون":
        e.append("[2j] Article 58 number_label_ar must be 'المادة الثامنة والخمسون', got %r"
                 % art58.get("number_label_ar"))

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[4] %s: article_key not found in source" % r["article_key"]); continue
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    for r in recs:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[5] %s: article_key not found in source" % r["article_key"]); continue
        if r["article_text_ar"] != a["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        expected_status = EXPECTED_STATUS_BY_KEY.get(r["article_key"], STATUS_UNCHANGED)
        if r.get("source_trust", {}).get("source_status") != expected_status.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Universities Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: The Saudi Universities Law (نظام الجامعات)")
    print("  - 58 records: 58 اصلية, 0 معدلة, 0 مضافة, 0 ملغاة (the Law has had no amendments)")
    print("  - 14 chapters (الفصل الأول..الرابع عشر) -- governing division term is الفصل, not الباب")
    print("  - CITATION: Royal Decree M/27, 2/3/1441H (Council of Ministers Resolution 183,")
    print("    1/3/1441H; Shura 61/239, 28/2/1440H; Umm al-Qura 11/3/1441H; in force 180 days")
    print("    after publication per Article 58).")
    print("  - NAMED REPEAL: Article 57 replaces & repeals-conflicting-provisions of the")
    print("    predecessor نظام مجلس التعليم العالي والجامعات (M/8, 4/6/1414H) -- phased in")
    print("    transitionally (old law kept in force for universities not yet covered).")
    print("  - VERIFICATION TIER: TIER_3 -- laws.boe.gov.sa checked first but unreachable this")
    print("    pass (HTTP 503 / connection reset), Wayback egress-blocked (not circumvented);")
    print("    full verbatim text from bibliotdroit.com (born-digital HTML), cross-verified")
    print("    article-by-article against the administering authority's own official edition")
    print("    (cua.gov.sa PDF); 58-article/14-chapter structure re-confirmed by moe.gov.sa.")
    print("  - Implementing regulations (Council of Universities' Affairs regulations, e.g. for")
    print("    private universities and foreign branches) exist and are flagged as companion")
    print("    candidates, NOT ingested this pass (one-instrument-per-pass).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
