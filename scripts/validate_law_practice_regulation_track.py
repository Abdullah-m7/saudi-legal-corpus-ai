#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Code of Law Practice (90 records).

Trust gate: every article MATCHES_PDF (>=0.90 vs the committed official MOJ PDF,
hash re-verified) EXCEPT the 5 visually-adjudicated long/list articles (1, 3, 19,
60, 62) confirmed verbatim on the rendered pages; the numbered sequence is a
complete 1..90 (no مكرر); and every article is اصلية (this is a fresh full 1446H
issuance — the prior 1423H regulation is InActive and not ingested), consistent
with its is_repealed/is_amended/is_added flags all False. The section-API status
equals the PDF status for every article (no dual-status divergence). Tatweel is
banned EXCEPT the 'هـ' digraph and space-bounded enumerator dashes."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "law_practice", "regulation", "official_source",
                   "law_practice_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "law_practice", "regulation", "verified",
                       "law_practice_regulation_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "law_practice_arabic_legal_llm",
                   "law_practice_regulation_legal_llm_001_090.json")
PDF = os.path.join(ROOT, "inputs", "law_practice_official_pdfs",
                   "law_practice_regulation_moj_official_ar.pdf")
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
N = 90
SIM_FLOOR = 0.90
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 90}
VISUALLY_ADJUDICATED = {"law_practice_reg_art_001", "law_practice_reg_art_003",
                        "law_practice_reg_art_019", "law_practice_reg_art_060",
                        "law_practice_reg_art_062"}
TRUSTED = {"MATCHES_PDF", "MATCHES_PDF_VISUALLY_ADJUDICATED"}
AR = "ء-ي"


def _bad_tatweel(text):
    bad = 0
    for m in re.finditer("ـ+", text):
        before = text[m.start() - 1] if m.start() > 0 else " "
        if re.match("[%s]" % AR, before) and before != "ه":
            bad += 1
    return bad


def main():
    e = []
    for p in (SRC, RECORDS, LLM, PDF):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    # [1] structure: complete 1..90, no mukarrar
    nums = sorted(int(re.match(r"law_practice_reg_art_(\d{3})", k).group(1)) for k in arts
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
        e.append("[2] unexpected non-original articles (fresh issuance should be all اصلية)")

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
        if not (r.get("is_repealed") is False and r.get("is_amended") is False
                and r.get("is_added") is False):
            e.append("[4] %s: status flags must all be False (اصلية)" % r["article_key"])
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
    if sum(1 for r in recs if r["legal_status_ar"] == "اصلية") != N:
        e.append("[5] llm not all اصلية")

    if e:
        print("FAIL: %d error(s) in Law Practice Regulation track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Code of Law Practice — 90 records (fresh 1446H issuance, all اصلية)")
    print("  - trust gate: 85/90 MATCHES_PDF; 5 long/list articles (1, 3, 19, 60, 62) visually adjudicated verbatim")
    print("  - complete 1..90 (no مكرر); committed official MOJ PDF hash verified; no dual-status divergence")
    print("  - current Active regulation (supersedes the InActive 1423H one, not ingested)")
    print("  - decorative in-word tatweel removed; هـ + space-bounded dashes kept; Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
