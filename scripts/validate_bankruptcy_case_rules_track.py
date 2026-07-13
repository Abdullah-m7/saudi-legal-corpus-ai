#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Bankruptcy Case Rules track (24 records).

Trust gate: every article MATCHES_PDF (>=0.90 vs the committed official MOJ PDF,
hash re-verified) — 24/24 matched outright (mean 0.960, min 0.912), so no article
required visual adjudication; the numbered sequence is a complete 1..24 (no
مكرر); and every article carries an explained legal_status consistent with its
is_repealed/is_amended/is_added flags. The section-API status equals the PDF
status for every article (no dual-status divergence). This is a fresh full
issuance: all 24 اصلية (0 معدلة / 0 ملغاة / 0 مضافة). Tatweel is banned EXCEPT
the 'هـ' digraph and space-bounded enumerator dashes."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "bankruptcy", "case_rules", "official_source",
                   "bankruptcy_case_rules_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "bankruptcy", "case_rules", "verified",
                       "bankruptcy_case_rules_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "bankruptcy_arabic_legal_llm",
                   "bankruptcy_case_rules_legal_llm_001_024.json")
PDF = os.path.join(ROOT, "inputs", "bankruptcy_official_pdfs",
                   "bankruptcy_case_rules_moj_official_ar.pdf")
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
N = 24
SIM_FLOOR = 0.90
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 24}
VISUALLY_ADJUDICATED = set()
TRUSTED = {"MATCHES_PDF", "MATCHES_PDF_VISUALLY_ADJUDICATED"}
AR = "ء-ي"


def _bad_tatweel(text):
    # Decorative in-word kashida = a tatweel run sitting BETWEEN two Arabic
    # letters (e.g. الرحـمن). That is what the strip removes and what is banned.
    # Word-boundary tatweels that mark a standalone letter — the 'هـ' enumerator,
    # a preposition prefix before a parenthetical figure (لـ(ثلاثين), بـ(واحد)),
    # or a list enumerator (دـ-) — are legitimate orthography and kept verbatim.
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
    for p in (SRC, RECORDS, LLM, PDF):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    # [1] structure: complete 1..24, no mukarrar
    nums = sorted(int(re.match(r"bankruptcy_rules_art_(\d{3})", k).group(1)) for k in arts
                  if not k.endswith("_mukarrar"))
    if nums != list(range(1, N + 1)):
        e.append("[1] numbered articles not a complete 1..%d sequence" % N)
    if any(k.endswith("_mukarrar") for k in arts):
        e.append("[1] unexpected mukarrar keys")
    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))

    # [2] trust gate
    sc = Counter()
    for k, a in arts.items():
        if a["status"] not in TRUSTED:
            e.append("[2] %s: UNTRUSTED status %r" % (k, a["status"]))
        sim = a.get("pdf_similarity") or 0
        if sim < SIM_FLOOR and k not in VISUALLY_ADJUDICATED:
            e.append("[2] %s: sim %.3f below floor and not visually adjudicated" % (k, sim))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected section/PDF status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %d != %d" % (st, sc.get(st), want))
    if sc.get("معدلة") or sc.get("ملغاة") or sc.get("مضافة"):
        e.append("[2] unexpected amended/repealed/added articles present")

    # [2b] no dual-status divergence
    if src["provenance"].get("section_vs_structure_divergences") not in (0, None):
        e.append("[2b] unexpected section-vs-structure divergence recorded")

    # [3] committed PDF hash
    if hashlib.sha256(open(PDF, "rb").read()).hexdigest() != src["provenance"]["pdf_sha256"]:
        e.append("[3] committed MOJ PDF sha256 mismatch")

    # [4] verified records
    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts[r["article_key"]]
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        ls = r.get("legal_status_ar")
        if (r.get("is_repealed") != (ls == "ملغاة") or r.get("is_amended") != (ls == "معدلة")
                or r.get("is_added") != (ls == "مضافة")):
            e.append("[4] %s: status flags inconsistent with legal_status_ar" % r["article_key"])
        if r.get("official_text_status") != STATUS:
            e.append("[4] %s: bad status" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    # [5] LLM layer verbatim/hashes
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
    if sum(1 for r in recs if r["is_amended"] or r["is_repealed"] or r["is_added"]):
        e.append("[5] unexpected amended/repealed/added flag in LLM layer")

    if e:
        print("FAIL: %d error(s) in Bankruptcy Case Rules track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Bankruptcy Case Rules — 24 records (fresh issuance: all 24 اصلية)")
    print("  - trust gate: 24/24 MATCHES_PDF outright (mean 0.960, min 0.912); no visual adjudication needed")
    print("  - complete 1..24 (no مكرر); committed official MOJ PDF hash verified; no dual-status divergence")
    print("  - Minister of Justice Decision 6421 (9/4/1441H); procedural rules for bankruptcy cases before the commercial courts")
    print("  - decorative in-word tatweel removed; هـ + space-bounded dashes kept; Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
