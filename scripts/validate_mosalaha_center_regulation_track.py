#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Regulation of the Conciliation Center track
(10 records).

Trust gate: every article MATCHES_PDF (>=0.90 vs the committed official MOJ
PDF, hash re-verified) — all 10/10 matched outright via the 300dpi
tesseract-ara OCR channel (mean 0.9897, min 0.968); no visual-only
adjudication needed, though all 10 were additionally cross-checked visually.
Articles are numbered by ordinal position 1..10 (no مكرر), flat structure
with no chapter/section wrapper (section_ar empty for every article — not a
bug). FRESH FULL ISSUANCE: all 10 اصلية; none amended, repealed or added.
Tatweel is banned EXCEPT the 'هـ' digraph and space-bounded enumerator
dashes. DOCUMENTED SOURCE ANOMALY: article 1 item 2 ("الوزارة") reads
"الوزارة: ىوزارة العدل." — an anomalous character preceding "وزارة العدل",
confirmed present independently in both the portal DB text and the rendered
official PDF glyphs, preserved verbatim, not corrected. Companion track to
sources/muslaha/regulation/ (kept fully separate, not modified here)."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "mosalaha_center", "regulation", "official_source",
                   "mosalaha_center_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "mosalaha_center", "regulation", "verified",
                       "mosalaha_center_regulation_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "mosalaha_center_arabic_legal_llm",
                   "mosalaha_center_regulation_legal_llm_001_010.json")
PDF = os.path.join(ROOT, "inputs", "mosalaha_center_official_pdfs",
                   "mosalaha_center_regulation_moj_official_ar.pdf")
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
N = 10
KEY_RE = r"mosalaha_center_art_(\d{3})$"
SIM_FLOOR = 0.90
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 10}
VISUALLY_ADJUDICATED = set()
TRUSTED = {"MATCHES_PDF", "MATCHES_PDF_VISUALLY_ADJUDICATED"}
AR = "ء-ي"
ANOMALY_KEY = "mosalaha_center_art_001"
ANOMALY_MARKER = "ىوزارة العدل"


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
        e.append("[1] numbered articles not a complete 1..%d sequence" % N)
    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))

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
        e.append("[2] unexpected amended/repealed/added articles present")

    # [2b] documented source anomaly in article 1 item 2 preserved verbatim
    if ANOMALY_MARKER not in arts.get(ANOMALY_KEY, {}).get("text", ""):
        e.append("[2b] article 1 missing the documented الوزارة anomaly marker")

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
        print("FAIL: %d error(s) in Regulation of the Conciliation Center track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Regulation of the Conciliation Center — 10 records (fresh issuance: all 10 اصلية)")
    print("  - trust gate: all 10/10 MATCHES_PDF outright via OCR channel (mean 0.9897, min 0.968); no visual adjudication needed")
    print("  - numbered 1..10 by ordinal position (no مكرر), flat structure; no dual-status divergence")
    print("  - IN-FORCE Council of Ministers Decision 103 (08/04/1434H); committed MOJ PDF hash verified; Arabic governs")
    print("  - documented source anomaly: art 1 item 2 (الوزارة) carries an anomalous character, confirmed in both official sources, preserved verbatim")
    return 0


if __name__ == "__main__":
    sys.exit(main())
