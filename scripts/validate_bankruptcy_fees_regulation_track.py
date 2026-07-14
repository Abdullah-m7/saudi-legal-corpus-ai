#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Rules for Determining the Fees of Experts and
Trustees under the Bankruptcy Law track (20 records).

Trust gate: every record MATCHES_PDF or MATCHES_PDF_VISUALLY_ADJUDICATED
(>=0.90 vs the committed official MOJ PDF, hash re-verified, unless visually
adjudicated). Only 6/20 matched outright (arts 4, 7, 10, 11, 12, 17; mean
0.8217, min 0.5822) because this PDF's text layer mixes inconsistent RTL
extraction conventions and the OCR channel misreads embedded numerals; the
other 14 (arts 1,2,3,5,6,8,9,13,14,15,16 + all 3 fee-schedule tables) were
visually adjudicated verbatim. Records are numbered by ordinal position
1..20 (no مكرر): 17 numbered "المادة"-labeled articles + 3 appendix
fee-schedule tables (18-20, is_fee_schedule=True). The section-API status
equals the PDF status for every record (no dual-status divergence). FRESH
FULL ISSUANCE: all 20 اصلية; none amended, repealed or added. Tatweel is
banned EXCEPT the 'هـ' digraph and space-bounded enumerator dashes.
DOCUMENTED SOURCE ANOMALIES: (1) the three tables' number_label_ar are
formatted inconsistently ("الجدول رقم(١)" / "الجدول رقم (٢)" / "جدول رقم
(٣)"); (2) inside art 19, a sub-table header cell reads "الأصول" instead of
"الديون" — both confirmed in both official sources, preserved verbatim."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "bankruptcy_fees", "regulation", "official_source",
                   "bankruptcy_fees_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "bankruptcy_fees", "regulation", "verified",
                       "bankruptcy_fees_regulation_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "bankruptcy_fees_arabic_legal_llm",
                   "bankruptcy_fees_regulation_legal_llm_001_020.json")
PDF = os.path.join(ROOT, "inputs", "bankruptcy_fees_official_pdfs",
                   "bankruptcy_fees_regulation_moj_official_ar.pdf")
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
N = 20
N_ART = 17
KEY_RE = r"bankruptcy_fees_art_(\d{3})$"
SIM_FLOOR = 0.90
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 20}
FEE_SCHEDULE_KEYS = {"bankruptcy_fees_art_018", "bankruptcy_fees_art_019", "bankruptcy_fees_art_020"}
VISUALLY_ADJUDICATED = {"bankruptcy_fees_art_%03d" % n for n in
                        (1, 2, 3, 5, 6, 8, 9, 13, 14, 15, 16, 18, 19, 20)}
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
        e.append("[1] records not a complete 1..%d sequence" % N)
    if len(arts) != N:
        e.append("[1] %d records != %d" % (len(arts), N))

    visual = set()
    sc = Counter()
    fee_keys = set()
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
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if a.get("is_fee_schedule"):
            fee_keys.add(k)
    if visual != VISUALLY_ADJUDICATED:
        e.append("[2] visually-adjudicated set %s != expected %s"
                 % (sorted(visual), sorted(VISUALLY_ADJUDICATED)))
    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("معدلة") or sc.get("ملغاة") or sc.get("مضافة"):
        e.append("[2] unexpected amended/repealed/added records present")
    if fee_keys != FEE_SCHEDULE_KEYS:
        e.append("[2] fee-schedule key set %s != expected %s" % (sorted(fee_keys), sorted(FEE_SCHEDULE_KEYS)))

    # [2c] numbered articles 1..17 carry the المادة prefix; fee-schedule tables (18-20) don't
    for n in range(1, N_ART + 1):
        k = "bankruptcy_fees_art_%03d" % n
        if not arts[k]["number_label_ar"].startswith("المادة"):
            e.append("[2c] %s: expected المادة prefix on numbered article" % k)
    for k in FEE_SCHEDULE_KEYS:
        if arts[k]["number_label_ar"].startswith("المادة"):
            e.append("[2c] %s: fee-schedule table unexpectedly carries المادة prefix" % k)

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
        if bool(r.get("is_fee_schedule")) != (r["article_key"] in FEE_SCHEDULE_KEYS):
            e.append("[4] %s: is_fee_schedule flag mismatch" % r["article_key"])
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
        print("FAIL: %d error(s) in Bankruptcy Fees Regulation track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Rules for Determining the Fees of Experts and Trustees under the Bankruptcy Law — 20 records (fresh issuance: all 20 اصلية)")
    print("  - trust gate: 6/20 MATCHES_PDF outright, 14 visually adjudicated (mean 0.8217, min 0.5822)")
    print("  - 17 numbered articles (1..17, no مكرر) + 3 fee-schedule tables (18-20); no dual-status divergence")
    print("  - IN-FORCE Minister of Justice Decision 2514 (02/08/1442H); committed MOJ PDF hash verified; Arabic governs")
    print("  - documented source anomalies: inconsistent table label formatting; art 19 sub-table header mislabeled الأصول instead of الديون")
    return 0


if __name__ == "__main__":
    sys.exit(main())
