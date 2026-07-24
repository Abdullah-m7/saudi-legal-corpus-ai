#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi General Education Law track (نظام
التعليم العام; 68 records, all اصلية, 0 معدلة, 0 ملغاة, 0 مضافة; 9 فصول
(chapters); the LAW IS NOT YET IN FORCE).

VERIFICATION TIER -- see the generator's module docstring and
sources/general_education/law/official_source/
general_education_law_official_source.json's verification_methodology_note
for the full account: this Law was issued essentially on the eve of this
research pass. Direct LIVE access to the Umm al-Qura Official Gazette
(uqn.gov.sa) SUCCEEDED (HTTP 200, no Wayback/mirror needed) for the decree,
the Council of Ministers Resolution, and the Law's full text (all 68
articles). No dedicated laws.boe.gov.sa lawId page exists yet (expected given
freshness, confirmed via direct search). Officially corroborated (facts, not
full wording) by the Saudi Press Agency (spa.gov.sa); structurally
cross-checked (68 articles/9 chapters, specific article substance) by
independent press (sabq.org, argaam.com, alriyadh.com, albiladdaily.com) ->
TIER_2. This validator does not re-adjudicate provenance; it only checks
internal self-consistency and that every discrepancy is still recorded.

MATERIAL FACTS checked: 9-chapter structure with exact article ranges; all 68
articles اصلية (no amendments known, brand-new Law); Article 68 carries the
literal 180-day not-yet-in-force effective-date clause; the Royal Decree's
Clause Third repeals the Adult Education and Literacy Law (M/22, 9/6/1392H)
immediately but with a one-year phased transition; the gazette date
discrepancy (24 vs 25 July 2026) is recorded in
known_unresolved_discrepancies; not_yet_in_force is asserted true throughout.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "general_education", "law", "official_source",
                   "general_education_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "general_education", "law", "verified",
                       "general_education_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "general_education", "law", "verified",
                       "general_education_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "general_education_arabic_legal_llm",
                   "general_education_law_legal_llm_001_068.json")
N = 68
N_CHAPTERS = 9
KEY_RE = r"general_education_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 68, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
CHAPTER_RANGES = {
    1: (1, 6), 2: (7, 16), 3: (17, 26), 4: (27, 30), 5: (31, 36),
    6: (37, 50), 7: (51, 56), 8: (57, 65), 9: (66, 68),
}
CHAPTER_TITLES = {
    1: "التعريفات والأهداف", 2: "المجلس والوزارة",
    3: "مراحل ومسارات التعليم العام وأنماطه", 4: "البرامج والمناهج التعليمية",
    5: "المؤسسات التعليمية الخاصة", 6: "الطلاب والمعلمون وأولياء الأمور",
    7: "المؤسسات التعليمية والتجهيزات والخدمات", 8: "المخالفات والجزاءات",
    9: "أحكام ختامية",
}

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
FLAGGED_DISCREPANCY_KEYS = {
    "general_education_law_gazette_date_one_day_discrepancy",
    "general_education_law_not_yet_in_force",
    "general_education_law_adult_education_repeal_immediate_not_deferred",
    "general_education_law_seven_com_resolutions_repealed_untracked",
    "general_education_law_boe_not_yet_indexed",
    "general_education_law_beta_website_label_not_draft_status",
    "general_education_law_spa_url_blocked_via_webfetch_curl_used",
    "general_education_law_tashkeel_stripped",
}
AR = "ء-ي"
HARAKAT = re.compile(r"[ً-ْٰٕٓٔ]")
LAW_AR_CHECK = "نظام التعليم العام"


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

    # continuous 1..68, no gaps/dupes
    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != list(range(1, N + 1)):
        e.append("[1b] article numbers not a clean 1..%d sequence: %s" % (N, nums))

    # 9-chapter structure with exact expected ranges
    chs = src.get("chapter_structure")
    if not chs or len(chs) != N_CHAPTERS:
        e.append("[1c] expected %d chapters, found %r" % (N_CHAPTERS, chs))
    else:
        for c in chs:
            cn = c.get("chapter_number")
            want_lo, want_hi = CHAPTER_RANGES.get(cn, (None, None))
            if list(c.get("article_range", [])) != [want_lo, want_hi]:
                e.append("[1c] chapter %s: article_range %r != expected [%s, %s]"
                         % (cn, c.get("article_range"), want_lo, want_hi))
            if c.get("chapter_title_ar") != CHAPTER_TITLES.get(cn):
                e.append("[1c] chapter %s: title mismatch %r" % (cn, c.get("chapter_title_ar")))

    # build expected article->chapter map
    art_chapter = {}
    for cn, (lo, hi) in CHAPTER_RANGES.items():
        for n in range(lo, hi + 1):
            art_chapter[n] = CHAPTER_TITLES[cn]

    sc = Counter()
    for k, a in arts.items():
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected structure_status divergence" % k)
        if a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section_status divergence" % k)
        if not a.get("status") or not str(a.get("status")).strip():
            e.append("[2] %s: empty verification status string" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&{}]", a["text"]):
            e.append("[2] %s: empty text or latin/html/template leftovers" % k)
        n = int(re.match(KEY_RE, k).group(1))
        if a.get("section_ar") != art_chapter.get(n):
            e.append("[2] %s: section_ar %r != expected chapter title %r"
                     % (k, a.get("section_ar"), art_chapter.get(n)))
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly)" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment history" % k)
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

    ah = src.get("amendment_history")
    if not ah:
        e.append("[2k] missing amendment_history (must record founding decree)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in ah)
        if "م/36" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/36")

    # NOT-YET-IN-FORCE must be asserted, never silently dropped
    if src.get("not_yet_in_force") is not True:
        e.append("[2j] not_yet_in_force must be True -- this law is not in force yet")
    if not src.get("effective_date_note_ar") or "مائة وثمانين" not in src.get("effective_date_note_ar", ""):
        e.append("[2j] effective_date_note_ar must state the 180-day (مائة وثمانين) post-publication rule")

    # spot-checks anchoring key facts
    art1 = arts.get("general_education_law_art_001", {}).get("text", "")
    if "التعليم العام" not in art1 or "الوزارة" not in art1:
        e.append("[2j] Article 1 missing expected definitions")
    art4 = arts.get("general_education_law_art_004", {}).get("text", "")
    if "السادسة" not in art4 or "الخامسة عشرة" not in art4:
        e.append("[2j] Article 4 missing expected compulsory-education-age clause (6-15)")
    art6 = arts.get("general_education_law_art_006", {}).get("text", "")
    if "مدارس تعليم البنات" not in art6 or "مدارس تعليم البنين" not in art6:
        e.append("[2j] Article 6 missing expected girls/boys school separation clause")
    art7 = arts.get("general_education_law_art_007", {}).get("text", "")
    if "مجلس لشؤون التعليم العام" not in art7:
        e.append("[2j] Article 7 missing expected Council-establishment clause")
    art68 = arts.get("general_education_law_art_068", {}).get("text", "")
    for token in ("مائة وثمانين", "يعمل بالنظام", "يلغي جميع ما يتعارض معه"):
        if token not in art68:
            e.append("[2j] Article 68 missing expected token %r" % token)

    # exactly ONE effective-date clause (Article 68 only)
    hits = [k for k, a in arts.items() if "يعمل بالنظام بعد" in a["text"]]
    if hits != ["general_education_law_art_068"]:
        e.append("[2j] 180-day effective-date clause must appear in Article 68 only, found: %s"
                 % hits)

    if src.get("decree") != "المرسوم الملكي رقم م/36" or src.get("decree_date_hijri") != "27/1/1448":
        e.append("[2j] decree/decree_date_hijri mismatch with Royal Decree M/36, 27/1/1448H")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (brand-new law, no amendments)")
    pre = src.get("preamble_ar", "")
    if not pre or "103" not in pre or LAW_AR_CHECK not in pre:
        e.append("[2j] preamble_ar must be present and reference CoM Resolution 103 and the law name")
    if "م/22" not in pre or "1392" not in pre:
        e.append("[2j] preamble_ar must reference the repealed Adult Education Law (م/22, 1392H)")
    # the 7 repealed CoM-level regulations must all be named in the preamble
    for num in ("779", "557", "1006", "26", "175", "245", "49", "238"):
        if num not in pre:
            e.append("[2j] preamble_ar must reference repealed resolution number %r" % num)

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
        if r.get("law_not_yet_in_force") is not True:
            e.append("[4] %s: law_not_yet_in_force must be True" % r["article_key"])
        if (r.get("is_amended")) != (r["article_key"] in AMENDED_KEYS):
            e.append("[4] %s: is_amended flag mismatch" % r["article_key"])
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
    if summary.get("not_yet_in_force") is not True:
        e.append("[4b] summary not_yet_in_force must be True")

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    if llm.get("law_not_yet_in_force") is not True:
        e.append("[5] llm law_not_yet_in_force must be True")
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
        print("FAIL: %d error(s) in General Education Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Saudi General Education Law (نظام التعليم العام)")
    print("  - 68 records: all اصلية, 0 معدلة, 0 ملغاة, 0 مضافة across 9 chapters")
    print("  - VERIFICATION TIER: TIER_2 -- full text fetched directly (HTTP 200) from the Umm")
    print("    al-Qura Official Gazette (uqn.gov.sa) itself; officially corroborated (facts, not")
    print("    full wording) by the Saudi Press Agency; structurally cross-checked by independent")
    print("    press (sabq.org confirms 68 articles/9 chapters). No laws.boe.gov.sa lawId page")
    print("    exists yet (expected given this Law's freshness)")
    print("  - Royal Decree M/36 (27/1/1448H), CoM Resolution 103 (22/1/1448H)")
    print("  - THE LAW IS NOT YET IN FORCE: Article 68 sets effect 180 days after gazette")
    print("    publication (~mid-January 2027)")
    print("  - Gazette publication date discrepancy of one day (24 vs 25 July 2026) disclosed,")
    print("    not silently resolved")
    print("  - REPEALS (immediately, but phased with a one-year transition): the Adult Education")
    print("    and Literacy Law (M/22, 9/6/1392H) and seven Council-of-Ministers-level school")
    print("    regulations -- none of these eight are tracked instruments in this corpus, so no")
    print("    supersession-graph edge is required for any of them")
    return 0


if __name__ == "__main__":
    sys.exit(main())
