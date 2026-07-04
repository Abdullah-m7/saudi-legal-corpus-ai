#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the FULL official English Legal LLM-ready layer (all 281 articles).

Builds one LLM/RAG-ready record per article directly on the EXACT english_reference_text from the
full official English BOE guidance reference alignment file. The English guidance text is copied
verbatim as `legal_rule_text_en`; only mechanical retrieval metadata (titles, path, conservative
keywords/queries) is generated. This layer does NOT summarize, paraphrase, translate, analyze, or
OCR-correct the text, and it does NOT use Arabic (to rewrite English) or Chinese. English is an
official guidance translation only — NOT binding, NOT governing; the Arabic text is governing.
Not legal advice.

Reads : data/english_reference/companies_law_m132_1443_en_reference_001_281.json
Writes: data/official_english_legal_llm/companies_law_m132_1443_official_english_legal_llm_001_281.json
"""

from __future__ import annotations

import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "english_reference",
                   "companies_law_m132_1443_en_reference_001_281.json")
OUT_DIR = os.path.join(ROOT, "data", "official_english_legal_llm")
OUT = os.path.join(OUT_DIR,
                   "companies_law_m132_1443_official_english_legal_llm_001_281.json")

LAW_ID = "sa-companies-law-m132-1443"
TARGET = 281
SOURCE_FILE = "inputs/companies_law_official_english_guidance.pdf"
SOURCE_REFERENCE_FILE = ("data/english_reference/"
                         "companies_law_m132_1443_en_reference_001_281.json")
GUIDANCE_NOTE = ("This translation is provided for guidance. The governing text is the "
                 "Arabic text.")


def _sha256(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def _search_queries(n, heading):
    q = [
        "Companies Law Article %d" % n,
        "Article %d Companies Law" % n,
    ]
    h = (heading or "").strip()
    if h:
        q.append("Companies Law %s" % h)
        if h not in q:
            q.append(h)
    seen, out = set(), []
    for x in q:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def build_record(sr):
    n = sr["article_number"]
    heading = sr["article_heading_en"]
    text = sr["english_reference_text"]
    keywords = list(sr.get("llm", {}).get("keywords_en", []))  # reuse reference keywords
    return {
        "law_id": LAW_ID,
        "article_number": n,
        "article_heading_en": heading,
        "record_id": "oe-llm-companies-art-%03d" % n,
        "record_type": "official_english_guidance_article",
        "language": "en",
        "governing_text_language": "ar",
        "legal_rule_text_en": text,
        "legal_rule_text_hash_sha256": _sha256(text),
        "llm_title_en": "Article %d: %s" % (n, heading),
        "retrieval_title_en": "Companies Law - Article %d - %s" % (n, heading),
        "article_path": "companies_law/articles/%03d/en" % n,
        "keywords_en": keywords,
        "search_queries_en": _search_queries(n, heading),
        "source_trust": {
            "english_source_status": "official_guidance_translation",
            "source_authority": "Bureau of Experts at the Council of Ministers",
            "department": "Official Translation Department",
            "source_file": SOURCE_FILE,
            "source_reference_file": SOURCE_REFERENCE_FILE,
            "governing_text_language": "ar",
            "manual_review_status": "needs_manual_check",
            "guidance_note": GUIDANCE_NOTE,
            "binding_status": "guidance_only_not_binding",
            "notes": "Verbatim official English guidance text copied from the full English "
                     "reference alignment (english_reference_text). Not summarized, paraphrased, "
                     "translated, or OCR-corrected. English is an official guidance translation "
                     "only — not binding and not governing; the Arabic text is governing. Not "
                     "legal advice.",
        },
    }


def build():
    with open(SRC, "r", encoding="utf-8") as fh:
        src = json.load(fh)
    srecs = sorted(src["records"], key=lambda r: r["article_number"])
    records = [build_record(r) for r in srecs]

    payload = {
        "layer_id": "sa-companies-official-english-legal-llm-full",
        "law_id": LAW_ID,
        "title_en": "Companies Law — full official English Legal LLM-ready layer (281 articles)",
        "record_type": "official_english_guidance_article",
        "language": "en",
        "governing_text_language": "ar",
        "record_count": len(records),
        "article_range": [1, TARGET],
        "source_reference_file": SOURCE_REFERENCE_FILE,
        "source_file": SOURCE_FILE,
        "separate_from": "data/english_legal_llm/ (old partial English Legal LLM layer, "
                         "8 files / 87 records) — left untouched",
        "english_source_status": "official_guidance_translation",
        "binding_status": "guidance_only_not_binding",
        "not_legal_advice": True,
        "disclaimer_en": "Full official English Legal LLM-ready layer built verbatim from the "
                         "official English BOE guidance reference alignment. English is guidance "
                         "only — not binding and not governing; the Arabic text is governing. "
                         "legal_rule_text_en equals the reference english_reference_text exactly. "
                         "Not legal advice.",
        "records": records,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("wrote full English Legal LLM-ready layer: %d records (articles %d..%d) -> %s"
          % (len(records), records[0]["article_number"], records[-1]["article_number"],
             os.path.relpath(OUT, ROOT)))


def main():
    build()


if __name__ == "__main__":
    main()
