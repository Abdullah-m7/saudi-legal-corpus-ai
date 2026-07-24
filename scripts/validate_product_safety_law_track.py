#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Product Safety Law track (نظام سلامة
المنتجات; 37 records, ALL اصلية, 0 معدلة, 0 ملغاة, 0 مضافة; 9 أبواب).

VERIFICATION TIER -- see the generator's module docstring and
sources/product_safety/law/official_source/product_safety_law_official_source.json's
verification_methodology_note for the full account: decree number CORRECTED
from the coverage-gap-map's unconfirmable "M/148" to the multi-source
(including an OFFICIAL Umm al-Qura Gazette citation) confirmed Royal Decree
M/36 (29/1/1446H). This decree's Clause Two separately approved the wholly
distinct Standards and Quality Law (track_id: standards_quality) -- checked
here only for cross-reference consistency, not re-ingested. TIER_2: full
text from qanoonsa.com cross-checked against nezams.com (Article 5 sourced
from nezams.com instead due to a qanoonsa markup gap; chapter 4 heading
sourced from qanoonsa.com due to a nezams markup gap), plus an official Umm
al-Qura Gazette notice quoting Article 36 verbatim. laws.boe.gov.sa was
unreachable this pass. This validator does not re-adjudicate provenance; it
only checks internal self-consistency and that every discrepancy is still
recorded.

MATERIAL FACTS checked: 9 أبواب (chapter_structure), continuous 1-37
numbering, all articles اصلية (no amendments), no named-predecessor repeal,
the shared-decree relationship with standards_quality is documented, and
Article 10 note about the sibling law's legitimate Latin "SASO" acronym is
NOT expected to appear in THIS law's own text (checked separately)."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "product_safety", "law", "official_source",
                   "product_safety_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "product_safety", "law", "verified",
                       "product_safety_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "product_safety", "law", "verified",
                       "product_safety_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "product_safety_arabic_legal_llm",
                   "product_safety_law_legal_llm_001_037.json")
N = 37
KEY_RE = r"product_safety_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 37, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_CHAPTERS = 9
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
STATUS_MAIN = ("UQN_OFFICIAL_GAZETTE_DECREE_M36_CITATION_CONFIRMED_X_QANOONSA_PRIMARY_TEXT_"
               "X_NEZAMS_CROSS_VERIFIED_BOE_LAWID_UNREACHABLE")
STATUS_ART5 = ("UQN_OFFICIAL_GAZETTE_DECREE_M36_CITATION_CONFIRMED_X_NEZAMS_PRIMARY_TEXT_"
               "QANOONSA_MARKUP_GAP_AT_ART5_CROSS_VERIFIED_BOE_LAWID_UNREACHABLE")
FLAGGED_DISCREPANCY_KEYS = {
    "product_safety_decree_number_corrected_from_m148_to_m36",
    "product_safety_shared_decree_with_standards_quality_law",
    "product_safety_boe_lawid_not_confirmed_live_unreachable",
    "product_safety_article5_source_flip_qanoonsa_markup_gap",
    "product_safety_chapter4_heading_recovered_from_qanoonsa",
    "product_safety_saso_english_acronym_verbatim_in_article10",
    "product_safety_no_named_predecessor_repeal",
    "product_safety_implementing_regulation_out_of_scope",
    "product_safety_no_amendments_found_as_of_2026",
    "product_safety_gregorian_date_cross_source_note",
    "product_safety_tashkeel_and_normalization",
}
AR = "ء-ي"
HARAKAT = re.compile(r"[ً-ْٰٕٓٔ]")


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

    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))
    if src.get("article_count") != N:
        e.append("[1] article_count field != %d" % N)
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)

    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != list(range(1, N + 1)):
        e.append("[1b] article numbers not a clean 1..%d sequence: %s" % (N, nums))

    chapters = src.get("chapter_structure") or []
    if len(chapters) != EXPECTED_CHAPTERS:
        e.append("[1c] expected %d أبواب, got %d" % (EXPECTED_CHAPTERS, len(chapters)))
    for c in chapters:
        if not c.get("label_ar", "").startswith("الباب"):
            e.append("[1c] chapter entry %r: expected a باب label" % c)
        if not c.get("title_ar", "").strip():
            e.append("[1c] chapter entry %r: missing title_ar" % c)

    sc = Counter()
    for k, a in arts.items():
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected structure/section status divergence" % k)
        expected_status = STATUS_ART5 if k == "product_safety_law_art_005" else STATUS_MAIN
        if a.get("status") != expected_status:
            e.append("[2] %s: expected status %r, got %r" % (k, expected_status, a.get("status")))
        if not a["text"].strip():
            e.append("[2] %s: empty text" % k)
        # SASO's Latin acronym is a confirmed, legitimate exception -- but only in the
        # SIBLING law (standards_quality) Article 10; this law's own text must be Latin-free.
        if re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: unexpected latin/html leftovers in Product Safety Law text" % k)
        if not a.get("section_ar", "").strip():
            e.append("[2] %s: missing section_ar (expected a باب/chapter title)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly)" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if a.get("history"):
            e.append("[2i] %s: no amendments expected; history must be empty" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the tier")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))

    ah = src.get("amendment_history")
    if not ah:
        e.append("[2k] missing amendment_history (must record founding decree)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in ah)
        if "م/36" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/36")
        if any("148" in str(h.get("decree", "")) for h in ah):
            e.append("[2k] amendment_history must NOT reference the unconfirmed م/148")

    # spot-checks anchoring key facts
    art1 = arts.get("product_safety_law_art_001", {}).get("text", "")
    if "نظام سلامة المنتجات" not in art1 or "المشغل الاقتصادي" not in art1:
        e.append("[2j] Article 1 missing expected definitions")
    art5 = arts.get("product_safety_law_art_005", {}).get("text", "")
    if "تحظر صناعة المنتجات غير الآمنة" not in art5:
        e.append("[2j] Article 5 missing expected safety-prohibition clause")
    art34 = arts.get("product_safety_law_art_034", {}).get("text", "")
    for token in ("عشرة ملايين", "الإنذار", "إغلاق المنشأة"):
        if token not in art34:
            e.append("[2j] Article 34 (penalties) missing expected token %r" % token)
    art36 = arts.get("product_safety_law_art_036", {}).get("text", "")
    if "تسعين" not in art36 or "اللوائح" not in art36:
        e.append("[2j] Article 36 missing expected implementing-regulation mandate")
    art37 = arts.get("product_safety_law_art_037", {}).get("text", "")
    if "تسعين" not in art37:
        e.append("[2j] Article 37 missing expected 90-day effective-date clause")

    # NO named-predecessor repeal anywhere; only the generic conflict clause in Art 37
    for k, a in arts.items():
        if re.search(r"يلغي نظام|يلغى نظام|إلغاء نظام|تحل محل نظام", a["text"]):
            e.append("[2j] %s: unexpected NAMED repeal clause in a law with none confirmed" % k)

    if src.get("decree") != "المرسوم الملكي رقم م/36" or src.get("decree_date_hijri") != "29/1/1446":
        e.append("[2j] decree/decree_date_hijri mismatch with Royal Decree M/36, 29/1/1446H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (no confirmed amendments)")
    pre = src.get("preamble_ar", "")
    if not pre or "نظام سلامة المنتجات" not in pre or "نظام المواصفات والجودة" not in pre:
        e.append("[2j] preamble_ar must reference BOTH clauses of the joint decree M/36")
    if "148" in src.get("decree", ""):
        e.append("[2j] decree field must not contain the unconfirmed م/148")

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
        if r.get("legal_status_ar") != a.get("legal_status_ar"):
            e.append("[4] %s: legal_status_ar mismatch" % r["article_key"])
        if r.get("is_amended"):
            e.append("[4] %s: is_amended must be False (no amendments in this law)" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")
    if summary.get("consolidated_amended_law") is not False:
        e.append("[4b] summary consolidated_amended_law must be False")

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
        if r.get("source_trust", {}).get("source_status") != a["status"].lower():
            e.append("[5] %s: llm record source_status mismatch in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Product Safety Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Saudi Product Safety Law (نظام سلامة المنتجات)")
    print("  - 37 records: ALL اصلية (no confirmed amendments), 0 ملغاة, 0 مضافة")
    print("  - 9 أبواب (chapters), continuous numbering 1-37")
    print("  - VERIFICATION TIER: TIER_2 -- official Umm al-Qura Gazette notice quotes the")
    print("    decree (M/36, 29/1/1446H) AND Article 36 verbatim; full text from qanoonsa.com")
    print("    cross-checked against nezams.com; laws.boe.gov.sa unreachable this pass")
    print("  - Royal Decree M/36 (29/1/1446H / 5 Aug 2024G) CORRECTED from the coverage-gap-map's")
    print("    unconfirmable M/148; CoM Resolution 93 (24/1/1446H); Umm al-Qura Issue 5043")
    print("    (16/8/2024G)")
    print("  - Decree M/36's Clause Two separately approved the DISTINCT Standards and Quality")
    print("    Law (track_id: standards_quality) -- two different statutes, one joint decree")
    print("  - NO named-predecessor repeal (Article 37 is a generic conflict clause only)")
    print("  - Follow-up candidate NOT ingested: Implementing Regulation (Minister of Commerce")
    print("    Decision 097, 18/5/1446H)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
