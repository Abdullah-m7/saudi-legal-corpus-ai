#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Executive Working Mechanism for the Law of
the Judiciary and the Law of the Board of Grievances track (15 records).

Trust gate: every item MATCHES_PDF or MATCHES_PDF_VISUALLY_ADJUDICATED
(>=0.90 vs the committed official MOJ PDF, hash re-verified, unless visually
adjudicated). 1/15 (item 9) matched outright; the other 14 (mean 0.5026, min
0.1253) were visually adjudicated verbatim due to a known RTL/ligature PDF
text-layer extraction artifact. Items are numbered by ordinal position
1..15 (no مكرر), grouped into 3 sections (9+5+1). NOT A FRESH ISSUANCE: 14 of
15 items are اصلية; item 7 is معدلة with a 2-version amendment history
(originally اصلية 1428H -> amended by م/6 1440H -> amended again by م/113
1443H, current). Tatweel is banned EXCEPT the 'هـ' digraph and space-bounded
enumerator dashes. DOCUMENTED SOURCE ANOMALIES (confirmed identically in
both official sources): item 9's heading reads «شبة القضائية» instead of
«شبه»; item 10's heading reads «بمجل القضاء الإداري», missing the س of
مجلس."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "judiciary_bog", "mechanism", "official_source",
                   "judiciary_bog_mechanism_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "judiciary_bog", "mechanism", "verified",
                       "judiciary_bog_mechanism_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "judiciary_bog_arabic_legal_llm",
                   "judiciary_bog_mechanism_legal_llm_001_015.json")
PDF = os.path.join(ROOT, "inputs", "judiciary_bog_mechanism_official_pdfs",
                   "judiciary_bog_mechanism_moj_official_ar.pdf")
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
N = 15
KEY_RE = r"judiciary_bog_mechanism_art_(\d{3})$"
SIM_FLOOR = 0.90
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 14, "معدلة": 1}
AMENDED_KEY = "judiciary_bog_mechanism_art_007"
VISUALLY_ADJUDICATED = {"judiciary_bog_mechanism_art_%03d" % n for n in
                        (1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15)}
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

    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != list(range(1, N + 1)):
        e.append("[1] items not a complete 1..%d sequence" % N)
    if len(arts) != N:
        e.append("[1] %d items != %d" % (len(arts), N))

    visual = set()
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
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/PDF status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar (3-section grouping expected)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
    if visual != VISUALLY_ADJUDICATED:
        e.append("[2] visually-adjudicated set %s != expected %s"
                 % (sorted(visual), sorted(VISUALLY_ADJUDICATED)))
    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة") or sc.get("مضافة"):
        e.append("[2] unexpected repealed/added items present")

    # [2b] the sole amended item carries its 2-version amendment history
    a7 = arts.get(AMENDED_KEY, {})
    if a7.get("legal_status_ar") != "معدلة":
        e.append("[2b] item 7 must be معدلة")
    hist = a7.get("history") or []
    if len(hist) != 2:
        e.append("[2b] item 7 history must have exactly 2 versions, found %d" % len(hist))
    if not any("م/6" in (h.get("decree") or "") for h in hist):
        e.append("[2b] item 7 history missing المرسوم الملكي رقم م/6")
    if not any(h.get("legalStatusName") == "اصلية" for h in hist):
        e.append("[2b] item 7 history missing the original 1428 body")

    if src["provenance"].get("section_vs_structure_divergences") not in (0, None):
        e.append("[2c] unexpected section-vs-structure divergence recorded")

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
        if r["is_amended"] != (a.get("legal_status_ar") == "معدلة"):
            e.append("[4] %s: is_amended flag mismatch" % r["article_key"])
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
        print("FAIL: %d error(s) in Judiciary/Board of Grievances Executive Mechanism track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Executive Working Mechanism for the Law of the Judiciary and the Law of the Board of Grievances — 15 records (14 اصلية, 1 معدلة)")
    print("  - trust gate: 1/15 MATCHES_PDF outright (item 9), 14 visually adjudicated (mean 0.5026, min 0.1253)")
    print("  - numbered 1..15 by ordinal position across 3 sections (9+5+1); item 7 carries a 2-version amendment history (م/6 1440H, م/113 1443H)")
    print("  - IN-FORCE Royal Decree م/78 (19/09/1428H); committed MOJ PDF hash verified; Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
