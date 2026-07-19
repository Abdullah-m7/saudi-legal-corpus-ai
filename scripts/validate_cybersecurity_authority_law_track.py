#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Statute (Organizational Regulation) of the
National Cybersecurity Authority track (15 records, all اصلية at the
per-article level, 0 معدلة, 0 ملغاة, 0 مضافة; flat structure -- NO
أبواب/فصول grouping).

VERIFICATION TIER -- see the generator's module docstring and
sources/cybersecurity_authority/law/official_source/
cybersecurity_authority_law_official_source.json's
verification_methodology_note for the full account: no laws.boe.gov.sa
page for this exact statute could be located this pass (repeated
WebSearch queries surfaced only OTHER BOE-catalogued laws that merely
cite this statute in passing; a direct curl to the portal returned
"Connection reset by peer"). The PRIMARY source actually used is an
official PDF hosted on the National Cybersecurity Authority's own website
(nca.gov.sa), whose embedded text layer has a confirmed, systematic
character-transposition artifact worked around via Tesseract OCR of
300dpi page renders, cross-checked word-by-word against the flawed-but-
complete pdftotext/fitz extraction and against qistas.com's independent
excerpt for Articles 1-3. This track is honestly assessed at TIER_2 (one
official/primary source + secondary cross-checks), not TIER_1, since no
second genuinely independent official source was located. The source's
own title page confirms an amendment (Royal Order 7053) exists at the
document level, but no source found this pass attributes it to a
specific article -- consolidated_amended_law is set to true, but no
individual article is marked معدلة absent specific evidence. This
validator does not attempt to re-adjudicate any of this; it only checks
internal self-consistency of the text this track actually ingests, and
that every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "cybersecurity_authority", "law", "official_source",
                   "cybersecurity_authority_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "cybersecurity_authority", "law", "verified",
                       "cybersecurity_authority_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "cybersecurity_authority", "law", "verified",
                       "cybersecurity_authority_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "cybersecurity_authority_arabic_legal_llm",
                   "cybersecurity_authority_law_legal_llm_001_015.json")
N = 15
KEY_RE = r"cybersecurity_authority_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 15, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 1  # flat statute -- no أبواب/فصول, single leaf range 1-15

STATUS_UNCHANGED = ("NCA_OFFICIAL_SITE_PDF_PRIMARY_TESSERACT_OCR_TRANSCRIBED_X_QISTAS_"
                     "STRUCTURAL_PARTIAL_CROSSCHECK_TIER2_BOE_PAGE_NOT_LOCATED")
EXPECTED_STATUS_BY_KEY = {}  # every article shares STATUS_UNCHANGED (all اصلية)
AMENDED_KEYS = set()
ADDED_KEYS = set()
REPEALED_KEYS = set()
MUKARRAR_KEYS = set()
FLAGGED_DISCREPANCY_KEYS = {
    "cybersecurity_authority_pdf_text_layer_letter_transposition_artifact",
    "cybersecurity_authority_7053_amendment_article_unattributed",
    "cybersecurity_authority_founding_order_55775_secondary_only",
    "cybersecurity_authority_no_named_predecessor_repeal_confirmed_negative",
    "cybersecurity_authority_enablers_m117_distinct_not_ingested",
    "cybersecurity_authority_boe_page_not_located",
    "cybersecurity_authority_sama_old_name_clue",
    "cybersecurity_authority_no_baab_fasl_structure",
    "cybersecurity_authority_no_inline_article_titles",
    "cybersecurity_authority_list_numerals_omitted_per_corpus_convention",
    "cybersecurity_authority_gap_map_estimate_confirmed",
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
    """Yield (lo, hi) for every leaf range in chapter_structure. This
    statute has no أبواب/فصول nesting -- every top-level entry IS a leaf
    (no 'sections' key), so this is a flat single-level walk."""
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
        e.append("[1c] expected %d top-level chapter_structure entries (flat statute, "
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
        expected_status = EXPECTED_STATUS_BY_KEY.get(k, STATUS_UNCHANGED)
        if a.get("status") != expected_status:
            e.append("[2] %s: expected status %r, got %r" % (k, expected_status, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
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
        if "title_ar" in a:
            e.append("[2i] %s: unexpected title_ar key present (source supplies no "
                      "inline per-article titles for this statute -- see "
                      "known_unresolved_discrepancies)" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "ًً" in a["text"]:
            e.append("[2g] %s: residual doubled-tanwin artifact detected" % k)
        if re.search(r"\(\s*\)\d", a["text"]):
            e.append("[2h] %s: residual bidi paren-before-digit artifact detected" % k)
        if re.search(r"^[0-9٠-٩]+[-.\s]", a["text"]):
            e.append("[2h] %s: text begins with a residual list-numeral marker "
                      "(should be omitted per corpus convention)" % k)

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
        e.append("[2k] missing amendment_history (must record 6801 and 7053)")
    else:
        decrees = " ".join(h.get("decree", "") for h in src["amendment_history"])
        for token in ("6801", "7053"):
            if token not in decrees:
                e.append("[2k] amendment_history must reference %s" % token)

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("cybersecurity_authority_art_001", {})
    if "الهيئة الوطنية للأمن السيبراني" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected الهيئة definition")
    art3 = arts.get("cybersecurity_authority_art_003", {})
    if "الجهة المختصة في المملكة بالأمن السيبراني" not in art3.get("text", ""):
        e.append("[2j] Article 3 missing expected competent-authority mandate clause")
    art6 = arts.get("cybersecurity_authority_art_006", {})
    if "محافظ الهيئة" not in art6.get("text", ""):
        e.append("[2j] Article 6 missing expected board-composition clause")
    art12 = arts.get("cybersecurity_authority_art_012", {})
    if "مؤسسة النقد العربي السعودي" not in art12.get("text", ""):
        e.append("[2j] Article 12 missing expected SAMA-name clause (see "
                 "cybersecurity_authority_sama_old_name_clue)")
    art15 = arts.get("cybersecurity_authority_art_015", {})
    if "يلغي كل ما يتعارض معه من أحكام" not in art15.get("text", ""):
        e.append("[2j] Article 15 missing expected generic repeal clause")
    if src.get("decree") != "الأمر الملكي رقم (6801)" or src.get("decree_date_hijri") != "11/2/1439":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Order 6801, 11/2/1439H")

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
        print("FAIL: %d error(s) in Cybersecurity Authority Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Statute (Organizational Regulation) of the National Cybersecurity Authority")
    print("  - 15 records, ALL اصلية at the per-article level (0 معدلة, 0 ملغاة, 0 مضافة)")
    print("  - flat structure, NO أبواب/فصول grouping (single leaf range 1-15); no")
    print("    inline per-article titles in the source (no title_ar key used)")
    print("  - VERIFICATION TIER: TIER_2 -- primary source is an official PDF on the")
    print("    National Cybersecurity Authority's own site (nca.gov.sa), OCR-")
    print("    transcribed to work around a confirmed text-layer letter-transposition")
    print("    artifact, cross-checked against qistas.com (partial, Arts. 1-3) and")
    print("    saudipedia.com; no laws.boe.gov.sa page for this exact statute could")
    print("    be located this pass, precluding a TIER_1 rating")
    print("  - Royal Order 6801 (11/2/1439H / ~31 Oct-1 Nov 2017G), amended by Royal")
    print("    Order 7053 (2/2/1443H) -- amendment confirmed at the document level")
    print("    (consolidated_amended_law=true) but NOT attributed to any specific")
    print("    article by any source found this pass (honest gap, not guessed)")
    print("  - CONFIRMED NEGATIVE FINDING: no named predecessor organizational statute")
    print("    is repealed by this instrument -- only a generic repeal clause (Art. 15)")
    print("  - A separate, newer, Royal-Decree-level instrument (م/117, 21/6/1446H,")
    print("    'الممكنات النظامية' -- licensing/violations/penalties) was found but is")
    print("    NOT ingested here, being textually and substantively distinct")
    return 0


if __name__ == "__main__":
    sys.exit(main())
