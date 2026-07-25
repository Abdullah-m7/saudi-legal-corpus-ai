#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation ("Executive List")
of the Anti-Narcotics and Psychotropic Substances Control Law track (40
records, all اصلية, flat sequence of مواد, no باب/فصل structure and no
topical section headers -- a genuine structural difference from the
base law track, see below).

DISTINCT, LOWER VERIFICATION TIER than the base law's track -- see the
generator's module docstring and sources/anti_narcotics_regulation/law/
official_source/anti_narcotics_regulation_official_source.json's
verification_methodology_note for the full disclosure. The official BOE
portal, the MOI PDF, and Wayback Machine content were all attempted and
all failed; this track rests on a SINGLE full-text primary source
(nezams.com), with only the enacting resolution's preamble (not the
article bodies) independently cross-matched via qistas.com, plus
topical (non-verbatim) corroboration for 3 of 40 articles via
almehleky.sa. This validator checks internal consistency and that
every article carries the distinct-tier status tag; it CANNOT re-run
the underlying web fetches against the primary portal itself, and it
CANNOT upgrade this track's verification tier."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "anti_narcotics_regulation", "law",
                   "official_source",
                   "anti_narcotics_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "anti_narcotics_regulation", "law",
                       "verified", "anti_narcotics_regulation_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "anti_narcotics_regulation_arabic_legal_llm",
                   "anti_narcotics_regulation_legal_llm_001_040.json")
N = 40
KEY_RE = r"anti_narcotics_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 40}
STATUS = "NEZAMS_HTML_SINGLE_FULLTEXT_X_QISTAS_PREAMBLE_PARTIAL_MATCH"
FLAGGED_DISCREPANCY_KEYS = {
    "anti_narcotics_regulation_single_source_tier",
    "anti_narcotics_regulation_boe_unreachable",
    "anti_narcotics_regulation_moi_pdf_unreachable",
    "anti_narcotics_regulation_wayback_verification_gap",
    "anti_narcotics_regulation_zarah_pdf_excluded",
    "anti_narcotics_regulation_no_topical_headers",
    "anti_narcotics_regulation_art_034_site_nav_stripped",
    "anti_narcotics_regulation_table_linearization",
    "anti_narcotics_regulation_dash_style_uncertain",
    "anti_narcotics_regulation_com_res_201_bundled_reward_clause",
}
AR = "ء-ي"
SITE_NAV_JUNK = ("انقر هنا", "اضغط هنا", "اقرأ أيضا", "تابعنا على", "شارك هذا المقال",
                  "لاستعراض التشريع كاملاً")


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
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)

    # This track has NO chapter_structure / no topical headers -- unlike the base
    # law, that must be honestly absent here, not invented.
    if src.get("chapter_structure"):
        e.append("[1c] unexpected chapter_structure present -- this Regulation has "
                 "no topical headers per its primary source; do not invent one")

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
        if not a["text"].strip() or re.search(r"<|>|&(?!\w)", a["text"]):
            e.append("[2] %s: empty text or leftover HTML markup" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        for junk in SITE_NAV_JUNK:
            if junk in a["text"]:
                e.append("[2] %s: site-navigation text leaked into article body: %r"
                         % (k, junk))
        if a.get("history"):
            e.append("[2] %s: unexpected non-empty amendment history (no amendments found)" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة") or sc.get("مضافة") or sc.get("معدلة"):
        e.append("[2] unexpected repealed/added/amended articles present")

    # Articles 2 and 34 must retain their linearized [جدول]...[/جدول] table blocks --
    # this is where the Regulation's substance/dosage tables live.
    for tk in ("anti_narcotics_regulation_art_002", "anti_narcotics_regulation_art_034"):
        t = arts.get(tk, {}).get("text", "")
        if "[جدول]" not in t or "[/جدول]" not in t:
            e.append("[2h] %s: expected linearized [جدول]...[/جدول] table block" % tk)

    # Article 34's table must retain its bilingual Arabic/English substance names
    # (published as such by the government; not translations added by this track).
    art34_text = arts.get("anti_narcotics_regulation_art_034", {}).get("text", "")
    if "Fentanyl" not in art34_text or "الخشخاش" not in art34_text:
        e.append("[2i] anti_narcotics_regulation_art_034: expected bilingual substance "
                 "table content (e.g. 'الخشخاش' / 'Fentanyl') preserved verbatim")

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
        print("FAIL: %d error(s) in Anti-Narcotics Regulation track:" % len(e))
        for x in e[:20]:
            print("  - %s" % x)
        return 1
    print("PASS: Anti-Narcotics Regulation ('Executive List') — 40 records (all اصلية)")
    print("  - DISTINCT, LOWER TIER: single full-text primary source (nezams.com) x")
    print("    qistas.com preamble-only partial match; BOE/MOI/Wayback unreachable")
    print("    (disclosed honestly, not overstated to match the base law's tier)")
    print("  - numbered 1..40, flat sequence, no باب/فصل, no topical section headers")
    print("  - IN-FORCE CoM Resolution 201 (10/6/1431H); no amendments found to article text")
    print("  - Articles 2 and 34 retain linearized substance/dosage tables verbatim")
    return 0


if __name__ == "__main__":
    sys.exit(main())
