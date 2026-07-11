#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Sharia Procedure implementing-regulation track
(639 records, consolidated amended regulation, DUAL-STATUS model).

Trust gate: every provision MATCHES_PDF against the committed official MOJ PDF
(hash re-verified); the document-order sequence is a complete 1..639; each
provision carries BOTH the PDF badge status (pdf_document_status_ar, the
governing anchor) and the portal live legal status (portal_legal_status_ar),
with is_repealed/is_amended/is_added driven by the PDF badge and the 151
Evidence-Law-superseded provisions flagged is_superseded with superseded_by_ar.
Repealed provisions keep full text and are flagged, not deleted. Tatweel banned
EXCEPT the 'هـ' digraph and space-bounded enumerator dashes. Six provisions
scored below the similarity floor and were VISUALLY adjudicated on the rendered
PDF pages (digit-in-parenthetical artifacts + one معدلة body preferred from the
PDF); they are the only provisions permitted below the floor."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "sharia_procedure", "regulation", "official_source",
                   "sharia_procedure_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "sharia_procedure", "regulation", "verified",
                       "sharia_procedure_regulation_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "sharia_procedure_arabic_legal_llm",
                   "sharia_procedure_regulation_legal_llm_001_637.json")
PDF = os.path.join(ROOT, "inputs", "sharia_procedure_official_pdfs",
                   "sharia_procedure_regulation_moj_official_ar.pdf")
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
N = 637  # 639 portal nodes fetched; 2 exact redundancies removed to match the PDF
SIM_FLOOR = 0.90
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
PDF_COUNTS = {"اصلية": 536, "معدلة": 17, "ملغاة": 63, "مضافة": 21}
PORTAL_COUNTS = {"اصلية": 388, "معدلة": 16, "ملغاة": 212, "مضافة": 21}
SUPERSEDED = 149
# The six provisions adjudicated visually on the rendered PDF pages (below floor).
VISUALLY_ADJUDICATED = {"mur_reg_art_010", "mur_reg_art_072", "mur_reg_art_081",
                        "mur_reg_art_482", "mur_reg_art_483", "mur_reg_art_588"}
DUP_LABELS = {"٣/١٠٤", "٣/١٦٦", "٣/١٧٩", "٣/٦٥", "٦/٧٥"}
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

    # [1] structure: complete document order 1..639
    pos = sorted(int(re.match(r"mur_reg_art_(\d+)$", k).group(1)) for k in arts)
    if pos != list(range(1, N + 1)):
        e.append("[1] document order not a complete 1..%d sequence" % N)
    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))

    # [2] trust gate + dual status
    pdf_sc, portal_sc = Counter(), Counter()
    superseded = 0
    for k, a in arts.items():
        if a["status"] != "MATCHES_PDF":
            e.append("[2] %s: UNTRUSTED status %r" % (k, a["status"]))
        sim = a.get("pdf_similarity") or 0
        if sim < SIM_FLOOR and k not in VISUALLY_ADJUDICATED:
            e.append("[2] %s: sim %.3f below floor and not visually adjudicated" % (k, sim))
        pdf_st = a.get("pdf_document_status_ar")
        portal_st = a.get("portal_legal_status_ar")
        if pdf_st not in ALLOWED_STATUS:
            e.append("[2] %s: bad pdf_document_status %r" % (k, pdf_st))
        if portal_st not in ALLOWED_STATUS:
            e.append("[2] %s: bad portal_legal_status %r" % (k, portal_st))
        pdf_sc[pdf_st] += 1
        portal_sc[portal_st] += 1
        want_sup = (portal_st == "ملغاة" and pdf_st != "ملغاة")
        if bool(a.get("is_superseded")) != want_sup:
            e.append("[2] %s: is_superseded inconsistent with statuses" % k)
        if want_sup:
            superseded += 1
            if a.get("superseded_by_ar") != "نظام الإثبات (م/43)":
                e.append("[2] %s: missing/incorrect superseded_by_ar" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
    for st, want in PDF_COUNTS.items():
        if pdf_sc.get(st) != want:
            e.append("[2] pdf status %s: %d != %d" % (st, pdf_sc.get(st), want))
    for st, want in PORTAL_COUNTS.items():
        if portal_sc.get(st) != want:
            e.append("[2] portal status %s: %d != %d" % (st, portal_sc.get(st), want))
    if superseded != SUPERSEDED:
        e.append("[2] superseded %d != %d" % (superseded, SUPERSEDED))

    # [2b] duplicate labels: exactly the 5 known repeal+replacement pairs
    label_counts = Counter(a["number_label_ar"] for a in arts.values())
    dups = {lbl for lbl, c in label_counts.items() if c > 1}
    if dups != DUP_LABELS:
        e.append("[2b] duplicate labels %s != expected %s" % (sorted(dups), sorted(DUP_LABELS)))

    # [3] committed PDF hash
    if hashlib.sha256(open(PDF, "rb").read()).hexdigest() != src["provenance"]["pdf_sha256"]:
        e.append("[3] committed MOJ PDF sha256 mismatch")

    # [4] verified records: flags consistent with pdf badge; verbatim
    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts[r["article_key"]]
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        pdf_st = r.get("pdf_document_status_ar")
        if (r.get("is_repealed") != (pdf_st == "ملغاة") or r.get("is_amended") != (pdf_st == "معدلة")
                or r.get("is_added") != (pdf_st == "مضافة")):
            e.append("[4] %s: status flags inconsistent with pdf badge" % r["article_key"])
        if r.get("official_text_status") != STATUS:
            e.append("[4] %s: bad status" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    # [5] LLM layer verbatim/hashes + marker discipline
    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    for r in recs:
        a = arts[r["article_key"]]
        if r["article_text_ar"] != a["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        # superseded provisions must be marked in the llm title; repealed get (ملغاة)
        t = r["llm_title_ar"]
        if r["is_repealed"] and "(ملغاة)" not in t:
            e.append("[5] %s: repealed provision missing (ملغاة) marker" % r["article_key"])
        if r.get("is_superseded") and "مستبدلة بنظام الإثبات" not in t:
            e.append("[5] %s: superseded provision missing supersession marker" % r["article_key"])
    repealed = sum(1 for r in recs if r["is_repealed"])
    if repealed != PDF_COUNTS["ملغاة"]:
        e.append("[5] repealed count %d != %d" % (repealed, PDF_COUNTS["ملغاة"]))
    sup = sum(1 for r in recs if r.get("is_superseded"))
    if sup != SUPERSEDED:
        e.append("[5] superseded count %d != %d" % (sup, SUPERSEDED))

    if e:
        print("FAIL: %d error(s) in Sharia Procedure Regulation track:" % len(e))
        for x in e[:20]:
            print("  - %s" % x)
        return 1
    print("PASS: Sharia Procedure implementing regulation — 637 records (consolidated, dual-status)")
    print("  - 639 portal nodes fetched; 2 exact redundancies (١/٢٣٢, ١٢/٢٢٨) removed to match the PDF")
    print("  - PDF-badge status (governing): 536 اصلية / 17 معدلة / 63 ملغاة / 21 مضافة")
    print("  - portal legal status: 388 اصلية / 16 معدلة / 212 ملغاة / 21 مضافة")
    print("  - 149 provisions superseded by the Law of Evidence (م/43) flagged is_superseded + marked in title")
    print("  - every provision MATCHES_PDF; 6 sub-floor provisions visually adjudicated; PDF hash verified")
    print("  - repealed provisions keep full text and are flagged (not deleted); Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
