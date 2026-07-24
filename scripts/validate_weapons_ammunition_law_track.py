#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Weapons and Ammunition Law track
(نظام الأسلحة والذخائر; 63 records: 56 اصلية, 7 معدلة [arts 2, 12, 25, 31,
43, 50, 53], 0 ملغاة, 0 مضافة; SEVEN topical sections, no formal باب/فصل
label in the source).

VERIFICATION TIER -- see the generator's module docstring and
sources/weapons_ammunition/law/official_source/
weapons_ammunition_law_official_source.json's verification_methodology_note
for the full account: laws.boe.gov.sa HAS a dedicated lawId page for this law
(a445af93-671f-496b-818a-a9a700f19150) but the LIVE portal was unreachable
this pass (HTTP 503 / connection-reset). Three Wayback Machine snapshots of
that SAME official portal (2019, 2025, 2026) were cross-checked against
nezams.com for all 63 articles -> TIER_2. Five articles (12, 25, 43, 50, 53)
required a documented interpretive judgment between two texts BOE itself
provides; Article 31's paragraph (d) is sourced from nezams.com with only
partial official-gazette corroboration. This validator does not re-adjudicate
provenance; it only checks internal self-consistency and that every
discrepancy is still recorded.

MATERIAL FACTS checked: 7 topical sections spanning all 63 articles with a
"<label> (<range>)" section_ar convention (NOT bab/fasl-labelled); the 7
amended articles carry both original and amendment_current history whose
current text equals `text`; Article 62 contains the named predecessor-repeal
clause (Royal Decree M/8, 19/2/1402H); the fee-schedule-annex and
implementing-regulation follow-up candidates are recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "weapons_ammunition", "law", "official_source",
                   "weapons_ammunition_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "weapons_ammunition", "law", "verified",
                       "weapons_ammunition_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "weapons_ammunition", "law", "verified",
                       "weapons_ammunition_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "weapons_ammunition_arabic_legal_llm",
                   "weapons_ammunition_law_legal_llm_001_063.json")
N = 63
KEY_RE = r"weapons_ammunition_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 56, "معدلة": 7, "ملغاة": 0, "مضافة": 0}

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
AMENDED_KEYS: set[str] = {
    "weapons_ammunition_law_art_002",
    "weapons_ammunition_law_art_012",
    "weapons_ammunition_law_art_025",
    "weapons_ammunition_law_art_031",
    "weapons_ammunition_law_art_043",
    "weapons_ammunition_law_art_050",
    "weapons_ammunition_law_art_053",
}
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY: dict[str, str] = {k: STATUS_AMENDED_DATED for k in AMENDED_KEYS}
FLAGGED_DISCREPANCY_KEYS = {
    "weapons_ammunition_law_boe_live_unreachable_wayback_used",
    "weapons_ammunition_law_boe_internal_text_conflict_arts_12_25_43_50_53",
    "weapons_ammunition_law_art31_para_d_uqn_partial_verification",
    "weapons_ammunition_law_named_repeal_of_predecessor_m8_1402h",
    "weapons_ammunition_law_fee_schedule_annex_out_of_scope",
    "weapons_ammunition_law_implementing_regulation_out_of_scope",
    "weapons_ammunition_law_flat_topical_sections_no_bab_fasl_label",
    "weapons_ammunition_law_gregorian_date_not_pinpointed",
}
SECTION_RANGES = [
    ("التعريفات", 1, 1),
    ("أحكام عامة", 2, 8),
    ("أحكام الرخص", 9, 27),
    ("إصلاح الأسلحة وصيانتها", 28, 30),
    ("أحكام خاصة بالدبلوماسيين والمقيمين والوفود الرسمية", 31, 33),
    ("العقوبات", 34, 58),
    ("أحكام انتقالية", 59, 63),
]
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


def _section_for(n):
    for label, a, b in SECTION_RANGES:
        if a <= n <= b:
            return label
    return None


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

    # Seven topical sections must cover 1..63 with no gaps/overlap
    chs = src.get("chapter_structure")
    if not chs or len(chs) != 7:
        e.append("[1c] expected 7 chapter_structure entries, got %r" % (chs,))
    else:
        covered = set()
        for entry, (label, a, b) in zip(chs, SECTION_RANGES):
            if entry.get("label_ar") != label:
                e.append("[1c] chapter_structure label mismatch: %r != %r" % (entry.get("label_ar"), label))
            if entry.get("articles") != "%d-%d" % (a, b):
                e.append("[1c] chapter_structure articles range mismatch for %s" % label)
            covered.update(range(a, b + 1))
        if covered != set(range(1, N + 1)):
            e.append("[1c] chapter_structure ranges do not cover all 63 articles cleanly")

    sc = Counter()
    for k, a in arts.items():
        n = int(re.match(KEY_RE, k).group(1))
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
        if not a["text"].strip() or re.search(r"[<>&]", a["text"]):
            e.append("[2] %s: empty text or html leftovers" % k)
        expected_label = _section_for(n)
        if expected_label is None or expected_label not in (a.get("section_ar") or ""):
            e.append("[2] %s: section_ar %r does not contain expected topical label %r"
                     % (k, a.get("section_ar"), expected_label))
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
        if "title_ar" in a:
            e.append("[2i] %s: unexpected title_ar key present" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        if k in AMENDED_KEYS:
            hist = a.get("history") or []
            types = [h.get("type") for h in hist]
            if "amendment_current" not in types or "original" not in types:
                e.append("[2m] %s: amended history must include amendment_current AND original" % k)
            cur = next((h for h in hist if h.get("type") == "amendment_current"), None)
            if cur and cur.get("text") != a["text"]:
                e.append("[2m] %s: history amendment_current text must equal current `text`" % k)
            orig = next((h for h in hist if h.get("type") == "original"), None)
            if orig and orig.get("text") == a["text"]:
                e.append("[2m] %s: original history text must DIFFER from amended current text" % k)

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
        e.append("[2k] missing amendment_history (must record founding + amending decrees)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in ah)
        for must in ("م/45", "م/17", "217", "م/71", "967"):
            if must not in decrees:
                e.append("[2k] amendment_history must reference decree/resolution %r" % must)

    # spot-checks anchoring key facts
    art1 = arts.get("weapons_ammunition_law_art_001", {}).get("text", "")
    if "الأسلحة الحربية" not in art1 or "الذخيرة" not in art1:
        e.append("[2j] Article 1 missing expected definitions")
    art2 = arts.get("weapons_ammunition_law_art_002", {}).get("text", "")
    if "رئاسة أمن الدولة" not in art2:
        e.append("[2j] Article 2 (amended) missing added subsection (رئاسة أمن الدولة)")
    art12 = arts.get("weapons_ammunition_law_art_012", {}).get("text", "")
    if "نادي رماية" not in art12:
        e.append("[2j] Article 12 (amended) missing expected shooting-club fee text")
    art25 = arts.get("weapons_ammunition_law_art_025", {}).get("text", "")
    if "الجدول الملحق" not in art25:
        e.append("[2j] Article 25 (amended) missing expected fee-schedule reference")
    art31 = arts.get("weapons_ammunition_law_art_031", {}).get("text", "")
    if "المعاملة بالمثل" not in art31 or "د-" not in art31:
        e.append("[2j] Article 31 (amended) missing added paragraph (د)")
    art43 = arts.get("weapons_ammunition_law_art_043", {}).get("text", "")
    if "بندقية هوائية" not in art43:
        e.append("[2j] Article 43 (amended) missing expected air-rifle clause")
    art50 = arts.get("weapons_ammunition_law_art_050", {}).get("text", "")
    if "3 -" not in art50 or "4 -" not in art50:
        e.append("[2j] Article 50 (amended) missing expected expanded paragraphs")
    art53 = arts.get("weapons_ammunition_law_art_053", {}).get("text", "")
    if "المحكمة الإدارية" not in art53:
        e.append("[2j] Article 53 (amended) missing expected updated appeal-venue term")
    art62 = arts.get("weapons_ammunition_law_art_062", {}).get("text", "")
    if "م/8" not in art62 or "1402" not in art62 or "يلغي" not in art62:
        e.append("[2j] Article 62 missing expected named predecessor-repeal clause")

    if src.get("decree") != "المرسوم الملكي رقم م/45" or src.get("decree_date_hijri") != "25/7/1426":
        e.append("[2j] decree/decree_date_hijri mismatch with Royal Decree M/45, 25/7/1426H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True (this law HAS amendments incorporated)")
    pre = src.get("preamble_ar", "")
    if not pre or "193" not in pre or "نظام الأسلحة والذخائر" not in pre:
        e.append("[2j] preamble_ar must be present and reference CoM Resolution 193 and the law name")

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
    if summary.get("consolidated_amended_law") is not True:
        e.append("[4b] summary consolidated_amended_law must be True")

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
        print("FAIL: %d error(s) in Weapons and Ammunition Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Saudi Weapons and Ammunition Law (نظام الأسلحة والذخائر)")
    print("  - 63 records: 56 اصلية, 7 معدلة (arts 2, 12, 25, 31, 43, 50, 53), 0 ملغاة, 0 مضافة")
    print("  - SEVEN topical sections (no formal باب/فصل label in the source), covering 1-63 cleanly")
    print("  - VERIFICATION TIER: TIER_2 -- laws.boe.gov.sa live portal unreachable this pass (HTTP")
    print("    503 / connection-reset); 3 Wayback snapshots of the SAME official portal (2019-2026)")
    print("    cross-checked verbatim against nezams.com for all 63 articles. 5 articles required a")
    print("    documented interpretive judgment; Article 31's amendment partially corroborated via")
    print("    the Umm al-Qura gazette API")
    print("  - Royal Decree M/45 (25/7/1426H, ~2005G), CoM Resolution 193 (24/7/1426H), published")
    print("    Umm al-Qura 18/9/1426H")
    print("  - NAMED PREDECESSOR REPEAL: Article 62 repeals the prior Weapons and Ammunition Law")
    print("    (Royal Decree M/8, 19/2/1402H)")
    print("  - Follow-up candidates NOT ingested: Implementing Regulation; fee-schedule annex table")
    return 0


if __name__ == "__main__":
    sys.exit(main())
