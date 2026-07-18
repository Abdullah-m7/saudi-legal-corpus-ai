#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Cooperative Health Insurance Law track (19
records, consolidated amended law: 17 اصلية / 2 معدلة; flat structure, no
أبواب or فصول).

VERIFICATION TIER -- see the generator's module docstring and
sources/cooperative_health_insurance/law/official_source/
cooperative_health_insurance_law_official_source.json's
verification_methodology_note for the full caveat: laws.boe.gov.sa's LIVE
portal was unreachable this pass, but a Wayback Machine archive of the
exact law page WAS reachable and is treated as the primary source, cross-
verified against nezams.com. IMPORTANT: this validator does NOT require a
second independent source for Article 4's 1440H amendment text specifically
-- that gap (BOE cites the amending resolution but does not reproduce its
text; nezams.com is the sole source, with disclosed normalization of
evident transcription artifacts) is documented in
known_unresolved_discrepancies rather than fabricated or silently
resolved."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "cooperative_health_insurance", "law", "official_source",
                   "cooperative_health_insurance_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "cooperative_health_insurance", "law", "verified",
                       "cooperative_health_insurance_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "cooperative_health_insurance_arabic_legal_llm",
                   "cooperative_health_insurance_law_legal_llm_001_019.json")
N = 19
KEY_RE = r"cooperative_health_insurance_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 17, "معدلة": 2}
STATUS = "BOE_WAYBACK_ARCHIVE_X_NEZAMS_CROSS_VERIFIED_LIVE_BOE_503"
AMENDED_KEYS = {"cooperative_health_insurance_art_%03d" % n for n in (4, 14)}
FLAGGED_DISCREPANCY_KEYS = {
    "cooperative_health_insurance_boe_metadata_date_panel_inconsistency",
    "cooperative_health_insurance_art_004_1440h_amendment_single_source",
    "cooperative_health_insurance_art_004_nezams_transcription_artifacts_normalized",
    "cooperative_health_insurance_implementing_regulation_not_ingested_this_pass",
    "cooperative_health_insurance_cchi_circulars_and_umrah_hajj_coverage_out_of_scope",
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
    for k in AMENDED_KEYS:
        if k not in arts:
            e.append("[1] expected article key %s missing" % k)

    if src.get("chapter_structure") != []:
        e.append("[1c] expected empty chapter_structure for this flat-structure law")

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
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")):
            e.append("[2] %s: unexpected is_mukarrar=True (no مكرر articles in this law)" % k)
        original = (a.get("original_1420h_text") or a.get("original_1425h_text")
                    or a.get("original_1440h_text"))
        if k in AMENDED_KEYS and not original:
            e.append("[2] %s: amended article missing an original_*_text field" % k)
        if original and original == a["text"]:
            e.append("[2] %s: original text identical to current text (no-op amendment?)" % k)
        # residual bidi paren-before-digit / doubled-tanwin artifacts
        if re.search(r"\(\s*\)\d", a["text"]):
            e.append("[2h] %s: residual bidi paren-before-digit artifact detected" % k)
        if "ًً" in a["text"]:
            e.append("[2g] %s: residual doubled-tanwin artifact detected" % k)
        # Article 4's known-normalized artifacts must NOT survive into final text
        if k == "cooperative_health_insurance_art_004":
            for bad_frag in ("»", "ثمرة واحدة", "الخاصء", "بأمر مسن", "التامين"):
                if bad_frag in a["text"]:
                    e.append("[2i] %s: un-normalized transcription artifact %r present"
                              % (k, bad_frag))

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة"):
        e.append("[2] unexpected repealed articles present")
    if sc.get("مضافة"):
        e.append("[2] unexpected added (مضافة) articles present")

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
        expected_original = (a.get("original_1420h_text") or a.get("original_1425h_text")
                              or a.get("original_1440h_text"))
        if r.get("original_text") != expected_original:
            e.append("[4] %s: original_text not propagated" % r["article_key"])
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
        print("FAIL: %d error(s) in Cooperative Health Insurance Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Cooperative Health Insurance Law — 19 records (17 اصلية / 2 معدلة)")
    print("  - flat structure, no أبواب/فصول (confirmed absent from both BOE and nezams.com)")
    print("  - VERIFICATION TIER: BOE-via-Wayback-Machine archive (primary, live BOE")
    print("    unreachable) x nezams.com HTML transcription (zero substantive discrepancies")
    print("    across 17 unamended articles + 1420H/1425H states of 2 amended articles)")
    print("  - IN-FORCE Royal Decree M/10 (1/5/1420H); Article 4 amended twice (Council of")
    print("    Ministers Resolution 246, 1425H, then 472, 1440H); Article 14 amended once")
    print("    (Resolution 246, 1425H)")
    print("  - Article 4's 1440H amendment text is single-sourced (nezams.com; BOE cites the")
    print("    resolution but not its text) with disclosed normalization of evident")
    print("    transcription artifacts; companion Implementing Regulation and CCHI/CHI")
    print("    circulars (incl. Umrah/Hajj coverage expansions) identified but NOT ingested")
    print("    this pass -- candidates for follow-up, not fabricated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
