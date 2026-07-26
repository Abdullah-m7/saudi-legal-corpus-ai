#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Elderly Rights and Care Law track
(23 records, all اصلية -- 0 معدلة, 0 ملغاة, 0 مضافة; flat structure, no
أبواب/فصول; Royal Decree M/47, 3/6/1443H).

VERIFICATION TIER: TIER_1 -- see the generator's module docstring and
sources/elderly_care_law/law/official_source/
elderly_care_law_official_source.json's verification_methodology_note for the
full account. Summary: laws.boe.gov.sa's live portal was unreachable this
pass, but a Wayback Machine snapshot of this law's own dedicated BOE lawId
page WAS reachable and carries the official portal's own full verbatim text
of all 23 articles (none flagged modified/canceled); cross-checked
byte-for-byte against nezams.com; identity/count/publication date
independently confirmed a third time via a National Society for Human Rights
pamphlet PDF. This validator does not re-adjudicate provenance; it checks
internal self-consistency and that every discrepancy is recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "elderly_care_law", "law", "official_source",
                   "elderly_care_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "elderly_care_law", "law", "verified",
                       "elderly_care_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "elderly_care_law", "law", "verified",
                       "elderly_care_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "elderly_care_law_arabic_legal_llm",
                   "elderly_care_law_legal_llm_001_023.json")
N = 23
KEY_RE = r"elderly_care_law_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 23, "معدلة": 0, "ملغاة": 0, "مضافة": 0}

STATUS_UNCHANGED = "UNCHANGED"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
FLAGGED_DISCREPANCY_KEYS = {
    "elderly_care_law_boe_live_unreachable_wayback_worked",
    "elderly_care_law_no_chapters_flat_structure",
    "elderly_care_law_implementing_regulation_separate_track",
    "elderly_care_law_com_resolution_292_role_clarified",
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

    numbers = sorted(a["article_number"] for a in arts.values())
    if numbers != list(range(1, N + 1)):
        e.append("[1b] article numbers %s != contiguous 1..%d" % (numbers, N))

    if src.get("chapter_structure") != []:
        e.append("[1c] chapter_structure must be empty (flat structure, no أبواب/فصول)")

    sc = Counter()
    for k, a in arts.items():
        if a.get("status") != STATUS_UNCHANGED:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS_UNCHANGED, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected structure/section status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
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
            e.append("[2i] %s: original article must have empty history[]" % k)
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
        e.append("[2d] missing verification_methodology_note explaining the verification tier")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))

    if not src.get("amendment_history"):
        e.append("[2k] missing amendment_history (must record founding decree)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "م/47" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/47")

    # spot-checks anchoring key facts established this pass
    a1 = arts.get("elderly_care_law_art_001", {})
    if "ستين" not in a1.get("text", "") or "كبير السن" not in a1.get("text", ""):
        e.append("[2j] Article 1 missing expected definition of كبير السن (age sixty)")
    a23 = arts.get("elderly_care_law_art_023", {})
    if "تسعين" not in a23.get("text", ""):
        e.append("[2j] Article 23 missing expected 90-day effective-date clause")
    a22 = arts.get("elderly_care_law_art_022", {})
    if "الوزير" not in a22.get("text", "") or "تسعين" not in a22.get("text", ""):
        e.append("[2j] Article 22 missing expected Minister-issues-Regulation-within-90-days clause")
    a16 = arts.get("elderly_care_law_art_016", {})
    if "خمسمائة ألف" not in a16.get("text", ""):
        e.append("[2j] Article 16 missing expected penalty amount (خمسمائة ألف ريال)")

    if src.get("decree") != "المرسوم الملكي رقم م/47" or src.get("decree_date_hijri") != "3/6/1443":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Decree M/47, 3/6/1443H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (no amendment found)")
    pre = src.get("preamble_ar", "")
    if not pre or "(292)" not in pre or "نظام حقوق كبير السن ورعايته" not in pre:
        e.append("[2j] preamble_ar must be present and reference CoM Resolution 292 and the law's name")

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
        e.append("[5] llm article_range must be [1, %d]" % N)
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
        if r.get("source_trust", {}).get("source_status") != STATUS_UNCHANGED.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Elderly Care Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Saudi Arabian Elderly Rights and Care Law")
    print("  - 23 records: 23 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة; flat structure, no أبواب/فصول")
    print("  - VERIFICATION TIER: TIER_1 -- laws.boe.gov.sa live portal unreachable this pass, but")
    print("    a Wayback-archived snapshot of this law's own BOE lawId page WAS reachable and")
    print("    carries the official portal's own full verbatim text of all 23 articles (none")
    print("    flagged modified/canceled); cross-checked byte-for-byte against nezams.com;")
    print("    identity/count/publication date confirmed a third time via a National Society for")
    print("    Human Rights (nshr.org.sa) pamphlet PDF")
    print("  - Royal Decree M/47 (3/6/1443H, ~14 January 2022G), Council of Ministers Resolution")
    print("    292 (1/6/1443H), published Umm al-Qura Gazette 11 Jumada al-Akhirah 1443H (14 Jan")
    print("    2022G), Issue 4917; administered by the Ministry of Human Resources and Social")
    print("    Development")
    print("  - No amendment found in any source checked as of this pass")
    print("  - Implementing Regulation tracked separately as elderly_care_regulation (shared")
    print("    internal law_key: elderly_care) -- includes an important correction of CoM")
    print("    Resolution 292's actual role (it approved this Law, not the Regulation)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
