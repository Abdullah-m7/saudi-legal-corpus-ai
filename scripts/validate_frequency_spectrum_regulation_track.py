#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Frequency Spectrum Regulations for Radio
Services and Applications track (تنظيمات استخدامات الطيف الترددي للخدمات
الراديوية وتطبيقاتها, document code RS45, First Edition, CST Decision No.
559/1446, dated 23/7/1446H = 23/1/2025G; 15 records, all اصلية, General
Framework only -- the document's own six technical annexes are NOT
ingested this pass, see known_unresolved_discrepancies).

VERIFICATION TIER -- see the generator's module docstring and
sources/frequency_spectrum_regulation/law/official_source/
frequency_spectrum_regulation_official_source.json's verification_methodology_note
for the full account. This validator asserts: exactly 15 articles in a
clean 1..15 run; exactly 7 chapter_structure entries (1 ingested General
Framework + 6 explicitly-flagged NOT-ingested annexes); all 15 articles are
اصلية with empty amendment history (single, first-and-only edition); no
ملغاة/معدلة/مضافة articles this pass; number_label_ar stores the bare
numeral only (no fabricated "المادة"/"البند"/"القسم" noun); preamble_ar
(the Decision's own recital text) is present and mentions the six merged
predecessor regulations.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "frequency_spectrum_regulation", "law", "official_source",
                   "frequency_spectrum_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "frequency_spectrum_regulation", "law", "verified",
                       "frequency_spectrum_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "frequency_spectrum_regulation", "law", "verified",
                       "frequency_spectrum_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "frequency_spectrum_regulation_arabic_legal_llm",
                   "frequency_spectrum_regulation_legal_llm_001_015.json")
N = 15
KEY_RE = r"frequency_spectrum_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 15, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
STATUS = "CST_OFFICIAL_PDF_PRIMARY_VISUAL_TRANSCRIPTION_EN_STRUCTURAL_CROSSCHECK"
EXPECTED_CHAPTER_ENTRIES = 7
EXPECTED_NOT_INGESTED_ANNEXES = 6
FLAGGED_DISCREPANCY_KEYS = {
    "frequency_spectrum_regulation_six_annexes_not_ingested",
    "frequency_spectrum_regulation_title_naming_variance",
    "frequency_spectrum_regulation_no_madda_convention",
    "frequency_spectrum_regulation_single_ar_primary_source_en_structural_crosscheck_only",
    "frequency_spectrum_regulation_clause_15_4_word_disambiguation",
    "frequency_spectrum_regulation_six_predecessor_regulations_not_ingested",
    "frequency_spectrum_regulation_tesseract_ocr_infra_failure",
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


def main():
    for p in (SRC, RECORDS, SUMMARY, LLM):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1

    e = []
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))
    if src.get("article_count") != N:
        e.append("[1] article_count field %r != %d" % (src.get("article_count"), N))
    seen = set()
    for k in arts:
        m = re.match(KEY_RE, k)
        if not m:
            e.append("[1] %s: does not match key pattern" % k)
        else:
            seen.add(int(m.group(1)))
    if seen != set(range(1, N + 1)):
        e.append("[1] article numbers not a clean 1..%d run: %s" % (N, sorted(seen)))

    # number_label_ar must be the bare numeral only (no المادة/البند/القسم noun
    # fabricated) -- honesty check specific to this track's own documented finding.
    for k, a in arts.items():
        lbl = a.get("number_label_ar", "")
        if not re.fullmatch(r"\d{1,2}", lbl):
            e.append("[1b] %s: number_label_ar %r must be a bare numeral (no "
                      "المادة/البند/القسم noun fabricated)" % (k, lbl))
        for bad_noun in ("المادة", "البند", "القسم"):
            if bad_noun in lbl:
                e.append("[1b] %s: number_label_ar contains fabricated noun %r"
                          % (k, bad_noun))

    chapters = src.get("chapter_structure")
    if not chapters or len(chapters) != EXPECTED_CHAPTER_ENTRIES:
        e.append("[1c] expected %d chapter_structure entries (1 ingested General "
                 "Framework + 6 not-ingested annexes), got %r"
                 % (EXPECTED_CHAPTER_ENTRIES, chapters))
    else:
        ingested = [c for c in chapters if c.get("ingested")]
        not_ingested = [c for c in chapters if not c.get("ingested")]
        if len(ingested) != 1:
            e.append("[1c] expected exactly 1 ingested chapter_structure entry "
                     "(الإطار العام), got %d" % len(ingested))
        elif ingested[0].get("label_ar") != "الإطار العام":
            e.append("[1c] the ingested entry should be labeled الإطار العام, got %r"
                     % ingested[0].get("label_ar"))
        elif ingested[0].get("sections") != "1-15":
            e.append("[1c] الإطار العام sections span should be '1-15', got %r"
                     % ingested[0].get("sections"))
        if len(not_ingested) != EXPECTED_NOT_INGESTED_ANNEXES:
            e.append("[1c] expected exactly %d not-ingested annex entries, got %d"
                     % (EXPECTED_NOT_INGESTED_ANNEXES, len(not_ingested)))
        for c in not_ingested:
            if not c.get("label_ar", "").startswith("الملحق"):
                e.append("[1c] not-ingested entry label %r does not start with الملحق"
                         % c.get("label_ar"))
            if c.get("sections") is not None:
                e.append("[1c] not-ingested annex %r should have sections=None "
                         "(no fabricated section text)" % c.get("label_ar"))

    if src.get("consolidated_amended_law") is not True:
        e.append("[1d] consolidated_amended_law must be True for this track "
                 "(it consolidates six prior regulations)")
    if not (src.get("preamble_ar") or "").strip():
        e.append("[1e] preamble_ar (the Decision's own recital text) must be non-empty")
    else:
        preamble = src["preamble_ar"]
        for must_have in ("أولا", "ثانيا", "ثالثا", "1445/503", "1445/553",
                          "1443/474", "1445/546", "1445/547", "1445/548"):
            if must_have not in preamble:
                e.append("[1e] preamble_ar must contain %r (decision recital / "
                         "one of the six merged predecessor decree numbers)"
                         % must_have)

    sc = Counter()
    for k, a in arts.items():
        n = int(re.match(KEY_RE, k).group(1))
        if a.get("status") != STATUS:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            # EIRP/ITU/WLAN/IMT are legitimate acronyms quoted inside definitions;
            # allow those specific tokens only, flag anything else Latin.
            stripped = a["text"]
            for tok in ("EIRP", "ITU", "WLAN", "IMT"):
                stripped = stripped.replace(tok, "")
            if not a["text"].strip() or re.search(r"[A-Za-z<>&]", stripped):
                e.append("[2] %s: empty text or unexpected latin/html leftovers" % k)
        if not a.get("section_ar", "").strip():
            e.append("[2] %s: section_ar must be non-empty" % k)
        if not a.get("article_title_ar", "").strip():
            e.append("[2] %s: article_title_ar must be non-empty (source captions "
                     "every section)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if re.search(r"[٠-٩]", a["text"]):
            e.append("[2] %s: residual Eastern-Arabic-Indic digit (must be normalized)" % k)
        if "  " in a["text"]:
            e.append("[2] %s: residual double-space artifact" % k)
        if not a.get("number_label_ar"):
            e.append("[2] %s: missing number_label_ar" % k)

        # single, first-and-only-confirmed edition: every article must be اصلية, no history
        if ls != "اصلية":
            e.append("[3] %s: section %d expected اصلية (no amendment confirmed this "
                     "pass), got %r" % (k, n, ls))
        if a.get("history"):
            e.append("[3] %s: section %d must have empty history (اصلية-only track)" % (k, n))

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))
    declared = src.get("status_counts") or {}
    for st in ALLOWED_STATUS:
        if declared.get(st, 0) != sc.get(st, 0):
            e.append("[2f] declared status_counts[%s] does not match actual per-article counts" % st)

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

    if src.get("law_component") != "regulation":
        e.append("[2j] law_component must be 'regulation'")
    if src.get("legal_status_ar") != "نافذ":
        e.append("[2j] legal_status_ar must be نافذ")

    amend_hist = src.get("amendment_history")
    if not amend_hist or len(amend_hist) != 7:
        e.append("[2k] expected 7 amendment_history entries (6 merged predecessor "
                 "regulations + this consolidated edition itself), got %r"
                 % (len(amend_hist) if amend_hist else amend_hist))

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[4] %s: unknown article_key" % r["article_key"]); continue
        if r.get("law_component") != "regulation":
            e.append("[4] %s: law_component must be 'regulation', got %r"
                     % (r["article_key"], r.get("law_component")))
        if "article_number" not in r:
            e.append("[4] %s: missing article_number field" % r["article_key"])
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        if r.get("is_amended") is not False or r.get("is_repealed") is not False or r.get("is_added") is not False:
            e.append("[4] %s: expected all status flags False (اصلية-only track)" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts mismatch with source")
    if not (summary.get("preamble_ar") or "").strip():
        e.append("[4b] summary missing preamble_ar")

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    for r in recs:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[5] %s: unknown article_key" % r["article_key"]); continue
        if r.get("law_component") != "regulation":
            e.append("[5] %s: law_component must be 'regulation', got %r"
                     % (r["article_key"], r.get("law_component")))
        if "article_number" not in r:
            e.append("[5] %s: missing article_number field" % r["article_key"])
        if r["article_text_ar"] != a["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != STATUS.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Frequency Spectrum Regulation track:" % len(e))
        for x in e[:25]:
            print("  - %s" % x)
        return 1
    print("PASS: Frequency Spectrum Regulations for Radio Services and Applications "
          "— 15 records (15 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة; General Framework only)")
    print("  - TIER: cst.gov.sa official PDF, primary visual transcription "
          "(vector-rendered, no text layer), EN-PDF structural cross-check "
          "(section/clause counts only)")
    print("  - IN-FORCE CST Decision No. 559/1446 (23/7/1446H = 23/1/2025G)")
    print("  - Six technical annexes (WLAN/IMT/Maritime/Broadcasting/Fixed Wireless "
          "Links/Amateur Radio, ~87%% of the document) NOT ingested this pass -- "
          "deliberate, fully-disclosed scope limitation")
    print("  - CONFIRMED six merged predecessor regulations superseded (per the "
          "Decision's own preamble_ar text) -- not ingested individually (out of scope)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
