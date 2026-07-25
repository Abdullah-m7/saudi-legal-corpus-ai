#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Saudi Arabian
Child Protection Law track (25 records, all اصلية; 5 chapters فصول; no
mukarrar; no amendment). STANDALONE track -- does not touch shared pipeline
files.

VERIFICATION TIER -- see the generator's module docstring and
sources/child_protection_regulation/law/official_source/
child_protection_regulation_official_source.json's verification_methodology_note:
laws.boe.gov.sa was unreachable this pass (HTTP 000 connection-reset direct
curl; HTTP 503 via WebFetch) and no dedicated lawId page for this regulation
was found via indexed search. Full verbatim text from nezams.com (HTTP 200);
decree identity + 5-chapter structure + 25-article count independently
confirmed by the OFFICIAL Ministry of Justice Adl-journal PDF
(adlm.moj.gov.sa/attach/1463.pdf, HTTP 200) -> TIER_3. CoM Resolution 427
(1443H), which amended the BASE LAW, was independently confirmed NOT to have
amended this regulation (nezams.com metadata "لم يجرِ عليه تعديل"; Umm Al-Qura
gazette title referencing the two LAWS, not their regulations) -- a general
WebSearch summary that conflated the two was rejected. This validator does not
re-adjudicate provenance; it checks internal self-consistency and that every
discrepancy is recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "child_protection_regulation", "law", "official_source",
                    "child_protection_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "child_protection_regulation", "law", "verified",
                       "child_protection_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "child_protection_regulation", "law", "verified",
                       "child_protection_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "child_protection_regulation_arabic_legal_llm",
                   "child_protection_regulation_legal_llm_001_025.json")
N = 25                 # total records
N_NUMBERED = 25        # numbered articles 1..25
KEY_RE = r"child_protection_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 25, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 5  # 5 فصول

STATUS_UNCHANGED = "UNCHANGED"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
HISTORY_KEYS = AMENDED_KEYS | ADDED_KEYS
EXPECTED_STATUS_BY_KEY: dict[str, str] = {}
FLAGGED_DISCREPANCY_KEYS = {
    "child_protection_regulation_boe_no_dedicated_lawid_found",
    "child_protection_regulation_com_427_did_not_amend_regulation",
    "child_protection_regulation_websearch_summary_conflated_law_and_regulation",
    "child_protection_regulation_mirrors_base_law_original_pre_1443_text",
    "child_protection_regulation_chapter2_title_plural_vs_law_singular",
    "child_protection_regulation_moj_pdf_bidi_artifacts",
    "child_protection_regulation_wayback_https_worked_this_pass",
    "child_protection_regulation_jina_reader_blocked",
    "child_protection_regulation_art_015_source_typo_preserved",
    "child_protection_regulation_art_001_talqa_spelling_preserved",
    "child_protection_regulation_no_preamble_found",
    "child_protection_regulation_gregorian_date_not_pinpointed",
    "child_protection_regulation_distinct_from_base_law_track",
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

    chs = src.get("chapter_structure") or []
    n_top = len(chs)
    if n_top != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d chapters (فصول), got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

    covered = set()
    for lo, hi in _iter_chapter_ranges(chs):
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] article %d covered by more than one chapter range" % n)
            covered.add(n)
    if covered != set(range(1, N_NUMBERED + 1)):
        missing = sorted(set(range(1, N_NUMBERED + 1)) - covered)
        extra = sorted(covered - set(range(1, N_NUMBERED + 1)))
        if missing:
            e.append("[1c] chapter_structure missing article(s): %s" % missing[:20])
        if extra:
            e.append("[1c] chapter_structure covers out-of-range article(s): %s" % extra[:20])

    titles = [c.get("title_ar") for c in chs]
    if len(set(titles)) != len(titles):
        e.append("[1d] unexpected duplicate chapter title(s): %s"
                 % [t for t in titles if titles.count(t) > 1])

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
        if k in HISTORY_KEYS and not a.get("history"):
            e.append("[2] %s: amended/added article missing history" % k)
        if k not in HISTORY_KEYS and a.get("history"):
            e.append("[2i] %s: original article must have empty history[]" % k)
        if "title_ar" in a:
            e.append("[2i] %s: unexpected title_ar key present (source supplies no inline "
                     "per-article titles -- section_ar carries the chapter title)" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact (should be straight quotes)" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)

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
        e.append("[2k] missing amendment_history (must record the founding ministerial resolution)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "56386" not in decrees:
            e.append("[2k] amendment_history must reference the founding resolution 56386")

    # ---- structural / content spot-checks anchoring the central verification finding ----
    a1 = arts.get("child_protection_regulation_art_001", {})
    if "الثامنة عشرة" not in a1.get("text", "") or "الطفل" not in a1.get("text", ""):
        e.append("[2j] Article 1 missing expected definition of الطفل (under 18, reproduced from base law)")
    # NOTE: the source (nezams.com) spells this "تلقى" (alef maqsura) rather
    # than the standard "تلقي" -- a source-level spelling variant preserved
    # verbatim (no silent correction); see known_unresolved_discrepancies.
    if "38" not in a1.get("text", "") or "مركز تلقى البلاغات" not in a1.get("text", ""):
        e.append("[2j] Article 1 missing expected regulation-specific definitions (item 38, مركز تلقى البلاغات)")
    a25 = arts.get("child_protection_regulation_art_025", {})
    if "تسعين" not in a25.get("text", "") or "25/1" not in a25.get("text", ""):
        e.append("[2j] Article 25 missing expected 90-day clause and its 25/1 implementing sub-clause")
    a12 = arts.get("child_protection_regulation_art_012", {})
    if "السلوكي أو الفكري" in a12.get("text", ""):
        e.append("[3] Article 12 text must NOT contain the base law's 1443H-added phrase "
                 "(السلوكي أو الفكري) -- this regulation predates that amendment and was itself "
                 "independently confirmed unamended")
    a19 = arts.get("child_protection_regulation_art_019", {})
    if "وزارة الموارد البشرية والتنمية الاجتماعية" in a19.get("text", ""):
        e.append("[3] Article 19 text must NOT contain the base law's 1443H-amended wording -- "
                 "this regulation was independently confirmed unamended")

    if src.get("decree") != "القرار الوزاري رقم (56386)" or src.get("decree_date_hijri") != "16/6/1436":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Ministerial Resolution 56386, 16/6/1436H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (no amendment to this regulation was found)")

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
        print("FAIL: %d error(s) in Child Protection Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Saudi Arabian Child Protection Law")
    print("  - 25 records: all اصلية (0 معدلة, 0 ملغاة, 0 مضافة); no mukarrar; 5 chapters (فصول)")
    print("  - VERIFICATION TIER: TIER_3 -- laws.boe.gov.sa was unreachable this pass (HTTP 000")
    print("    connection-reset direct; HTTP 503 via WebFetch) and no dedicated lawId page for this")
    print("    regulation was found via indexed search. Full verbatim text from nezams.com (HTTP 200);")
    print("    decree identity + 5-chapter structure + 25-article count independently confirmed by the")
    print("    OFFICIAL Ministry of Justice Adl-journal PDF (adlm.moj.gov.sa/attach/1463.pdf, HTTP 200)")
    print("  - Ministerial Resolution No. 56386 (16/6/1436H), issued pursuant to Article 24 of the")
    print("    Child Protection Law (Royal Decree M/14, 3/2/1436H); published 29/10/1436H")
    print("  - CENTRAL FINDING: CoM Resolution 427 (1443H) / Royal Decree M/72, which amended the BASE")
    print("    LAW (Articles 12, 15, 19, 23 + added Article 23-mukarrar), independently confirmed NOT")
    print("    to have amended this regulation (nezams.com metadata: \"لم يجرِ عليه تعديل\"; Umm")
    print("    Al-Qura gazette title references the two LAWS, not their regulations). A general")
    print("    WebSearch summary conflating the two was rejected in favor of the primary-source check")
    print("  - DISTINCT, standalone track from child_protection_law (base law); does not modify any")
    print("    shared pipeline files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
