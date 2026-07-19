#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Domestic Labor Regulation track
(33 records, all اصلية -- 0 معدلة, 0 ملغاة, 0 مضافة; flat 14-section
structure, no formal أبواب/فصول numbering).

VERIFICATION TIER -- see the generator's module docstring and
sources/domestic_labor/regulation/official_source/
domestic_labor_regulation_official_source.json's verification_methodology_note
for the full account: laws.boe.gov.sa was checked FIRST (per this corpus's
standard methodology) but its only page for this topic is confirmed STALE --
even the most recent archived Wayback Machine snapshot (6 Sep 2025) shows only
the superseded 2013/1434H predecessor, not the current 2023/1445H regulation.
The PRIMARY source actually used is hrsd.gov.sa (the issuing Ministry's own
site), cross-verified against qanoonsa.com and lexismiddleeast.com. That
primary source is itself confirmed truncated (Article 33's text ends
mid-sentence) and its cover/preamble retains an unfilled draft template --
both disclosed, not silently fixed. This validator does not re-adjudicate any
of this; it only checks internal self-consistency of the text this track
actually ingests, and that every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "domestic_labor", "regulation", "official_source",
                   "domestic_labor_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "domestic_labor", "regulation", "verified",
                       "domestic_labor_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "domestic_labor", "regulation", "verified",
                       "domestic_labor_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "domestic_labor_arabic_legal_llm",
                   "domestic_labor_regulation_legal_llm_001_033.json")
N = 33
KEY_RE = r"domestic_labor_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 33, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_SECTIONS = 14  # thematic sections, no أبواب/فصول numbering

STATUS_UNCHANGED = "UNCHANGED"
STATUS_INCOMPLETE = "ORIGINAL_TEXT_INCOMPLETE"
INCOMPLETE_NUMS = (33,)
INCOMPLETE_KEYS = {"domestic_labor_art_%03d" % n for n in INCOMPLETE_NUMS}
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY = {k: STATUS_INCOMPLETE for k in INCOMPLETE_KEYS}
FLAGGED_DISCREPANCY_KEYS = {
    "domestic_labor_gap_map_estimate_was_for_predecessor",
    "domestic_labor_boe_portal_stale",
    "domestic_labor_article33_truncated",
    "domestic_labor_draft_template_artifact",
    "domestic_labor_missing_space_typo",
    "domestic_labor_toc_item3_untitled",
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


def _iter_section_ranges(chs):
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
    if n_top != EXPECTED_TOP_LEVEL_SECTIONS:
        e.append("[1c] expected %d thematic sections (no formal أبواب/فصول), "
                  "got %d" % (EXPECTED_TOP_LEVEL_SECTIONS, n_top))

    covered = set()
    for lo, hi in _iter_section_ranges(chs):
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] article %d covered by more than one section range" % n)
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
        # ligature-extraction-bug regression guard (تر -> بخ font bug fixed at build time)
        for w in re.findall(r"[%s]*بخ[%s]*" % (AR, AR), a["text"]):
            if w != "بخلاف":
                e.append("[2g] %s: unresolved 'بخ' ligature-extraction artifact: %r" % (k, w))
        if k in INCOMPLETE_KEYS and a.get("text_complete") is not False:
            e.append("[2h] %s: expected text_complete=False (source-truncated article)" % k)
        if k not in INCOMPLETE_KEYS and a.get("text_complete") is False:
            e.append("[2h] %s: unexpectedly marked text_complete=False" % k)

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
        e.append("[2k] missing amendment_history (must record founding decree)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "40676" not in decrees:
            e.append("[2k] amendment_history must reference decree 40676")

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("domestic_labor_art_001", {})
    if "صاحب العمل المنزلي" not in art1.get("text", "") or "591" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected definitions (صاحب العمل المنزلي) or "
                 "insurance-instructions reference (Council of Ministers Resolution 591)")
    art6 = arts.get("domestic_labor_art_006", {})
    if "واحد وعشرين" not in art6.get("text", ""):
        e.append("[2j] Article 6 missing expected minimum-age (21 years) prohibition")
    art33 = arts.get("domestic_labor_art_033", {})
    if not art33.get("text", "").rstrip().endswith("وترحيل"):
        e.append("[2j] Article 33 text should end at the confirmed source truncation point "
                 "('...وترحيل') -- do not silently complete or alter it")
    if src.get("decree") != "القرار الوزاري رقم 40676" or src.get("decree_date_hijri") != "17/3/1445":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Ministerial Decision "
                 "40676, 17/3/1445H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (this is a founding single-version "
                 "instrument, not a consolidated multi-amendment law)")
    preamble = src.get("preamble_ar", "")
    if "قرار وزاري رقم" not in preamble or "310" not in preamble:
        e.append("[2j] preamble_ar must preserve the ministerial decision text verbatim, "
                 "including its reference to predecessor Decision 310")

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
        print("FAIL: %d error(s) in Domestic Labor Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Saudi Arabian Domestic Labor Regulation")
    print("  - 33 records: 33 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة")
    print("  - flat 14-section thematic structure, no formal أبواب/فصول numbering")
    print("  - VERIFICATION TIER: TIER_2 -- laws.boe.gov.sa checked first but confirmed STALE for")
    print("    this topic (still shows the superseded 2013/1434H predecessor as of its most recent")
    print("    archived snapshot, 6 Sep 2025); PRIMARY source is hrsd.gov.sa (the issuing Ministry's")
    print("    own site), cross-verified against qanoonsa.com (decree/date/repeal) and")
    print("    lexismiddleeast.com (33-article structure)")
    print("  - Ministerial Decision No. 40676 (17/3/1445H / 2 Oct 2023G), issued by the Minister of")
    print("    Human Resources and Social Development under Labor Law Article 7 (M/51, 23/8/1426H)")
    print("  - CONFIRMED NAMED REPEAL: replaces لائحة عمال الخدمة المنزلية ومن في حكمهم (Council of")
    print("    Ministers Decision 310, 7/9/1434H, 23 articles) -- not in this corpus, historical")
    print("    context only")
    print("  - ANOMALY: primary source PDF is genuinely truncated (Article 33 ends mid-sentence,")
    print("    text_complete=False, not fabricated) and its own cover/preamble retains an unfilled")
    print("    draft template (blank decree number/date placeholders, 'مسودة' header) -- both")
    print("    confirmed stable across 18+ months of Wayback snapshots, i.e. genuine source defects")
    print("  - Two source-artifact-layer (not content) defects corrected: a font ligature-extraction")
    print("    bug ('تر' -> 'بخ', fixed via 10-word dictionary) and mirrored/reversed parentheses")
    print("    (fixed via global paren swap); diacritics stripped uniformly for corpus consistency")
    return 0


if __name__ == "__main__":
    sys.exit(main())
