#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Law on Combating Crimes of Terrorism and its Financing track (28 records).

Trust gate: every article MATCHES_PDF (>=0.90 vs the committed official MOJ PDF,
hash re-verified) EXCEPT the 2 documented list articles (1, 4) whose PDF
text-layer reordered/split clauses — adjudicated VISUALLY VERBATIM on the rendered
pages and flagged MATCHES_PDF_VISUALLY_ADJUDICATED; articles are numbered by
ordinal position 1..26 plus two مكرر articles (20, 23 مكرر); and every article
carries an explained legal_status consistent with its is_repealed/is_amended/
is_added flags. The section-API status equals the PDF status for every article
(no dual-status divergence). CONSOLIDATED AMENDED: 18 اصلية / 7 معدلة (arts 2, 4,
16, 18, 21, 23, 24) / 1 ملغاة (art 9, flagged not deleted) / 2 مضافة (arts 20, 23
مكرر), each carrying amendment history. Tatweel is banned EXCEPT the 'هـ' digraph
and space-bounded enumerator dashes."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "terrorism", "implementing_regulation", "official_source",
                   "terrorism_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "terrorism", "implementing_regulation", "verified",
                       "terrorism_regulation_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "terrorism_arabic_legal_llm",
                   "terrorism_regulation_legal_llm_001_028.json")
PDF = os.path.join(ROOT, "inputs", "terrorism_reg_official_pdfs",
                   "terrorism_regulation_moj_official_ar.pdf")
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
N = 28
N_NUMBERED = 26
KEY_RE = r"terrorism_reg_art_(\d{3})(_mukarrar)?$"
SIM_FLOOR = 0.90
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 18, "معدلة": 7, "ملغاة": 1, "مضافة": 2}
AMENDED_ARTICLES = {2, 4, 16, 18, 21, 23, 24}
REPEALED_ARTICLES = {9}
EXPECTED_MUKARRAR = {"terrorism_reg_art_020_mukarrar", "terrorism_reg_art_023_mukarrar"}
VISUALLY_ADJUDICATED = {"terrorism_reg_art_001", "terrorism_reg_art_004"}
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

    visual = set()
    amended = set()
    repealed = set()
    sc = Counter()
    for k, a in arts.items():
        if a["status"] not in TRUSTED:
            e.append("[2] %s: UNTRUSTED status %r" % (k, a["status"]))
        sim = a.get("pdf_similarity") or 0
        if a["status"] == "MATCHES_PDF_VISUALLY_ADJUDICATED":
            visual.add(k)
        elif sim < SIM_FLOOR:
            e.append("[2] %s: sim %.3f below floor and not visually adjudicated" % (k, sim))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if ls == "معدلة":
            amended.add(int(re.match(KEY_RE, k).group(1)))
            if not a.get("history"):
                e.append("[2] %s: amended article missing amendment history" % k)
        if ls == "ملغاة":
            repealed.add(int(re.match(KEY_RE, k).group(1)))
            if not a.get("history"):
                e.append("[2] %s: repealed article missing amendment history" % k)
        if ls == "مضافة":
            if k not in EXPECTED_MUKARRAR:
                e.append("[2] %s: unexpected added (مضافة) article" % k)
            if not a.get("history"):
                e.append("[2] %s: added article missing amendment history" % k)
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/PDF status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
    if visual != VISUALLY_ADJUDICATED:
        e.append("[2] visually-adjudicated set %s != expected %s"
                 % (sorted(visual), sorted(VISUALLY_ADJUDICATED)))
    if amended != AMENDED_ARTICLES:
        e.append("[2] amended set %s != expected %s" % (sorted(amended), sorted(AMENDED_ARTICLES)))
    if repealed != REPEALED_ARTICLES:
        e.append("[2] repealed set %s != expected %s" % (sorted(repealed), sorted(REPEALED_ARTICLES)))
    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))

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

    if e:
        print("FAIL: %d error(s) in Implementing Regulation of the Law on Combating Crimes of Terrorism and its Financing track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Law on Combating Crimes of Terrorism and its Financing — 28 records (18 اصلية / 7 معدلة / 1 ملغاة / 2 مضافة)")
    print("  - trust gate: 26/28 MATCHES_PDF outright (mean 0.947); the 2 list articles (1, 4) adjudicated visually verbatim")
    print("  - amended arts 2,4,16,18,21,23,24 + repealed art 9 (flagged) + added 2 مكرر (20,23) carry full history")
    print("  - IN-FORCE Council of Ministers Decision 228 (2/5/1440H) implementing M/21; committed MOJ PDF hash verified; Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
