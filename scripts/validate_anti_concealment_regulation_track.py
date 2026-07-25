#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Anti-Concealment
Law track (اللائحة التنفيذية لنظام مكافحة التستر; 18 records, all اصلية; no
chapters/فصول of the base law's kind -- 9 unnumbered topical section headings
instead, matching the source's own table of contents).

VERIFICATION TIER -- see the generator's module docstring and sources/
anti_concealment_regulation/law/official_source/
anti_concealment_regulation_official_source.json's verification_methodology_note
for the full account: single direct official primary source (Ministry of
Commerce PDF, mc.gov.sa/ar/CC/D/RCC.pdf, vision-read in full after resolving
a server-side TLS chain gap), cross-checked against an independent Saudi
Press Agency (SPA) news article -> TIER_2. The founding resolution's number
(00479) and date (20/7/1442H) rest on convergent indirect evidence, not a
verbatim reading of the signed resolution -- this validator enforces that
this nuance stays disclosed rather than silently upgraded. This validator
does not re-adjudicate provenance; it only checks internal self-consistency
and that every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "anti_concealment_regulation", "law", "official_source",
                   "anti_concealment_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "anti_concealment_regulation", "law", "verified",
                       "anti_concealment_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "anti_concealment_regulation", "law", "verified",
                       "anti_concealment_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "anti_concealment_regulation_arabic_legal_llm",
                   "anti_concealment_regulation_legal_llm_001_018.json")
N = 18
KEY_RE = r"anti_concealment_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 18, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
STATUS = "PRIMARY_MC_GOVSA_PDF_X_SPA_OFFICIAL_CORROBORATION_TIER2"
EXPECTED_SECTIONS = 9
FLAGGED_DISCREPANCY_KEYS = {
    "anti_concealment_regulation_resolution_number_not_directly_read",
    "anti_concealment_regulation_uqn_wayback_jina_inaccessible",
    "anti_concealment_regulation_boe_503",
    "anti_concealment_regulation_qanoniah_js_gated",
    "anti_concealment_regulation_mc_govsa_tls_chain_incomplete",
    "anti_concealment_regulation_no_amendment_found",
    "anti_concealment_regulation_no_chapter_fasl_labels",
    "anti_concealment_regulation_tashkeel_stripped",
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
    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != list(range(1, N + 1)):
        e.append("[1b] article numbers not a contiguous 1..%d range: got %s" % (N, nums))

    chapters = src.get("chapter_structure") or []
    if len(chapters) != EXPECTED_SECTIONS:
        e.append("[1c] expected %d topical sections, got %d" % (EXPECTED_SECTIONS, len(chapters)))
    for ch in chapters:
        if "label_ar" in ch:
            e.append("[1c] chapter_structure entry has a label_ar field, but this source has "
                     "no فصل/باب numbering -- must use title_ar only: %r" % ch)
        if not ch.get("title_ar") or not ch.get("articles"):
            e.append("[1c] chapter_structure entry missing title_ar/articles: %r" % ch)

    sc = Counter()
    for k, a in arts.items():
        if a.get("status") != STATUS:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS, a.get("status")))
        if a.get("verification_tier") != STATUS:
            e.append("[2] %s: missing/mismatched verification_tier" % k)
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar (expected a topical section title)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present" % k)
        if a.get("history"):
            e.append("[2] %s: unexpected non-empty amendment history (no amendments found)" % k)
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

    # Honesty gate: the resolution number/date must stay flagged as convergent-indirect
    # evidence, not silently upgraded to "verbatim primary reading".
    if src.get("founding_resolution_confirmation_basis") != \
            "convergent_indirect_evidence_not_direct_primary_reading":
        e.append("[2g] founding_resolution_confirmation_basis must disclose the indirect "
                 "nature of the 00479/20-7-1442H confirmation")
    decree_text = str(src.get("decree", ""))
    if "00479" in decree_text and "لم يُقرأ" not in decree_text:
        e.append("[2g] decree field mentions 00479 without flagging that its signed text "
                 "was not read verbatim")
    if src.get("preamble_ar") not in ("", None):
        e.append("[2l] preamble_ar must be empty -- no resolution preamble/enacting text "
                 "was located this pass; a non-empty value would risk fabrication")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (no confirmed amendment found "
                 "this pass)")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")

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
            e.append("[5] %s: law_component must be 'regulation'" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != STATUS.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    # spot-checks anchoring key facts against the vision-read source text
    art1 = arts.get("anti_concealment_regulation_art_001", {}).get("text", "")
    if "اللجنة المنصوص عليها في الفقرة (4) من المادة (الخامسة)" not in art1:
        e.append("[2j] Article 1 missing expected اللجنة definition cross-reference")
    art6 = arts.get("anti_concealment_regulation_art_006", {}).get("text", "")
    for token in ("أ.", "ب.", "ج.", "د.", "هـ.", "و.", "ز.", "ح.", "ط.", "ي."):
        if token not in art6:
            e.append("[2j] Article 6 (محضر الضبط) missing expected item %r" % token)
    art18 = arts.get("anti_concealment_regulation_art_018", {}).get("text", "")
    if "الجريدة الرسمية" not in art18:
        e.append("[2j] Article 18 (publication clause) missing expected gazette token")

    if e:
        print("FAIL: %d error(s) in Anti-Concealment Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Anti-Concealment Law")
    print("  (اللائحة التنفيذية لنظام مكافحة التستر) — 18 records, all اصلية")
    print("  - 9 unnumbered topical sections (no فصل/باب labelling in source)")
    print("  - VERIFICATION TIER: TIER_2 -- single direct official primary source (Ministry")
    print("    of Commerce PDF, mc.gov.sa/ar/CC/D/RCC.pdf), vision-read in full; cross-checked")
    print("    against an independent Saudi Press Agency (SPA) news article")
    print("  - Resolution No. 00479 (20/7/1442H): confirmed by CONVERGENT INDIRECT evidence")
    print("    only (indexed gazette page title, aggregated web citations, PDF file-creation")
    print("    metadata) -- its signed text was NOT read verbatim this pass; disclosed, not")
    print("    silently upgraded")
    print("  - no confirmed amendment found this pass; all 18 articles اصلية")
    return 0


if __name__ == "__main__":
    sys.exit(main())
