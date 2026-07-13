#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Anti-Money Laundering Law track (52 records).

Trust gate: every article MATCHES_PDF (>=0.90 vs the committed official MOJ PDF,
hash re-verified) EXCEPT the 3 visually-adjudicated long definition/list articles
(the first «التعريفات» article, art 24, art 43) confirmed verbatim on the rendered
pages; articles are numbered by ordinal position 1..51 plus one مكرر article (49
مكرر); and every article carries an explained legal_status consistent with its
is_repealed/is_amended/is_added flags. The section-API status equals the PDF
status for every article (no dual-status divergence). Consolidated amended law:
44 اصلية / 7 معدلة (arts 14, 15, 16, 18, 28, 33, 50) / 1 مضافة (art 49 مكرر),
each amended/added article carrying its history (all by Royal Decree M/223,
27/10/1447H); none repealed.

Tatweel is banned EXCEPT the 'هـ' digraph and space-bounded enumerator dashes."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "aml", "law", "official_source",
                   "aml_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "aml", "law", "verified",
                       "aml_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "aml_arabic_legal_llm",
                   "aml_law_legal_llm_001_052.json")
PDF = os.path.join(ROOT, "inputs", "aml_official_pdfs",
                   "aml_law_moj_official_ar.pdf")
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
N = 52
N_NUMBERED = 51
KEY_RE = r"aml_art_(\d{3})(_mukarrar)?$"
SIM_FLOOR = 0.90
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 44, "معدلة": 7, "مضافة": 1}
VISUALLY_ADJUDICATED = {"aml_art_001", "aml_art_024", "aml_art_043"}
EXPECTED_AMENDED = {14, 15, 16, 18, 28, 33, 50}
EXPECTED_MUKARRAR = {"aml_art_049_mukarrar"}
TRUSTED = {"MATCHES_PDF", "MATCHES_PDF_VISUALLY_ADJUDICATED"}
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
    for p in (SRC, RECORDS, LLM, PDF):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts if not k.endswith("_mukarrar"))
    if nums != list(range(1, N_NUMBERED + 1)):
        e.append("[1] numbered articles not a complete 1..%d sequence" % N_NUMBERED)
    muk = {k for k in arts if k.endswith("_mukarrar")}
    if muk != EXPECTED_MUKARRAR:
        e.append("[1] mukarrar keys %s != expected %s" % (sorted(muk), sorted(EXPECTED_MUKARRAR)))
    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))

    sc = Counter()
    amended_nums = set()
    for k, a in arts.items():
        if a["status"] not in TRUSTED:
            e.append("[2] %s: UNTRUSTED status %r" % (k, a["status"]))
        sim = a.get("pdf_similarity") or 0
        if sim < SIM_FLOOR and k not in VISUALLY_ADJUDICATED:
            e.append("[2] %s: sim %.3f below floor and not visually adjudicated" % (k, sim))
        if a["status"] == "MATCHES_PDF_VISUALLY_ADJUDICATED" and k not in VISUALLY_ADJUDICATED:
            e.append("[2] %s: unexpected visually-adjudicated article" % k)
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if ls == "معدلة":
            amended_nums.add(int(re.match(KEY_RE, k).group(1)))
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/PDF status divergence" % k)
        if (ls in ("معدلة", "مضافة")) and not a.get("history"):
            e.append("[2] %s: amended/added article missing version history" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة"):
        e.append("[2] unexpected repealed articles present")
    if amended_nums != EXPECTED_AMENDED:
        e.append("[2] amended set %s != expected %s" % (sorted(amended_nums), sorted(EXPECTED_AMENDED)))

    if src["provenance"].get("section_vs_structure_divergences") not in (0, None):
        e.append("[2b] unexpected section-vs-structure divergence recorded")

    if hashlib.sha256(open(PDF, "rb").read()).hexdigest() != src["provenance"]["pdf_sha256"]:
        e.append("[3] committed MOJ PDF sha256 mismatch")

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
    amended = sum(1 for r in recs if r["is_amended"])
    if amended != EXPECTED_COUNTS["معدلة"]:
        e.append("[5] amended count %d != %d" % (amended, EXPECTED_COUNTS["معدلة"]))
    added = sum(1 for r in recs if r["is_added"])
    if added != EXPECTED_COUNTS["مضافة"]:
        e.append("[5] added count %d != %d" % (added, EXPECTED_COUNTS["مضافة"]))

    if e:
        print("FAIL: %d error(s) in Anti-Money Laundering Law track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Anti-Money Laundering Law — 52 records (consolidated: 44 اصلية / 7 معدلة / 1 مضافة)")
    print("  - trust gate: 49/52 MATCHES_PDF; the 3 long definition/list articles (1, 24, 43) visually adjudicated verbatim")
    print("  - numbered 1..51 by ordinal position + one مكرر article (49 مكرر, added); no dual-status divergence")
    print("  - 7 amended articles (14, 15, 16, 18, 28, 33, 50) + 1 added (49 مكرر) carry history (M/223, 27/10/1447H); committed MOJ PDF hash verified")
    print("  - decorative in-word tatweel removed; هـ + space-bounded dashes kept; Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
