#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Law of the
Saudi Council of Engineers track (32 records, all اصلية; 6 named فصول, no
أبواب -- الفصل الثاني further subdivided into 5 lettered subsections).

VERIFICATION TIER -- see the generator's module docstring and
sources/saudi_engineers_regulation/law/official_source/
saudi_engineers_regulation_official_source.json's verification_methodology_
note for the full account: a direct live fetch of saudieng.sa's hosted PDF
failed (TLS reset) this pass; its single archived Wayback Machine snapshot
(20250625074825) was fetched instead and cross-extracted by two
structurally independent PDF-parsing pipelines (poppler pdftotext and a
from-scratch pdfplumber word-level bidi/glyph-order reconstruction), which
agree word-for-word after normalization. This is a Council-internal,
General-Assembly-approved instrument with no BOE-style per-article
amendment changelog -- all 32 articles are 'اصلية' relative to the single
verified current consolidated text, not a claim of identity with any
earlier internal edition. This validator does not attempt to re-adjudicate
any of this; it only checks internal self-consistency of the text this
track actually ingests, and that every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "saudi_engineers_regulation", "law", "official_source",
                   "saudi_engineers_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "saudi_engineers_regulation", "law", "verified",
                       "saudi_engineers_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "saudi_engineers_regulation", "law", "verified",
                       "saudi_engineers_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "saudi_engineers_regulation_arabic_legal_llm",
                   "saudi_engineers_regulation_legal_llm_001_032.json")
N = 32
KEY_RE = r"saudi_engineers_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 32, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 6  # 6 named فصول, no أبواب

STATUS_UNCHANGED = ("SAUDIENG_SA_WAYBACK_20250625_PRIMARY_X_PDFTOTEXT_POPPLER_AND_PDFPLUMBER_"
                     "PDFMINER_DUAL_INDEPENDENT_EXTRACTION_CROSSCHECK_LIVE_FETCH_TLS_RESET")
EXPECTED_STATUS_BY_KEY = {}  # every article shares STATUS_UNCHANGED
AMENDED_KEYS = set()
ADDED_KEYS = set()
REPEALED_KEYS = set()
MUKARRAR_KEYS = set()
FLAGGED_DISCREPANCY_KEYS = {
    "sce_reg_disambiguation_from_engineering_practice_regulation",
    "sce_reg_general_assembly_meeting_number_unconfirmed",
    "sce_reg_no_prior_edition_found_for_diff",
    "sce_reg_scribd_and_jina_fallbacks_unavailable",
    "sce_reg_hamza_style_and_minor_spelling_artifacts",
    "sce_reg_article29_stray_duplicate_numeral_artifact",
    "sce_reg_related_uningested_instruments",
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
    """Yield (lo, hi) for every leaf article range in chapter_structure.
    الفصل الثاني nests 5 lettered subsections under 'sections'; every other
    فصل is itself a leaf (no 'sections' key)."""
    for ch in chs:
        secs = ch.get("sections")
        if not secs:
            lo, hi = (int(x) for x in ch["articles"].split("-"))
            yield (lo, hi)
            continue
        for sec in secs:
            slo, shi = (int(x) for x in sec["articles"].split("-"))
            yield (slo, shi)


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
        e.append("[1c] expected %d top-level chapter_structure entries (6 named فصول, no "
                  "أبواب), got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

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
        expected_status = EXPECTED_STATUS_BY_KEY.get(k, STATUS_UNCHANGED)
        if a.get("status") != expected_status:
            e.append("[2] %s: expected status %r, got %r" % (k, expected_status, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip():
            e.append("[2] %s: empty text" % k)
        if re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: latin/html leftovers" % k)
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
        if "title_ar" in a:
            e.append("[2i] %s: unexpected title_ar key present (this source supplies no "
                      "inline per-article titles distinct from chapter/subsection headings -- "
                      "see known_unresolved_discrepancies)" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "ًً" in a["text"]:
            e.append("[2g] %s: residual doubled-tanwin artifact detected" % k)

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
        e.append("[2k] missing amendment_history (must record the single 1445H consolidated "
                  "edition)")
    else:
        decrees = " ".join(h.get("date_hijri", "") for h in src["amendment_history"])
        if "1445" not in decrees:
            e.append("[2k] amendment_history must reference 1445")

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("saudi_engineers_regulation_art_001", {})
    if "النظام: نظام الهيئة السعودية للمهندسين" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected النظام definition cross-referencing the base law")
    if "الجهة المشرفة: وزارة البلديات والإسكان" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected الجهة المشرفة definition")
    art4 = arts.get("saudi_engineers_regulation_art_004", {})
    if "عشرة أعضاء" not in art4.get("text", ""):
        e.append("[2j] Article 4 missing expected 10-member board clause")
    art11 = arts.get("saudi_engineers_regulation_art_011", {})
    if "أسلوب الترشح" not in art11.get("text", "") or "أسلوب الانتخاب" not in art11.get("text", ""):
        e.append("[2j] Article 11 missing expected candidacy/voting-method subheadings")
    art29 = arts.get("saudi_engineers_regulation_art_029", {})
    if "3٣" not in art29.get("text", ""):
        e.append("[2j] Article 29 missing the confirmed stray duplicate-numeral artifact "
                 "(should be preserved verbatim, not silently corrected)")
    art32 = arts.get("saudi_engineers_regulation_art_032", {})
    if "يعمل بهذه اللائحة" not in art32.get("text", ""):
        e.append("[2j] Article 32 missing expected entry-into-force clause")
    if src.get("article_count") != N:
        e.append("[2j] article_count mismatch with verified 32-article structure")

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
        print("FAIL: %d error(s) in Saudi Engineers Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Law of the Saudi Council of Engineers")
    print("  - 32 records: all اصلية (Council-internal instrument, no BOE-style per-article")
    print("    amendment changelog; single archived edition found, none marked معدلة)")
    print("  - 6 named فصول, no أبواب; الفصل الثاني subdivided into 5 lettered subsections")
    print("    (أ-هـ); no inline per-article titles (no title_ar key used)")
    print("  - VERIFICATION TIER: saudieng.sa via a single Wayback Machine snapshot")
    print("    (20250625074825, 25 Jun 2025; live fetch TLS-reset this pass), cross-extracted")
    print("    by two independent PDF-parsing pipelines (poppler pdftotext x a from-scratch")
    print("    pdfplumber bidi/glyph-order reconstruction) agreeing word-for-word")
    print("  - DISAMBIGUATION: confirmed distinct from the sibling engineering_practice_")
    print("    regulation track (a Ministerial-Resolution/Umm-Al-Qura-gazette instrument")
    print("    implementing a SEPARATE base law) via this pass's own read of that sibling's")
    print("    PDF (67.pdf) from the same saudieng.sa directory")
    print("  - CONFIRMED VERBATIM-PRESERVED ANOMALY (Article 29): a stray duplicate-numeral")
    print("    artifact ('3٣') mid-item-2, agreeing byte-for-byte across both independent")
    print("    extraction pipelines -- preserved, not silently corrected")
    print("  - Could NOT independently confirm a prior-research claim that this edition was")
    print("    approved at the '20th Ordinary General Assembly meeting, 2024' -- flagged as")
    print("    an honest unconfirmed attribution, not repeated as fact")
    return 0


if __name__ == "__main__":
    sys.exit(main())
