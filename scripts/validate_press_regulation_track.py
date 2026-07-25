#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Press and
Publications Law track (اللائحة التنفيذية لنظام المطبوعات والنشر, Ministerial
Decision M/W/2759/1/M, 16/6/1422H; amended by Decision 91513, 9/11/1439H).

99 articles, all recorded as اصلية (consolidated current text -- the 1439H
amendment could not be attributed to specific articles from this source;
see known_unresolved_discrepancies). 7 أبواب (Article 1 sits before the
first named باب).

VERIFICATION TIER -- see the generator's module docstring and
sources/press_regulation/law/official_source/
press_regulation_official_source.json's verification_methodology_note for
the full account: TIER_2 -- Ministry of Media's own PDF, reached via a
Wayback Machine snapshot (live media.gov.sa unreachable this pass), all 99
articles vision-read in full (pdftotext/PyMuPDF scramble this PDF's text),
partially cross-checked against an Umm al-Qura Gazette article confirming
Article 69(c). This validator does not re-adjudicate any of this; it only
checks internal self-consistency of the text this track actually ingests,
and that every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "press_regulation", "law", "official_source",
                   "press_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "press_regulation", "law", "verified",
                       "press_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "press_regulation", "law", "verified",
                       "press_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "press_regulation_arabic_legal_llm",
                   "press_regulation_legal_llm_001_099.json")
N = 99
KEY_RE = r"press_reg_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 99, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 8  # Article-1-alone leaf range + 7 named أبواب

TOP_STATUS = ("TIER_2_MOM_WAYBACK_NOV2024_VISION_READ_FULL_X_UQN_GOV_SA_PARTIAL_"
              "CROSSCHECK_ART69_LIVE_MOM_UNREACHABLE_DIRECT")
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
FLAGGED_DISCREPANCY_KEYS = {
    "press_reg_all_source_access_and_ocr_scrambling",
    "press_reg_verification_tier_and_crosscheck",
    "press_reg_amendment_decree_91513_not_attributable_to_articles",
    "press_reg_article1_untitled_predates_baab1",
    "press_reg_baab2_fusul_numbering_irregularities",
    "press_reg_art007_016_procedural_redaction_placeholder",
    "press_reg_art072_073_survey_vs_tourism_authority_inconsistency",
    "press_reg_art085_089_page_reread_note",
    "press_reg_companion_base_law_already_tracked_separately",
    "press_reg_currency_check_98_articles_content_still_hosted_2024",
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
        yield (int(ch["first_article"]), int(ch["last_article"]))


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
        e.append("[1c] expected %d chapter_structure entries, got %d" %
                  (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

    covered = set()
    for lo, hi in _iter_chapter_ranges(chs):
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] article %d covered by more than one leaf range" % n)
            covered.add(n)
    if covered != set(range(1, N + 1)):
        missing = sorted(set(range(1, N + 1)) - covered)
        extra = sorted(covered - set(range(1, N + 1)))
        if missing:
            e.append("[1c] chapter_structure missing article(s): %s" % missing[:20])
        if extra:
            e.append("[1c] chapter_structure covers out-of-range article(s): %s" % extra[:20])

    # Article 1 must be modelled as its own untitled leaf range (its باب heading
    # physically appears after its own text, immediately before Article 2).
    first_ch = chs[0] if chs else {}
    if first_ch.get("first_article") != 1 or first_ch.get("last_article") != 1:
        e.append("[1d] first chapter_structure entry must cover only Article 1")
    if first_ch.get("section_ar") is not None:
        e.append("[1d] first chapter_structure entry (Article 1) should have "
                 "section_ar=null with a documentary section_note_ar")

    sc = Counter()
    for k, a in arts.items():
        if a.get("status") != TOP_STATUS:
            e.append("[2] %s: expected status %r, got %r" % (k, TOP_STATUS, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected structure_status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if k not in AMENDED_KEYS and a.get("history"):
            e.append("[2i] %s: non-amended article must have empty history[]" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)

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

    # Honesty gate: this track must NOT claim the 91513/1439H amendment is
    # attributed to specific articles (no changelog exists in the source).
    if src.get("consolidated_amended_law") is not True:
        e.append("[2g] consolidated_amended_law must be True (source is a "
                 "post-1439H-amendment consolidated document)")
    if not src.get("amendment_decree_ar") or "91513" not in src["amendment_decree_ar"]:
        e.append("[2g] amendment_decree_ar must reference decision 91513")
    if src.get("preamble_ar") not in ("", None):
        e.append("[2l] preamble_ar must be empty -- no resolution preamble/enacting "
                 "text was located this pass; a non-empty value would risk fabrication")

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("press_reg_art_001", {})
    if "تعريفات" not in art1.get("number_label_ar", ""):
        e.append("[2j] Article 1 missing expected تعريفات definitions title (this "
                 "source's own convention places تعريفات in the article's number "
                 "label/title line, not repeated in the body text)")
    if "التداول" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected التداول definition clause")
    art7 = arts.get("press_reg_art_007", {})
    if "{ تم تعديل الاجراء تقنياً }" not in art7.get("text", ""):
        e.append("[2j] Article 7 missing expected in-text procedural-redaction "
                 "placeholder")
    art16 = arts.get("press_reg_art_016", {})
    if "{ تم تعديل الاجراء تقنياً }" not in art16.get("text", ""):
        e.append("[2j] Article 16 missing expected in-text procedural-redaction "
                 "placeholder")
    art69 = arts.get("press_reg_art_069", {})
    if "فسح خطي لكل مؤلف" not in art69.get("text", ""):
        e.append("[2j] Article 69 missing expected clause matching the independent "
                 "Umm al-Qura Gazette cross-check")
    art99 = arts.get("press_reg_art_099", {})
    if "الجريدة الرسمية" not in art99.get("text", ""):
        e.append("[2j] Article 99 (publication clause) missing expected gazette token")
    if src.get("decree") != "قرار وزير الإعلام رقم (م/و/2759/1/م)" or \
            src.get("decree_date_hijri") != "16/6/1422":
        e.append("[2j] decree/decree_date_hijri mismatch with verified M/W/2759/1/M, "
                 "16/6/1422H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("base_law_key") != "press":
        e.append("[2j] base_law_key must reference the already-tracked base law (press)")

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
        if r.get("law_component") != "regulation":
            e.append("[4] %s: law_component must be 'regulation'" % r["article_key"])
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
        if r.get("law_component") != "regulation":
            e.append("[5] %s: law_component must be 'regulation'" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != TOP_STATUS.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Press Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Press and Publications Law")
    print("  - 99 records, all اصلية (consolidated current text); 0 معدلة/ملغاة/مضافة")
    print("    flagged individually -- the 91513/1439H amendment could not be")
    print("    attributed to specific articles from this changelog-free source")
    print("  - 8 flat structural leaf ranges: Article 1 alone (untitled, precedes the")
    print("    first named باب), then 7 أبواب (2-16, 17-62, 63-77, 78-89, 90-92, 93-96,")
    print("    97-99); Baab 2 carries genuine internal فصل-numbering defects, preserved")
    print("    as printed (not renumbered) -- see known_unresolved_discrepancies")
    print("  - VERIFICATION TIER: TIER_2 -- Ministry of Media's own PDF via a Wayback")
    print("    Machine snapshot (23 Nov 2024, live media.gov.sa unreachable this pass),")
    print("    all 99 articles vision-read in full across 98 pages (not OCR); partial")
    print("    cross-check via an Umm al-Qura Gazette article confirming Article 69(c)")
    print("  - Ministerial Decision M/W/2759/1/M (16/6/1422H), amended by Decision")
    print("    91513 (9/11/1439H); base law (نظام المطبوعات والنشر, M/32) already")
    print("    tracked separately at sources/press/")
    print("  - Articles 7 and 16 preserve an in-text procedural-redaction placeholder")
    print("    ('{ تم تعديل الاجراء تقنياً }') verbatim; Articles 72/73 preserve an")
    print("    internal الهيئة العامة للمساحة / للسياحة authority-name inconsistency")
    print("    verbatim -- neither was silently harmonised or corrected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
