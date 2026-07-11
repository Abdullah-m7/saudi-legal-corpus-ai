#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the three Evidence Law companion tracks.

Trust gate per instrument: complete article sequence, every article
MATCHES_PDF >= 0.90 vs the committed official MOJ PDF (hash re-verified),
legal status 'اصلية' (all three are unamended, issued by MoJ decision 921 of
1444H), chapter paths attached, clean text (no latin/HTML/tatweel), and
verbatim/hash consistency across the verified records and LLM layers."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
SIM_FLOOR = 0.90
TRACKS = [
    {"dir": "electronic_rules", "n": 24,
     "pdf": "inputs/evidence_official_pdfs/evidence_electronic_rules_moj_official_ar.pdf",
     "anchor": "يقصد بالألفاظ الآتية -أينما وردت في هذه الضوابط-"},
    {"dir": "procedural_manuals", "n": 135,
     "pdf": "inputs/evidence_official_pdfs/evidence_procedural_manuals_moj_official_ar.pdf",
     "anchor": "يقصد بالألفاظ الآتية -أينما وردت في هذه الأدلة-"},
    {"dir": "expertise_rules", "n": 34,
     "pdf": "inputs/evidence_official_pdfs/evidence_expertise_rules_moj_official_ar.pdf",
     "anchor": "يقصد بالألفاظ الآتية -أينما وردت في هذه القواعد-"},
]


def main():
    e = []
    for t in TRACKS:
        d, N = t["dir"], t["n"]
        src_p = os.path.join(ROOT, "sources", "evidence", d, "official_source",
                             "evidence_%s_official_source.json" % d)
        rec_p = os.path.join(ROOT, "sources", "evidence", d, "verified",
                             "evidence_%s_verified_records.jsonl" % d)
        llm_p = os.path.join(ROOT, "data", "evidence_arabic_legal_llm",
                             "evidence_%s_legal_llm_001_%03d.json" % (d, N))
        pdf_p = os.path.join(ROOT, t["pdf"])
        for p in (src_p, rec_p, llm_p, pdf_p):
            if not os.path.isfile(p):
                print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
        src = json.load(open(src_p, encoding="utf-8"))
        arts = src["articles"]

        nums = sorted(int(re.search(r"_art_(\d{3})$", k).group(1)) for k in arts)
        if len(arts) != N or nums != list(range(1, N + 1)):
            e.append("[%s-1] articles not a complete 1..%d sequence" % (d, N))
        for k, a in arts.items():
            if a["status"] != "MATCHES_PDF":
                e.append("[%s-1] %s: UNTRUSTED status %r" % (d, k, a["status"]))
            if (a.get("pdf_similarity") or 0) < SIM_FLOOR:
                e.append("[%s-1] %s: similarity below %.2f" % (d, k, SIM_FLOOR))
            if a.get("legal_status_ar") != "اصلية":
                e.append("[%s-1] %s: unexpected legal status" % (d, k))
            if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]) or "ـ" in a["text"]:
                e.append("[%s-1] %s: empty/latin/html/tatweel" % (d, k))
            if not a.get("section_ar", "").strip():
                e.append("[%s-1] %s: missing chapter path" % (d, k))
        first = min(arts, key=lambda k: int(re.search(r"_art_(\d{3})$", k).group(1)))
        if not arts[first]["text"].startswith(t["anchor"]):
            e.append("[%s-1] art 1 anchor mismatch" % d)
        if src.get("issued_by_ar") != "قرار وزير العدل رقم (921) وتاريخ 16/03/1444هـ":
            e.append("[%s-1] issuing decision metadata missing" % d)

        sha = hashlib.sha256(open(pdf_p, "rb").read()).hexdigest()
        if sha != src["provenance"]["pdf_sha256"]:
            e.append("[%s-2] committed PDF sha256 mismatch" % d)

        ver = [json.loads(l) for l in open(rec_p, encoding="utf-8") if l.strip()]
        if len(ver) != N:
            e.append("[%s-3] %d verified records != %d" % (d, len(ver), N))
        for r in ver:
            if r["article_text_verified"] != arts[r["article_key"]]["text"]:
                e.append("[%s-3] %s: text != source" % (d, r["article_key"]))
            if r.get("official_text_status") != STATUS:
                e.append("[%s-3] %s: bad status" % (d, r["article_key"]))
            for f in ("translation_performed", "legal_interpretation_performed",
                      "summarized_or_paraphrased", "english_used_for_correction"):
                if r.get(f) is not False:
                    e.append("[%s-3] %s: %s must be False" % (d, r["article_key"], f))
        llm = json.load(open(llm_p, encoding="utf-8"))
        recs = llm.get("records", [])
        if llm.get("record_count") != N or len(recs) != N:
            e.append("[%s-4] llm count != %d" % (d, N))
        for r in recs:
            if r["article_text_ar"] != arts[r["article_key"]]["text"]:
                e.append("[%s-4] %s: llm text != source" % (d, r["article_key"]))
            if r["article_text_hash_sha256"] != hashlib.sha256(
                    r["article_text_ar"].encode("utf-8")).hexdigest():
                e.append("[%s-4] %s: hash mismatch" % (d, r["article_key"]))
            if not r.get("keywords_ar") or not r.get("search_queries_ar"):
                e.append("[%s-4] %s: missing retrieval metadata" % (d, r["article_key"]))

    if e:
        print("FAIL: %d error(s) in Evidence companion tracks:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Evidence companion tracks — 24 + 135 + 34 = 193 records, complete sequences")
    print("  - trust gate: every article MATCHES_PDF >= %.2f; all 'اصلية' (MoJ decision 921, 1444H)" % SIM_FLOOR)
    print("  - all three committed official MOJ PDF hashes verified; definition-article anchors verbatim")
    print("  - texts verbatim vs committed sources; hashes consistent; Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
