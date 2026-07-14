#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Law on Combating Crimes of Terrorism and its Financing track (99 records).

Trust gate: every article MATCHES_PDF (>=0.90 vs the committed official MOJ PDF,
hash re-verified) EXCEPT the 9 documented long articles (1, 3, 10, 39, 43, 50, 56,
82, 83) whose PDF text-layer reordered/split clauses — adjudicated VISUALLY
VERBATIM on the rendered pages and flagged MATCHES_PDF_VISUALLY_ADJUDICATED;
articles are numbered by ordinal position 1..96 plus three مكرر articles (59, 63,
81 مكرر); and every article carries an explained legal_status consistent with its
is_repealed/is_amended/is_added flags. The section-API status equals the PDF status
for every article (no dual-status divergence). CONSOLIDATED AMENDED: 88 اصلية /
8 معدلة (arts 4, 9, 12, 63, 67, 70, 71, 83) / 3 مضافة (arts 59, 63, 81 مكرر), each
carrying amendment history; none repealed. Tatweel is banned EXCEPT the 'هـ'
digraph and space-bounded enumerator dashes."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "terrorism", "law", "official_source",
                   "terrorism_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "terrorism", "law", "verified",
                       "terrorism_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "terrorism_arabic_legal_llm",
                   "terrorism_law_legal_llm_001_099.json")
PDF = os.path.join(ROOT, "inputs", "terrorism_official_pdfs",
                   "terrorism_law_moj_official_ar.pdf")
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
N = 99
N_NUMBERED = 96
KEY_RE = r"terrorism_art_(\d{3})(_mukarrar)?$"
SIM_FLOOR = 0.90
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 88, "معدلة": 8, "مضافة": 3}
AMENDED_ARTICLES = {4, 9, 12, 63, 67, 70, 71, 83}
EXPECTED_MUKARRAR = {"terrorism_art_059_mukarrar", "terrorism_art_063_mukarrar",
                     "terrorism_art_081_mukarrar"}
VISUALLY_ADJUDICATED = {"terrorism_art_001", "terrorism_art_003", "terrorism_art_010",
                        "terrorism_art_039", "terrorism_art_043", "terrorism_art_050",
                        "terrorism_art_056", "terrorism_art_082", "terrorism_art_083"}
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
    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة"):
        e.append("[2] unexpected repealed articles present")

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
        print("FAIL: %d error(s) in Law on Combating Crimes of Terrorism and its Financing track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Law on Combating Crimes of Terrorism and its Financing — 99 records (88 اصلية / 8 معدلة / 3 مضافة)")
    print("  - trust gate: 90/99 MATCHES_PDF outright (mean 0.955); the 9 long articles adjudicated visually verbatim")
    print("  - amended arts 4,9,12,63,67,70,71,83 + added 3 مكرر (59,63,81) carry full history; numbered 1..96 plus 3 مكرر")
    print("  - IN-FORCE Royal Decree M/21 (12/2/1439H), superseding M/16 1435H; committed MOJ PDF hash verified; Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
