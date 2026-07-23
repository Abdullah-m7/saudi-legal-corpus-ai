#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Saudi Arabian
E-Commerce Law track (20 records: 20 اصلية, 0 معدلة, 0 مضافة, 0 ملغاة; a FLAT
regulation with no chapters/parts -- the issuing Ministry's own metadata states
"عدد الأبواب: 0 | عدد الفصول: 0 | عدد المواد: 20").

VERIFICATION TIER -- see the generator's module docstring and
sources/ecommerce/regulation/official_source/ecommerce_regulation_official_source.json's
verification_methodology_note for the full account: laws.boe.gov.sa was checked
FIRST (per this corpus's standard methodology) but returned HTTP 503 this pass
and, more fundamentally, has NO dedicated lawId page for this Implementing
Regulation at all (only for the base E-Commerce Law). The PRIMARY source actually
used is the issuing Ministry's OWN official page (mc.gov.sa, a born-digital HTML
page), cross-verified word-for-word against the Ministry's own official scanned
PDF (direct visual reading), and against qanoniah.com / lexismiddleeast.com /
argaam.com / mithaq.com.sa for decree number/date/article-count. This validator
does not re-adjudicate any of that; it only checks internal self-consistency of
the text this track ingests, and that every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "ecommerce", "regulation", "official_source",
                   "ecommerce_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "ecommerce", "regulation", "verified",
                       "ecommerce_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "ecommerce", "regulation", "verified",
                       "ecommerce_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "ecommerce_regulation_arabic_legal_llm",
                   "ecommerce_regulation_legal_llm_001_020.json")
N = 20
KEY_RE = r"ecommerce_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 20, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 0  # flat regulation: no أبواب/فصول

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
    "ecommerce_regulation_boe_no_dedicated_page",
    "ecommerce_regulation_resolution_number_labeled_transaction",
    "ecommerce_regulation_resolution_header_spelling_variant",
    "ecommerce_regulation_preamble_provenance",
    "ecommerce_regulation_amendment_consultation_no_enacting_resolution",
    "ecommerce_regulation_gazette_hijri_date_not_pinpointed",
    "ecommerce_regulation_inline_article_subtitles_preserved",
    "ecommerce_regulation_display_normalization",
}
AR = "ء-ي"
TASHKEEL_RE = re.compile("[ً-ْٰ]")
ARABIC_INDIC_RE = re.compile("[٠-٩۰-۹]")


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

    # This regulation is FLAT: chapter_structure must be empty and there must be
    # no chapters (Ministry metadata: عدد الأبواب 0 / عدد الفصول 0).
    chs = src.get("chapter_structure")
    if chs is None:
        e.append("[1c] chapter_structure key must be present (empty list)")
    elif len(chs) != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d chapters (flat regulation), got %d"
                 % (EXPECTED_TOP_LEVEL_CHAPTERS, len(chs)))

    # article numbers must be exactly 1..N, contiguous, no mukarrar
    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != list(range(1, N + 1)):
        e.append("[1b] article numbers not contiguous 1..%d: %s" % (N, nums))

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
        if a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section_status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        # flat regulation: section_ar must be EMPTY (no chapters)
        if a.get("section_ar"):
            e.append("[2] %s: section_ar must be empty for this flat regulation" % k)
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
        # display-normalization regression guards (each corresponds to a disclosed
        # normalization step). Arabic-Indic digits must have been converted;
        # tashkeel must have been stripped; hidden bidi marks must be gone.
        if ARABIC_INDIC_RE.search(a["text"]):
            e.append("[2g] %s: residual Arabic-Indic digit (should be normalized to Western)" % k)
        if TASHKEEL_RE.search(a["text"]):
            e.append("[2g] %s: residual tashkeel/harakat (should be stripped)" % k)
        for z in ("‏", "‎", "‌", "‍", "﻿"):
            if z in a["text"]:
                e.append("[2g] %s: residual hidden bidi/zero-width mark U+%04X" % (k, ord(z)))

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

    # metadata anchors established this pass
    if src.get("decree") != "قرار وزير التجارة والاستثمار رقم (200)" \
            or src.get("decree_date_hijri") != "19/5/1441":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Ministerial Resolution "
                 "200, 19/5/1441H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (founding text, no confirmed "
                 "amendment incorporated)")
    # preamble MUST be present (unlike food_regulation), sourced from the scanned
    # resolution page; it must carry the resolution number and the minister's name.
    pre = src.get("preamble_ar")
    if not pre:
        e.append("[2j] preamble_ar must be present (transcribed from the official scanned "
                 "resolution page; see known_unresolved_discrepancies)")
    else:
        if "200" not in pre:
            e.append("[2j] preamble_ar must reference resolution number 200")
        if "القصبي" not in pre:
            e.append("[2j] preamble_ar must name the issuing minister (القصبي)")
        if "الخامسة والعشرين" not in pre:
            e.append("[2j] preamble_ar must cite Article 25 basis (الخامسة والعشرين)")

    # spot-checks anchoring the ingested text
    art1 = arts.get("ecommerce_regulation_art_001", {})
    if art1.get("number_label_ar") != "المادة الأولى":
        e.append("[2j] Article 1 number_label_ar must be 'المادة الأولى'")
    if "التعريفات" not in art1.get("text", "") or "م/126" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected definitions/basis anchors (التعريفات / م/126)")
    art18 = arts.get("ecommerce_regulation_art_018", {})
    if "المنصات" not in art18.get("text", "") and "الوساطة" not in art18.get("text", ""):
        e.append("[2j] Article 18 missing expected intermediary-platform content (الوساطة)")
    art20 = arts.get("ecommerce_regulation_art_020", {})
    if art20.get("number_label_ar") != "المادة العشرون":
        e.append("[2j] Article 20 number_label_ar must be 'المادة العشرون'")
    if "الجريدة الرسمية" not in art20.get("text", ""):
        e.append("[2j] Article 20 (publication/effect) missing expected 'الجريدة الرسمية'")

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
    if llm.get("article_range") != [1, N]:
        e.append("[5] llm article_range != [1, %d]" % N)
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
        print("FAIL: %d error(s) in E-Commerce Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Saudi Arabian E-Commerce Law")
    print("  - 20 records: 20 اصلية, 0 معدلة, 0 مضافة, 0 ملغاة (flat regulation, no chapters)")
    print("  - VERIFICATION TIER: laws.boe.gov.sa checked first but returned HTTP 503 this pass")
    print("    and confirmed to have no dedicated lawId page for this Implementing Regulation at")
    print("    all; PRIMARY source is the issuing Ministry's OWN official page (mc.gov.sa,")
    print("    born-digital), cross-verified word-for-word against the Ministry's own official")
    print("    scanned PDF (direct visual reading of articles 1-4 and 18), and against")
    print("    qanoniah.com, lexismiddleeast.com, argaam.com and mithaq.com.sa")
    print("  - Ministerial Resolution No. (200), 19/5/1441H, Minister Dr. Majid Al-Qassabi,")
    print("    under Article 25 of the E-Commerce Law (Royal Decree M/126, 7/11/1440H)")
    print("  - Article count 20 (vs 26 for the base Law) confirmed four ways; NO predecessor")
    print("    regulation repealed/superseded (the base Law itself dates only to 1440H)")
    print("  - An amendment public-consultation exists (refund mechanism) but NO enacting")
    print("    amending resolution was confirmable this pass -- all 20 articles recorded اصلية")
    print("  - Display-layer normalization disclosed: Arabic-Indic->Western digits, tashkeel")
    print("    stripped, hijri 'هـ' preserved, hidden bidi marks removed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
