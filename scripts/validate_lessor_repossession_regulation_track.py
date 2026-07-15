#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Controls for the Lessor's Repossession of
Movable Assets track (7 records) — ضوابط تسلم المؤجر الأصول المنقولة.

Trust gate: every item MATCHES_PDF or MATCHES_PDF_VISUALLY_ADJUDICATED
(>=0.90 vs the committed official MOJ PDF, hash re-verified, unless
visually adjudicated). 4/7 matched outright (mean 0.9049, min 0.7976); the
other 3 (items 5, 6, 7) were visually adjudicated verbatim due to
short-item-length-amplified OCR artifacts. Item 1 is labeled "تمهيد"
(Preamble); items 2-7 are labeled with Arabic ordinal words (أولاً..سادساً),
not مادة-numbered, but numbered by ordinal position 1..7 internally (no
مكرر), flat structure with no chapter/section wrapper (section_ar empty for
every item — not a bug). FRESH FULL ISSUANCE: all 7 اصلية; none amended,
repealed or added. DOCUMENTED SOURCE ANOMALY: item 1's preamble cites
"المادة (٩٣/د)" of the Enforcement Law as its enabling provision — a
genuine citation typo (the correct sub-item is هـ, confirmed via the
regulation's own promulgating decree), present identically in both official
sources, preserved verbatim."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "lessor_repossession", "regulation", "official_source",
                   "lessor_repossession_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "lessor_repossession", "regulation", "verified",
                       "lessor_repossession_regulation_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "lessor_repossession_arabic_legal_llm",
                   "lessor_repossession_regulation_legal_llm_001_007.json")
PDF = os.path.join(ROOT, "inputs", "lessor_repossession_official_pdfs",
                   "lessor_repossession_regulation_moj_official_ar.pdf")
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
N = 7
KEY_RE = r"lessor_repossession_art_(\d{3})$"
SIM_FLOOR = 0.90
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 7}
VISUALLY_ADJUDICATED = {"lessor_repossession_art_%03d" % n for n in (5, 6, 7)}
EXPECTED_LABELS = ["تمهيد", "أولاً", "ثانياً", "ثالثاً", "رابعاً", "خامساً", "سادساً"]
TRUSTED = {"MATCHES_PDF", "MATCHES_PDF_VISUALLY_ADJUDICATED"}
AR = "ء-ي"
ANOMALY_KEY = "lessor_repossession_art_001"
ANOMALY_MARKER = "٩٣/د"


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
        e.append("[1] numbered items not a complete 1..%d sequence" % N)
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
        if a.get("section_ar"):
            e.append("[2] %s: unexpected non-empty section_ar in a flat-structure regulation" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
    if visual != VISUALLY_ADJUDICATED:
        e.append("[2] visually-adjudicated set %s != expected %s"
                 % (sorted(visual), sorted(VISUALLY_ADJUDICATED)))
    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("معدلة") or sc.get("ملغاة") or sc.get("مضافة"):
        e.append("[2] unexpected amended/repealed/added items present")

    for i, want_label in enumerate(EXPECTED_LABELS, start=1):
        key = "lessor_repossession_art_%03d" % i
        if arts.get(key, {}).get("number_label_ar") != want_label:
            e.append("[2d] %s: number_label_ar %r != expected %r"
                     % (key, arts.get(key, {}).get("number_label_ar"), want_label))

    # [2b] documented source anomaly in item 1's preamble citation preserved verbatim
    if ANOMALY_MARKER not in arts.get(ANOMALY_KEY, {}).get("text", ""):
        e.append("[2b] item 1 missing the documented ٩٣/د citation anomaly marker")

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
        print("FAIL: %d error(s) in Lessor Repossession Regulation track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Lessor Repossession Regulation — 7 records (fresh issuance: all 7 اصلية)")
    print("  - trust gate: 4/7 MATCHES_PDF outright via OCR channel, 3 visually adjudicated (mean 0.9049, min 0.7976)")
    print("  - numbered 1..7 by ordinal position (no مكرر), labels تمهيد/أولاً..سادساً, flat structure; no dual-status divergence")
    print("  - IN-FORCE Minister of Justice Decision 1448 (04/04/1440H); committed MOJ PDF hash verified; Arabic governs")
    print("  - documented source anomaly: item 1 preamble cites المادة (٩٣/د) — a genuine citation typo (correct sub-item is هـ), confirmed in both official sources, preserved verbatim")
    return 0


if __name__ == "__main__":
    sys.exit(main())
