#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Zakat Collection Implementing Regulation
track (128 records, consolidated amended law: 127 اصلية / 1 معدلة, 5
أبواب / 16 فصول / 12 فروع).

DISTINCT, WEAKER VERIFICATION TIER -- see the generator's module
docstring and sources/zakat/law/official_source/
zakat_law_official_source.json's verification_methodology_note for the
full caveat: ZATCA's own official PDF is the SOLE full-text primary
source this pass (single-source tier), with the Umm Al-Qura Gazette used
only for targeted spot-verification, not a second full-text diff.
IMPORTANT: this validator does NOT require original_1445h_text on the
single معدلة article (Article 73) -- its pre-amendment text was not
recovered from any source checked this pass (a documented gap, not a
fabrication)."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "zakat", "law", "official_source",
                   "zakat_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "zakat", "law", "verified",
                       "zakat_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "zakat_arabic_legal_llm",
                   "zakat_law_legal_llm_001_128.json")
N = 128
KEY_RE = r"zakat_law_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 127, "معدلة": 1}
STATUS = "ZATCA_PDF_PRIMARY_SINGLE_SOURCE_GAZETTE_SPOT_VERIFIED"
EXPECTED_BABS = 5
EXPECTED_FUSUL = 16
EXPECTED_FUROU = 12
AMENDED_KEYS = {"zakat_law_art_073"}
FLAGGED_DISCREPANCY_KEYS = {
    "zakat_law_base_decree_not_verbatim",
    "zakat_law_single_source_no_boe_cross_check",
    "zakat_law_prior_regulation_repeal_clause_not_in_operative_text",
    "zakat_law_resolution_1007_date_upgraded_confidence",
    "zakat_law_200k_400k_sar_claim_debunked",
    "zakat_law_article13_malak_vs_mulak_disambiguation",
    "zakat_law_ligature_extraction_bug_family",
    "zakat_law_line_order_scrambling_residual",
    "zakat_law_article73_original_text_not_recovered",
    "zakat_law_gstc_guide_not_used_for_operative_text",
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


def _count_chapters(chapter_structure):
    fusul = sum(len(b.get("chapters", [])) for b in chapter_structure)
    farou = sum(len(f.get("sections", [])) for b in chapter_structure
                for f in b.get("chapters", []))
    return len(chapter_structure), fusul, farou


def main():
    e = []
    for p in (SRC, RECORDS, LLM):
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
    for k in AMENDED_KEYS:
        if k not in arts:
            e.append("[1] expected amended article key %s missing" % k)

    chapters = src.get("chapter_structure") or []
    n_bab, n_fasl, n_farr = _count_chapters(chapters)
    if n_bab != EXPECTED_BABS:
        e.append("[1c] expected %d أبواب, got %d" % (EXPECTED_BABS, n_bab))
    if n_fasl != EXPECTED_FUSUL:
        e.append("[1c] expected %d فصول, got %d" % (EXPECTED_FUSUL, n_fasl))
    if n_farr != EXPECTED_FUROU:
        e.append("[1c] expected %d فروع, got %d" % (EXPECTED_FUROU, n_farr))

    sc = Counter()
    for k, a in arts.items():
        if a.get("status") != STATUS:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            # BOT/BOOT/BOO/AOT (build-operate-transfer contract abbreviations)
            # are legitimate Latin content in Articles 49 and 74; whitelist
            # those two articles only.
            if k not in ("zakat_law_art_049", "zakat_law_art_074"):
                e.append("[2] %s: empty text or unexpected latin/html leftovers" % k)
        if not a.get("title_ar"):
            e.append("[2] %s: missing title_ar" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar (expected a باب/فصل path)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        # lam-alef ligature-bug signatures must not survive into the final text
        if "الالئحة" in a["text"] or re.search(r"ا[أإآ]ل", a["text"]):
            e.append("[2f] %s: residual lam-alef ligature-bug signature detected" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة") or sc.get("مضافة"):
        e.append("[2] unexpected repealed/added articles present")

    # Article 73 must carry its Resolution 1248 amendment history.
    art73 = arts.get("zakat_law_art_073", {})
    hist73 = " ".join(h.get("date_hijri", "") for h in art73.get("history", []))
    if "11/10/1446" not in hist73:
        e.append("[2g] zakat_law_art_073: expected Resolution 1248 date "
                 "(11/10/1446H) recorded in history")

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

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts[r["article_key"]]
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        if r.get("original_1445h_text") != a.get("original_1445h_text"):
            e.append("[4] %s: original_1445h_text not propagated" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    for r in recs:
        if r["article_text_ar"] != arts[r["article_key"]]["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != STATUS.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Zakat Law track:" % len(e))
        for x in e[:30]:
            print("  - %s" % x)
        return 1
    print("PASS: Zakat Collection Implementing Regulation — 128 records (127 اصلية / 1 معدلة)")
    print("  - 5 أبواب / 16 فصول / 12 فروع")
    print("  - SINGLE-SOURCE TIER: ZATCA official PDF only (sole full-text primary source);")
    print("    Umm Al-Qura Gazette spot-verified for Resolution 1007 date and Article 13 title")
    print("  - IN-FORCE Minister of Finance Resolution No. 1007 (19/8/1445H); amended once by")
    print("    Resolution No. 1248 (11/10/1446H, Article 73 only)")
    print("  - lam-alef ligature PDF-extraction bug (الأصول/الإقرار/اللائحة/etc.) fixed via")
    print("    general regex + curated dictionary + context-anchored homograph resolution")
    print("  - no original_1445h_text populated for Article 73, a documented gap not a")
    print("    fabrication; base decree 17/2/28/8634 text not transcribed verbatim (gap)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
