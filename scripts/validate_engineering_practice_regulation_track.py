#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Law of
Practicing Engineering Professions track (اللائحة التنفيذية لنظام مزاولة
المهن الهندسية; 18 records, ALL اصلية, 0 معدلة, 0 ملغاة, 0 مضافة; flat
structure -- NO أبواب/فصول grouping).

VERIFICATION TIER -- see the generator's module docstring and
sources/engineering_practice_regulation/law/official_source/
engineering_practice_regulation_official_source.json's
verification_methodology_note for the full account: PRIMARY source is the
official Umm al-Qura Gazette portal (uqn.gov.sa) itself -- direct HTML text
for both the Regulation and its issuing Decision -- cross-checked verbatim
article-by-article against qanoonsa.com (an independent secondary
aggregator): 18/18 exact matches -> TIER_2. laws.boe.gov.sa and saudieng.sa
were both unreachable live this pass (connection reset); the Wayback
Machine's CDX/availability API confirmed a stable saudieng.sa PDF snapshot
exists but its content-serving path was blocked by this session's egress
policy. This validator does not re-adjudicate provenance; it only checks
internal self-consistency and that every discrepancy is still recorded.

MATERIAL FACTS checked: 18 consecutive articles, no أبواب/فصول; all اصلية
with empty history; Article 1's ministry/authority definitions; Article 4's
genuine missing "ج-" label and Article 7's genuine missing item "3-" (both
preserved, not patched); Article 18's publication clause.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "engineering_practice_regulation", "law", "official_source",
                   "engineering_practice_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "engineering_practice_regulation", "law", "verified",
                       "engineering_practice_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "engineering_practice_regulation", "law", "verified",
                       "engineering_practice_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "engineering_practice_regulation_arabic_legal_llm",
                   "engineering_practice_regulation_legal_llm_001_018.json")
N = 18
KEY_RE = r"engineering_practice_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 18, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 1  # flat regulation -- no أبواب/فصول, single leaf range 1-18

STATUS_UNCHANGED = ("UQN_GOV_SA_OFFICIAL_GAZETTE_DIRECT_HTML_HTTP200_X_QANOONSA_COM_"
                    "INDEPENDENT_SECONDARY_WORDFORWORD_MATCH_ALL_18_ARTICLES_X_"
                    "LAWS_BOE_GOV_SA_AND_SAUDIENG_SA_LIVE_UNREACHABLE_WAYBACK_"
                    "CONTENT_PATH_BLOCKED_CDX_ONLY")
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
FLAGGED_DISCREPANCY_KEYS = {
    "engineering_practice_regulation_supersedes_2018_original_not_ingested",
    "engineering_practice_regulation_ministry_naming_cross_track_note",
    "engineering_practice_regulation_article4_missing_jeem_label_source_level",
    "engineering_practice_regulation_article7_missing_item3_source_level",
    "engineering_practice_regulation_gazette_issue_number_secondary_source_only",
    "engineering_practice_regulation_boe_saudieng_live_unreachable_wayback_content_blocked",
    "engineering_practice_regulation_no_baab_fasl_structure",
    "engineering_practice_regulation_no_inline_article_titles",
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

    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != list(range(1, N + 1)):
        e.append("[1b] article numbers not a clean 1..%d sequence: %s" % (N, nums))

    chs = src.get("chapter_structure") or []
    n_top = len(chs)
    if n_top != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d top-level chapter_structure entries (flat regulation, "
                  "no أبواب/فصول), got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

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

    sc = Counter()
    for k, a in arts.items():
        if a.get("status") != STATUS_UNCHANGED:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS_UNCHANGED, a.get("status")))
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
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly)" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if a.get("history"):
            e.append("[2i] %s: no article in this unamended regulation should carry history[]" % k)
        if "title_ar" in a:
            e.append("[2i] %s: unexpected title_ar key present (source supplies no inline "
                      "per-article titles for this regulation)" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        if re.search(r"[٠-٩]", a["text"]):
            e.append("[2g] %s: residual Eastern-Arabic-Indic digit found" % k)

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
        e.append("[2k] missing amendment_history (must record both the 1439H original and "
                  "the current 1445H reissuance)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in ah)
        for token in ("38315", "4400942200"):
            if token not in decrees:
                e.append("[2k] amendment_history must reference %s" % token)

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("engineering_practice_regulation_art_001", {}).get("text", "")
    if "وزارة الشؤون البلدية والقروية والإسكان" not in art1:
        e.append("[2j] Article 1 missing expected current ministry naming")
    if "الهيئة السعودية للمهندسين" not in art1:
        e.append("[2j] Article 1 missing expected الهيئة definition")
    art4 = arts.get("engineering_practice_regulation_art_004", {}).get("text", "")
    if "ج- الفني" in art4 or "ج-الفني" in art4:
        e.append("[2j] Article 4 must NOT have a fabricated ج- label for الفني -- see "
                 "known_unresolved_discrepancies")
    if "الفني" not in art4 or "ب- الأخصائي" not in art4:
        e.append("[2j] Article 4 missing expected accreditation categories")
    art7 = arts.get("engineering_practice_regulation_art_007", {}).get("text", "")
    if "3- " in art7:
        e.append("[2j] Article 7 must NOT have a fabricated item 3- -- see "
                 "known_unresolved_discrepancies")
    if "2- الإشراف" not in art7 or "4- التنفيذ" not in art7:
        e.append("[2j] Article 7 missing expected 2-/4- numbering gap (genuine source anomaly)")
    art18 = arts.get("engineering_practice_regulation_art_018", {}).get("text", "")
    if "الجريدة الرسمية" not in art18:
        e.append("[2j] Article 18 missing expected publication/effective-date clause")

    if (src.get("decree") != "قرار وزير الشؤون البلدية والقروية والإسكان رقم (4/4400942200)"
            or src.get("decree_date_hijri") != "26/5/1445"):
        e.append("[2j] decree/decree_date_hijri mismatch with Decision 4/4400942200, 26/5/1445H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False")
    if src.get("law_component") != "regulation":
        e.append("[2j] law_component must be 'regulation'")
    pre = src.get("preamble_ar", "")
    if not pre or "4400942200" not in pre or "17103" not in pre:
        e.append("[2j] preamble_ar must reference Decision 4400942200 and Royal Order 17103")

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
        if r.get("law_component") != "regulation":
            e.append("[5] %s: law_component must be 'regulation'" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Engineering Practice Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Law of Practicing Engineering Professions")
    print("  (اللائحة التنفيذية لنظام مزاولة المهن الهندسية)")
    print("  - 18 records: ALL اصلية (0 معدلة, 0 ملغاة, 0 مضافة) -- fresh full reissuance")
    print("  - flat structure, NO أبواب/فصول grouping (single leaf range 1-18); no inline")
    print("    per-article titles in the source (no title_ar key used)")
    print("  - VERIFICATION TIER: TIER_2 -- uqn.gov.sa (official Umm al-Qura Gazette portal,")
    print("    direct HTML) x qanoonsa.com (independent secondary), 18/18 exact article matches;")
    print("    laws.boe.gov.sa and saudieng.sa both live-unreachable; Wayback content path")
    print("    blocked by egress policy (CDX/availability API only)")
    print("  - Decision No. (4/4400942200) of the Minister of Municipal, Rural Affairs and")
    print("    Housing, 26/5/1445H; published Umm al-Qura issue 5013, 16/6/1445H (29 Dec 2023G)")
    print("  - SUPERSEDES former Decision 38315 (12/7/1439H, ~1 Apr 2018G) via a general")
    print("    conflicting-decisions repeal clause; former text NOT ingested (honest")
    print("    could-not-confirm -- saudieng.sa/BOE unreachable, Wayback content blocked)")
    print("  - TWO GENUINE SOURCE-LEVEL ANOMALIES preserved, not fabricated: Article 4's missing")
    print("    ج- label for الفني; Article 7's missing item 3- (numbering jumps 2- to 4-)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
