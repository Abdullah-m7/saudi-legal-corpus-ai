#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the customs_law track (188 records, consolidated
amended law: 176 اصلية / 9 مضافة / 3 معدلة; 17 أبواب).

SINGLE-SOURCE TIER -- see the generator's module docstring and
sources/customs/law/official_source/customs_law_official_source.json's
verification_methodology_note for the full caveat: ZATCA's own official
PDF is the SOLE full-text primary source this pass (shared with
customs_regulation), with laws.boe.gov.sa confirmed unreachable.
IMPORTANT: this validator does NOT require original_1423h_text on the 3
معدلة articles (61, 72, 102) -- their pre-amendment text was not
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
SRC = os.path.join(ROOT, "sources", "customs", "law", "official_source",
                   "customs_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "customs", "law", "verified",
                       "customs_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "customs_arabic_legal_llm",
                   "customs_law_legal_llm_001_188.json")
N = 188
KEY_RE = r"customs_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 176, "مضافة": 9, "معدلة": 3}
STATUS = "ZATCA_PDF_PRIMARY_SINGLE_SOURCE_BOE_UNREACHABLE"
EXPECTED_BABS = 17
AMENDED_KEYS = {"customs_law_art_061", "customs_law_art_072", "customs_law_art_102"}
MUKARRAR_KEYS = {
    "customs_law_art_024_mukarrar", "customs_law_art_029_mukarrar",
    "customs_law_art_047_mukarrar", "customs_law_art_047_mukarrar2",
    "customs_law_art_048_mukarrar", "customs_law_art_104_mukarrar",
    "customs_law_art_141_mukarrar", "customs_law_art_150_mukarrar",
    "customs_law_art_177_mukarrar",
}
FLAGGED_DISCREPANCY_KEYS = {
    "customs_law_nezams_unreliable",
    "customs_law_m14_articles_unconfirmed",
    "customs_law_bis_articles_decree_attribution_unconfirmed",
    "customs_law_boe_unreachable",
    "customs_law_gcc_baseline_vs_saudi_domestic_text",
    "customs_law_ligature_and_lam_drop_bug_family",
    "customs_law_line_order_scrambling_11_articles_hand_reconstructed",
    "customs_law_article171_172_false_boundary_corrected",
    "customs_law_47_mukarrar_duplicate_numbering_resolved",
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


def _count_babs(chapter_structure):
    return len(chapter_structure)


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
    for k in AMENDED_KEYS | MUKARRAR_KEYS:
        if k not in arts:
            e.append("[1] expected article key %s missing" % k)

    n_bab = _count_babs(src.get("chapter_structure") or [])
    if n_bab != EXPECTED_BABS:
        e.append("[1c] expected %d أبواب, got %d" % (EXPECTED_BABS, n_bab))

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
        if not a["text"].strip() or re.search(r"[<>&]", a["text"]):
            e.append("[2] %s: empty text or html leftovers" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar (expected a باب/فصل path)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in MUKARRAR_KEYS):
            e.append("[2] %s: legal_status_ar/MUKARRAR_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar flag mismatch" % k)
        # residual lam-alef ligature-bug / lam-drop-bug signatures must not
        # survive into the final text
        if "الالئحة" in a["text"] or re.search(r"ا[أإآ]ل", a["text"]):
            e.append("[2f] %s: residual ligature-bug signature detected" % k)
        if "ًً" in a["text"]:
            e.append("[2g] %s: residual doubled-tanwin artifact detected" % k)
        if re.search(r"\(\s*\)\d", a["text"]):
            e.append("[2h] %s: residual bidi paren-before-digit artifact detected" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة"):
        e.append("[2] unexpected repealed articles present")

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
        if r.get("original_1423h_text") != a.get("original_1423h_text"):
            e.append("[4] %s: original_1423h_text not propagated" % r["article_key"])
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
        print("FAIL: %d error(s) in Customs Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Unified Customs Law (GCC) — 188 records (176 اصلية / 9 مضافة / 3 معدلة)")
    print("  - 17 أبواب")
    print("  - SINGLE-SOURCE TIER: ZATCA official consolidated PDF only (sole full-text primary")
    print("    source, shared with customs_regulation); laws.boe.gov.sa confirmed unreachable")
    print("    this pass (curl connection reset; WebFetch HTTP 503)")
    print("  - IN-FORCE Royal Decree M/41 (3/11/1423H); amended by M/14 (1443H, articles")
    print("    unconfirmed), M/81 (1444H, confirmed Art. 61), M/124 (1445H, confirmed Arts. 72/102)")
    print("  - lam-alef ligature + lam-drop PDF-extraction bug families fixed via general")
    print("    boundary regex + curated dictionary; 11 articles hand-reconstructed for line-order")
    print("    scrambling; Article 171/172 false-boundary self-reference corrected")
    print("  - no original_1423h_text populated for the 3 معدلة articles, a documented gap not a")
    print("    fabrication; 9 مكرر articles' individual amending-decree attribution not confirmed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
