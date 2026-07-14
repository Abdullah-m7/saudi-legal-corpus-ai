#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Professional Conduct Rules for Lawyers track (47 records).

Trust gate: every article MATCHES_PDF (>=0.90 vs the committed official MOJ PDF,
hash re-verified); no article required visual adjudication (mean 0.9551, min
0.900). Articles are numbered by ordinal position 1..42, 44..46 (rule 43 is a
documented source anomaly — genuinely absent from both the official portal
structure and the official PDF, confirmed on the rendered pages, not a fetch
artifact) plus two مكرر rules (9, 45 مكرر); and every article carries an
explained legal_status consistent with its is_repealed/is_amended/is_added
flags. The section-API status equals the PDF status for every article (no
dual-status divergence). CONSOLIDATED AMENDED through Minister of Justice
Decision 676 (19/4/1446H): 44 اصلية / 1 معدلة (rule 38) / 2 مضافة (rules 9, 45
مكرر), each carrying amendment history. Tatweel is banned EXCEPT the 'هـ'
digraph and space-bounded enumerator dashes."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "sulook", "regulation", "official_source",
                   "sulook_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "sulook", "regulation", "verified",
                       "sulook_regulation_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "sulook_arabic_legal_llm",
                   "sulook_regulation_legal_llm_001_047.json")
PDF = os.path.join(ROOT, "inputs", "sulook_official_pdfs",
                   "sulook_regulation_moj_official_ar.pdf")
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
N = 47
N_NUMBERED = 46
KEY_RE = r"sulook_art_(\d{3})(_mukarrar)?$"
SIM_FLOOR = 0.90
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 44, "معدلة": 1, "مضافة": 2}
EXPECTED_NUMBERED_NUMS = list(range(1, 43)) + list(range(44, 47))  # rule 43 genuinely absent
AMENDED_ARTICLES = {38}
EXPECTED_MUKARRAR = {"sulook_art_009_mukarrar", "sulook_art_045_mukarrar"}
VISUALLY_ADJUDICATED = set()
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
    if nums != EXPECTED_NUMBERED_NUMS:
        e.append("[1] numbered articles != expected 1..42,44..46 sequence (rule 43 documented absent): %s" % nums)
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
        print("FAIL: %d error(s) in Professional Conduct Rules for Lawyers track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Professional Conduct Rules for Lawyers — 47 records (44 اصلية / 1 معدلة / 2 مضافة)")
    print("  - trust gate: all 47/47 MATCHES_PDF outright (mean 0.9551, min 0.900); no visual adjudication needed")
    print("  - rule 43 documented absent from official source; amended rule 38 + added 2 مكرر (9, 45) carry full history")
    print("  - IN-FORCE Minister of Justice Decision 3453 (24/12/1442H), consolidated through Decision 676 (19/4/1446H); committed MOJ PDF hash verified; Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
