#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Labor Annex 3 and Annex 4 tracks.

Trust gate per annex: complete article sequence, all statuses ACTIVE, OCR
floor cleared, sections attached, verbatim/hash consistency across the
verified records and LLM layer. Latin characters are banned except the
whitelisted glyphs actually printed in the official PDF (annex 4 art 10 'o'
bullets; annex 4 art 14 'Enterprise resource planning (ERP)')."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATUS = "HRSD_OFFICIAL_PDF_OCR_CROSS_CHECKED"
OCR_FLOOR = 0.85
TRACKS = [
    {"annex": 3, "n": 20, "llm": "labor_annex3_legal_llm_001_020.json",
     "anchor": ("labor_annex3_art_001", "يقصد بالألفاظ")},
    {"annex": 4, "n": 72, "llm": "labor_annex4_legal_llm_001_072.json",
     "anchor": ("labor_annex4_art_001", "يقصد بالألفاظ")},
]
# article_key -> allowed latin token set (glyphs actually printed in the PDF)
LATIN_WHITELIST = {
    "labor_annex4_art_010": {"o"},
    "labor_annex4_art_014": {"Enterprise", "resource", "planning", "ERP"},
}


def main():
    e = []
    for t in TRACKS:
        n_annex, N = t["annex"], t["n"]
        src_p = os.path.join(ROOT, "sources", "labor", "annex%d" % n_annex,
                             "official_source", "labor_annex%d_official_source.json" % n_annex)
        rec_p = os.path.join(ROOT, "sources", "labor", "annex%d" % n_annex,
                             "verified", "labor_annex%d_verified_records.jsonl" % n_annex)
        llm_p = os.path.join(ROOT, "data", "labor_arabic_legal_llm", t["llm"])
        for p in (src_p, rec_p, llm_p):
            if not os.path.isfile(p):
                print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
        src = json.load(open(src_p, encoding="utf-8"))
        arts = src["articles"]

        nums = sorted(int(re.search(r"_art_(\d{3})$", k).group(1)) for k in arts)
        if nums != list(range(1, N + 1)):
            e.append("[a%d-1] articles not a complete 1..%d sequence" % (n_annex, N))
        for k, a in arts.items():
            if a["status"] != "ACTIVE":
                e.append("[a%d-1] %s: unexpected status %r" % (n_annex, k, a["status"]))
            if not a["text"].strip():
                e.append("[a%d-1] %s: empty text" % (n_annex, k))
            if (a.get("ocr_similarity") or 0) < OCR_FLOOR:
                e.append("[a%d-1] %s: OCR similarity below %.2f" % (n_annex, k, OCR_FLOOR))
            if not a.get("section_ar", "").strip():
                e.append("[a%d-1] %s: missing section heading" % (n_annex, k))
            latin = set(re.findall(r"[A-Za-z]+", a["text"]))
            if latin - LATIN_WHITELIST.get(k, set()):
                e.append("[a%d-1] %s: non-whitelisted latin %s"
                         % (n_annex, k, sorted(latin - LATIN_WHITELIST.get(k, set()))))
        akey, aprefix = t["anchor"]
        if not arts[akey]["text"].startswith(aprefix):
            e.append("[a%d-1] art 1 anchor mismatch" % n_annex)

        ver = [json.loads(l) for l in open(rec_p, encoding="utf-8") if l.strip()]
        if len(ver) != N:
            e.append("[a%d-2] %d verified records != %d" % (n_annex, len(ver), N))
        for r in ver:
            if r["article_text_verified"] != arts[r["article_key"]]["text"]:
                e.append("[a%d-2] %s: text != source" % (n_annex, r["article_key"]))
            if r.get("official_text_status") != STATUS:
                e.append("[a%d-2] %s: bad status" % (n_annex, r["article_key"]))
            for f in ("translation_performed", "legal_interpretation_performed",
                      "summarized_or_paraphrased", "english_used_for_correction"):
                if r.get(f) is not False:
                    e.append("[a%d-2] %s: %s must be False" % (n_annex, r["article_key"], f))
        llm = json.load(open(llm_p, encoding="utf-8"))
        recs = llm.get("records", [])
        if llm.get("record_count") != N or len(recs) != N:
            e.append("[a%d-3] llm count != %d" % (n_annex, N))
        for r in recs:
            if r["article_text_ar"] != arts[r["article_key"]]["text"]:
                e.append("[a%d-3] %s: llm text != source" % (n_annex, r["article_key"]))
            if r["article_text_hash_sha256"] != hashlib.sha256(
                    r["article_text_ar"].encode("utf-8")).hexdigest():
                e.append("[a%d-3] %s: hash mismatch" % (n_annex, r["article_key"]))
            if not r.get("keywords_ar") or not r.get("search_queries_ar"):
                e.append("[a%d-3] %s: missing retrieval metadata" % (n_annex, r["article_key"]))

    if e:
        print("FAIL: %d error(s) in Labor Annex 3/4 tracks:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Labor Annex 3 + 4 tracks — 20 + 72 records, complete sequences, all ACTIVE")
    print("  - OCR floor %.2f cleared for every article; section headings attached" % OCR_FLOOR)
    print("  - latin glyphs only where actually printed (annex 4 arts 10/14, whitelisted)")
    print("  - texts verbatim vs committed sources; hashes consistent; Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
