#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the customs_regulation track (36 records,
consolidated amended regulation: 34 اصلية / 2 مضافة; 7 أبواب).

SINGLE-SOURCE TIER -- see the generator's module docstring and
sources/customs/regulation/official_source/
customs_regulation_official_source.json's verification_methodology_note
for the full caveat: ZATCA's own official PDF is the SOLE full-text
primary source this pass (shared with customs_law), with
laws.boe.gov.sa confirmed unreachable. IMPORTANT: this validator does
NOT require any article to carry legal_status_ar='معدلة' -- none of the
6 amending resolutions' specific affected articles could be confirmed
from any source checked this pass (a documented gap, not a fabrication
that nothing changed)."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "customs", "regulation", "official_source",
                   "customs_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "customs", "regulation", "verified",
                       "customs_regulation_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "customs_regulation_arabic_legal_llm",
                   "customs_regulation_legal_llm_001_036.json")
N = 36
KEY_RE = r"customs_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 34, "مضافة": 2}
STATUS = "ZATCA_PDF_PRIMARY_SINGLE_SOURCE_BOE_UNREACHABLE"
EXPECTED_BABS = 7
MUKARRAR_KEYS = {"customs_regulation_art_002_mukarrar", "customs_regulation_art_025_mukarrar"}
FLAGGED_DISCREPANCY_KEYS = {
    "customs_regulation_amendments_articles_unconfirmed",
    "customs_regulation_boe_unreachable",
    "customs_regulation_shared_ligature_bug_methodology",
    "customs_regulation_article1_valuation_length_residual_risk",
    "customs_regulation_bab_chapeau_paragraphs_relocated",
    "customs_regulation_25mukarrar_header_missing_al_corrected",
    "customs_regulation_article13_clause1_not_independently_recovered",
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
    for k in MUKARRAR_KEYS:
        if k not in arts:
            e.append("[1] expected مكرر article key %s missing" % k)

    n_bab = len(src.get("chapter_structure") or [])
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
            e.append("[2] %s: missing section_ar (expected a باب path)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if (ls == "مضافة") != (k in MUKARRAR_KEYS):
            e.append("[2] %s: legal_status_ar/MUKARRAR_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar flag mismatch" % k)
        if "الالئحة" in a["text"] or re.search(r"ا[أإآ]ل", a["text"]):
            e.append("[2f] %s: residual ligature-bug signature detected" % k)
        if "ًً" in a["text"]:
            e.append("[2g] %s: residual doubled-tanwin artifact detected" % k)
        if re.search(r"\(\s*\)\d", a["text"]):
            e.append("[2h] %s: residual bidi paren-before-digit artifact detected" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة") or sc.get("معدلة"):
        e.append("[2] unexpected repealed/amended articles present (none confirmed this pass)")

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

    # Article 1's internal ordinal structure (أولاً..ثامناً) must be
    # preserved whole, not split into separate numbered articles.
    art1 = arts.get("customs_regulation_art_001", {})
    for marker in ("أولاً", "ثامناً"):
        if marker not in art1.get("text", ""):
            e.append("[2i] customs_regulation_art_001: missing expected ordinal marker %r "
                     "(internal valuation-methodology structure)" % marker)

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts[r["article_key"]]
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
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
        print("FAIL: %d error(s) in Customs Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the GCC Unified Customs Law — 36 records (34 اصلية / 2 مضافة)")
    print("  - 7 أبواب")
    print("  - SINGLE-SOURCE TIER: ZATCA official consolidated PDF only (sole full-text primary")
    print("    source, shared with customs_law); laws.boe.gov.sa confirmed unreachable this pass")
    print("    (curl connection reset; WebFetch HTTP 503)")
    print("  - IN-FORCE Ministerial/Committee Resolution 2748 (25/11/1423H); amended 6 times")
    print("    (2997, 3766, 939, 986, 955, 1374) -- no specific article individually attributable")
    print("    to any one resolution from the available source, a documented gap")
    print("  - Article 1's internal ordinal-clause structure (أولاً..ثامناً + الملحق التفسيري)")
    print("    preserved whole; 3 Book-level chapeau paragraphs (Books 3/6/7) relocated to their")
    print("    Book's first article (14/26/29) rather than discarded as section-title noise")
    return 0


if __name__ == "__main__":
    sys.exit(main())
