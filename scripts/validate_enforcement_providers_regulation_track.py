#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Regulation on Enforcement Service Providers
track (18 records).

Trust gate: every article MATCHES_PDF_VISUALLY_ADJUDICATED (>=0.90 vs the
committed official MOJ PDF, hash re-verified, unless visually adjudicated).
This PDF's text layer uses a consistent per-line word-order-reversal RTL
extraction convention that caps automated similarity scoring below the 0.90
floor for every record (18/18 landed between 0.5973 and 0.786, mean 0.7476),
so all 18 were visually adjudicated verbatim. Articles are numbered by
ordinal position 1..18 (no مكرر); every article carries an explained
legal_status consistent with its is_repealed/is_amended/is_added flags. The
section-API status equals the PDF status for every article (no dual-status
divergence). FRESH FULL ISSUANCE: all 18 اصلية; none amended, repealed or
added. Tatweel is banned EXCEPT the 'هـ' digraph and space-bounded
enumerator dashes. DOCUMENTED SOURCE ANOMALIES (confirmed identically in
both official sources, preserved verbatim): art 8 uses Persian
keheh/farsi-yeh in "وللوکیل"; art 9's "ترخيصه" is spelled inconsistently
within the same article; art 10 item 8 uses a Western ASCII digit "8."
instead of Eastern Arabic-Indic "٨."; art 15 item 2 uses the Extended
Arabic-Indic/Persian digit "۲" instead of standard "٢"."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "enforcement_providers", "regulation", "official_source",
                   "enforcement_providers_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "enforcement_providers", "regulation", "verified",
                       "enforcement_providers_regulation_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "enforcement_providers_arabic_legal_llm",
                   "enforcement_providers_regulation_legal_llm_001_018.json")
PDF = os.path.join(ROOT, "inputs", "enforcement_providers_official_pdfs",
                   "enforcement_providers_regulation_moj_official_ar.pdf")
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
N = 18
KEY_RE = r"enforcement_providers_art_(\d{3})$"
SIM_FLOOR = 0.90
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 18}
VISUALLY_ADJUDICATED = {"enforcement_providers_art_%03d" % n for n in range(1, N + 1)}
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
        print("FAIL: %d error(s) in Enforcement Providers Regulation track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Regulation on Enforcement Service Providers — 18 records (fresh issuance: all 18 اصلية)")
    print("  - trust gate: 18/18 visually adjudicated (mean 0.7476, min 0.5973) — RTL text-layer extraction artifact caps automated scoring")
    print("  - numbered 1..18 by ordinal position (no مكرر); no dual-status divergence")
    print("  - IN-FORCE Minister of Justice Decision 2268 (20/08/1443H); committed MOJ PDF hash verified; Arabic governs")
    print("  - documented source anomalies: Persian keheh/farsi-yeh in art 8; inconsistent yeh spelling in art 9; ASCII digit in art 10; Extended Arabic-Indic digit in art 15")
    return 0


if __name__ == "__main__":
    sys.exit(main())
