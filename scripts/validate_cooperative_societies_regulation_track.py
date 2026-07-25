#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Cooperative
Societies Law track (55 records: 55 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة;
9 أبواب, 13 chapter-structure ranges since باب 1/2 are further split into
فصول/أولاً-ثانياً subsections).

VERIFICATION TIER -- see the generator's module docstring and
sources/cooperative_societies_regulation/law/official_source/
cooperative_societies_regulation_official_source.json's
verification_methodology_note for the full account: full text fetched
directly (HTTP 200) as an image-scanned PDF, cross-corroborated between two
independent official bodies (ncnp.gov.sa and cscs.org.sa). No extractable
text layer -- every article was transcribed by directly reading rendered
page images. This validator does not re-adjudicate any of this; it only
checks internal self-consistency of the text this track ingests, and that
every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "cooperative_societies_regulation", "law", "official_source",
                   "cooperative_societies_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "cooperative_societies_regulation", "law", "verified",
                       "cooperative_societies_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "cooperative_societies_regulation", "law", "verified",
                       "cooperative_societies_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "cooperative_societies_regulation_arabic_legal_llm",
                   "cooperative_societies_regulation_legal_llm_001_055.json")
N = 55
KEY_RE = r"cooperative_societies_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 55, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_CHAPTER_RANGES = 13  # 9 أبواب, with باب 1 (4 فصول) and باب 2 (أولا/ثانيا) further split

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY: dict[str, str] = {}
FLAGGED_DISCREPANCY_KEYS = {
    "cooperative_societies_regulation_decree_number_reading_uncertain",
    "cooperative_societies_regulation_article1_internal_date_order_variance",
    "cooperative_societies_regulation_border_clipped_headers_pp16",
    "cooperative_societies_regulation_no_amendment_history_available_this_pass",
    "cooperative_societies_regulation_article52_table_transcribed_as_running_text",
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
    if n_top != EXPECTED_CHAPTER_RANGES:
        e.append("[1c] expected %d chapter-structure ranges, got %d" % (EXPECTED_CHAPTER_RANGES, n_top))

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
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly)" % k)
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
            e.append("[2f] %s: residual curly-quote artifact detected (should be normalized "
                     "to straight quotes)" % k)
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
        e.append("[2k] missing amendment_history (must record founding decision)")

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("cooperative_societies_regulation_art_001", {})
    if "الجمعية" not in art1.get("text", "") or "الوزارة" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected definitions clause")
    art54 = arts.get("cooperative_societies_regulation_art_054", {})
    if "مجلس الجمعيات التعاونية" not in art54.get("text", ""):
        e.append("[2j] Article 54 missing expected Cooperative Societies Council establishment clause")

    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (no confirmed amendments this pass)")

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
            e.append("[5] %s: llm law_component must be 'regulation'" % r["article_key"])
        if r.get("article_number") is None:
            e.append("[5] %s: llm record missing article_number" % r["article_key"])
        expected_status = EXPECTED_STATUS_BY_KEY.get(r["article_key"], STATUS_UNCHANGED)
        if r.get("source_trust", {}).get("source_status") != expected_status.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Cooperative Societies Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Cooperative Societies Law")
    print("  - 55 records: 55 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة")
    print("  - 9 أبواب (13 chapter-structure ranges; أبواب 1-2 further split into فصول/أولاً-ثانياً)")
    print("  - VERIFICATION TIER: direct fetch (HTTP 200) of an image-scanned PDF, cross-corroborated")
    print("    between two independent official bodies (ncnp.gov.sa and cscs.org.sa); every article")
    print("    transcribed from rendered page images (no extractable text layer exists in the source)")
    print("  - Legal basis: Cooperative Societies Law Article 42 (Royal Decree M/14, 10/3/1429H);")
    print("    Ministerial Decision No. 52068 -- exact day/month obscured by a cover-page ink stamp,")
    print("    NOT fabricated here (see known_unresolved_discrepancies)")
    print("  - No confirmed amendment found this pass (absence-of-evidence, not proof of none existing)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
