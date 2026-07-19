#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Saudi Arabian Food
Law track (85 records: 81 اصلية, 1 معدلة, 3 مضافة, 0 ملغاة; 12 chapters, with a
genuine duplicate chapter-title anomaly for chapters 4-5, both "تداول الغذاء",
mirroring the same disclosed anomaly in this corpus's food_law track).

VERIFICATION TIER -- see the generator's module docstring and
sources/food/regulation/official_source/food_regulation_official_source.json's
verification_methodology_note for the full account: laws.boe.gov.sa was
checked FIRST (per this corpus's standard methodology) but is unreachable this
pass (live: connection reset; Wayback snapshot content blocked by this
session's egress policy) and, more fundamentally, has no dedicated lawId page
for this Implementing Regulation at all (only for the base Food Law). The
PRIMARY source actually used is sfda.gov.sa (the issuing Authority's own site,
a born-digital PDF, NOT the scanned/OCR PDF this corpus's food_law track had
to rely on for the base law), cross-verified against qanoonsa.com and
qistas.com for decree number/date/article-count/amendment history. This
validator does not re-adjudicate any of this; it only checks internal
self-consistency of the text this track actually ingests, and that every
discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "food", "regulation", "official_source",
                   "food_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "food", "regulation", "verified",
                       "food_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "food", "regulation", "verified",
                       "food_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "food_regulation_arabic_legal_llm",
                   "food_regulation_legal_llm_001_085.json")
N = 85
KEY_RE = r"food_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 81, "معدلة": 1, "ملغاة": 0, "مضافة": 3}
EXPECTED_TOP_LEVEL_CHAPTERS = 12

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
AMENDED_KEYS = {"food_regulation_art_041"}
ADDED_KEYS = {"food_regulation_art_042", "food_regulation_art_043", "food_regulation_art_044"}
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY = {}
for k in AMENDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_AMENDED
for k in ADDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_ADDED
FLAGGED_DISCREPANCY_KEYS = {
    "food_regulation_gap_map_candidate_confirmed",
    "food_regulation_boe_unreachable_no_dedicated_page",
    "food_regulation_no_preamble_recovered",
    "food_regulation_gregorian_date_not_pinpointed",
    "food_regulation_article85_mislabeled_58",
    "food_regulation_extensive_ligature_reversal_defect",
    "food_regulation_article40_missing_terminal_period",
    "food_regulation_article41_amended_paragraph_not_isolated",
    "food_regulation_renumbering_after_articles_added",
    "food_regulation_penalty_table_out_of_scope",
    "food_regulation_duplicate_chapter_titles_anomaly",
    "food_regulation_no_inline_article_titles",
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

    # duplicate chapter-title anomaly must be preserved verbatim (chapters 4 and 5)
    if len(chs) >= 5:
        if chs[3].get("title_ar") != chs[4].get("title_ar"):
            e.append("[1d] expected chapters 4 and 5 to share the same disclosed duplicate "
                     "title anomaly ('تداول الغذاء'), titles diverge")

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
        # ligature-extraction-bug regression guards (each corresponds to a fix
        # disclosed in the generator script / known_unresolved_discrepancies).
        # Only word-INITIAL "امل" (optionally after a single و/ف/ب proclitic)
        # is the actual لم-ligature-after-alif-lam bug pattern -- "امل" occurring
        # elsewhere within a word (شاملة، حامل، عاملين، تعامل، يتعامل...) is
        # correctly-spelled Arabic and must NOT be flagged.
        for w in re.findall(r"(?:^|(?<=[\s]))[وفب]?امل[%s]*" % AR, a["text"]):
            e.append("[2g] %s: unresolved 'امل' (لم-ligature) artifact: %r" % (k, w))
        for bad in ("الالئحة", "مالئم", "أال ", "اإل", "األ", "اآل"):
            if bad in a["text"]:
                e.append("[2g] %s: unresolved لا/لإ-ligature artifact %r" % (k, bad))
        for bad in ("سالمة", "صالحية", "عالقة", "حاالت", "خالل", "حالل"):
            if bad in a["text"]:
                e.append("[2g] %s: unresolved mid-root لا-ligature artifact %r" % (k, bad))
        m40 = re.search(r"المادة\s+[ء-ي]+(?:\s+[ء-ي]+){0,3}\s*:", a["text"])
        if m40 and "من اللائحة" not in a["text"][max(0, m40.start() - 20):m40.end() + 20] \
                and len(m40.group()) < 45 and k != "food_regulation_art_003":
            e.append("[2g] %s: possible leaked base-law header %r" % (k, m40.group()))

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
        e.append("[2k] missing amendment_history (must record founding + 4/44 decisions)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "3-16-1439" not in decrees:
            e.append("[2k] amendment_history must reference founding decree 3-16-1439")
        if "4/44" not in decrees:
            e.append("[2k] amendment_history must reference amending decree 4/44")

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("food_regulation_art_001", {})
    if "الجهات المختصة" not in art1.get("text", "") or "مدخلات الإنتاج الزراعي" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected definitions (الجهات المختصة / "
                 "مدخلات الإنتاج الزراعي)")
    art41 = arts.get("food_regulation_art_041", {})
    if "التسمم الغذائي" not in art41.get("text", ""):
        e.append("[2j] Article 41 missing expected food-poisoning reference tying it to the "
                 "4/44 amendment")
    art42 = arts.get("food_regulation_art_042", {})
    if "تسمم غذائي" not in art42.get("text", ""):
        e.append("[2j] Article 42 (added per 4/44) missing expected food-poisoning-procedure "
                 "content")
    art85 = arts.get("food_regulation_art_085", {})
    if art85.get("number_label_ar") != "المادة (58) من اللائحة":
        e.append("[2j] Article 85's number_label_ar must preserve the source's own mislabeled "
                 "'(58)' header verbatim, not silently renumbered to '(85)'")
    if src.get("decree") != "قرار مجلس إدارة الهيئة العامة للغذاء والدواء رقم (3-16-1439)" \
            or src.get("decree_date_hijri") != "9/4/1439":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Board Resolution "
                 "3-16-1439, 9/4/1439H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True (this text reflects the 4/44 "
                 "amendment consolidated into the founding regulation)")
    if "preamble_ar" in src:
        e.append("[2j] preamble_ar should be ABSENT (not recovered this pass; see "
                 "known_unresolved_discrepancies) rather than a fabricated placeholder")

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
        print("FAIL: %d error(s) in Food Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Saudi Arabian Food Law")
    print("  - 85 records: 81 اصلية, 1 معدلة, 3 مضافة, 0 ملغاة")
    print("  - 12 chapters (chapters 4 and 5 share the disclosed duplicate title "
          "'تداول الغذاء', mirroring the same anomaly in the food_law track)")
    print("  - VERIFICATION TIER: TIER_2 -- laws.boe.gov.sa checked first but unreachable this")
    print("    pass and confirmed to have no dedicated lawId page for this Implementing")
    print("    Regulation at all; PRIMARY source is sfda.gov.sa (the issuing Authority's own")
    print("    site, a born-digital PDF, 2025-06 upload), cross-verified against qanoonsa.com")
    print("    and qistas.com (decree number/date, article count, amendment history)")
    print("  - SFDA Board Resolution No. (3-16-1439), 9/4/1439H, as amended by Resolution")
    print("    No. (4/44), 14/6/1446H (added a paragraph to Article 41; added Articles 42-44)")
    print("  - ANOMALY: the final article's own printed header literally reads 'المادة (58)")
    print("    من اللائحة' (a transposed-digit typo for 85), confirmed via direct visual page")
    print("    inspection -- preserved verbatim in number_label_ar, not silently renumbered")
    print("  - Extensive, individually-verified font ligature-reversal extraction defects")
    print("    fixed (three distinct patterns, confirmed via two independent extraction tools")
    print("    plus visual page inspection) -- see generator script docstring for full account")
    print("  - Separate violation-classification-and-penalty TABLE (amended by Resolution")
    print("    5/44, ~May 2026) confirmed out of scope -- a distinct tabular annex, not a")
    print("    textual amendment to any of this track's 85 numbered articles")
    return 0


if __name__ == "__main__":
    sys.exit(main())
