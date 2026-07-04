#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the FULL official Arabic Legal LLM-ready layer (all 281 articles).

Builds one LLM/RAG-ready record per article directly on the EXACT official_text_ar ingested from
the Bureau of Experts owner-provided source packet. The statutory text is copied verbatim; only
mechanical retrieval metadata (titles, path, conservative keywords/queries) is generated. This
layer does NOT summarize, paraphrase, analyze, normalize, or OCR-correct the legal text, and it
does NOT use English/Chinese text or OCR text. Arabic is governing. Not legal advice.

Reads : data/official_arabic/companies_law_m132_1443_official_arabic_user_provided.json
Writes: data/official_arabic_legal_llm/companies_law_m132_1443_official_arabic_legal_llm_001_281.json
"""

from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "official_arabic",
                   "companies_law_m132_1443_official_arabic_user_provided.json")
OUT_DIR = os.path.join(ROOT, "data", "official_arabic_legal_llm")
OUT = os.path.join(OUT_DIR, "companies_law_m132_1443_official_arabic_legal_llm_001_281.json")

LAW_ID = "sa-companies-law-m132-1443"
TARGET = 281

# Conservative Arabic stopwords / connective particles dropped from title-derived keywords.
_STOP = {
    "في", "من", "على", "عن", "إلى", "الى", "و", "أو", "او", "ثم", "التي", "الذي",
    "ما", "عند", "بين", "لدى", "هذا", "هذه", "ذلك", "التى", "أن", "ان", "مع", "أي", "اي",
}


def _sha256(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def _keywords(title):
    """Conservative title-derived keywords: meaningful title tokens only (no invention)."""
    out = []
    for raw in re.split(r"\s+", title.strip()):
        tok = raw.strip("().,،؛:-—\"'«»")
        if not tok or tok in _STOP:
            continue
        # strip a leading connective و only when it leaves a real word
        if tok.startswith("و") and len(tok) > 3 and tok[1:] not in _STOP:
            tok = tok[1:]
        if len(tok) < 3 or tok in _STOP:
            continue
        if tok not in out:
            out.append(tok)
    return out


def _search_queries(n, title):
    """Conservative mechanical retrieval queries: article-number + title based only."""
    q = [
        "المادة %d نظام الشركات" % n,
        "نظام الشركات المادة %d" % n,
    ]
    t = title.strip()
    if t:
        q.append("%s نظام الشركات" % t)
        if t not in q:
            q.append(t)
    seen, out = set(), []
    for x in q:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def build_record(a):
    n = a["article_number"]
    title = a["article_title_ar"]
    text = a["official_text_ar"]
    return {
        "law_id": LAW_ID,
        "article_number": n,
        "article_title_ar": title,
        "record_id": "oa-llm-companies-art-%03d" % n,
        "record_type": "official_arabic_article",
        "language": "ar",
        "governing_text_language": "ar",
        "official_text_ar": text,
        "official_text_hash_sha256": _sha256(text),
        "llm_title_ar": "المادة %d: %s" % (n, title),
        "retrieval_title_ar": "نظام الشركات - المادة %d - %s" % (n, title),
        "article_path": "companies_law/articles/%03d" % n,
        "keywords_ar": _keywords(title),
        "search_queries_ar": _search_queries(n, title),
        "source_trust": {
            "source_authority": "Bureau of Experts at the Council of Ministers",
            "source_authority_ar": "هيئة الخبراء بمجلس الوزراء",
            "source_status": "owner_provided_from_official_boe_source",
            "source_packet_status": "official_boe_owner_provided",
            "controlling_source_basis": "owner_provided_boe_text_plus_pdf_packet",
            "ocr_role": "supporting_artifact_only_not_controlling_gate",
            "text_type": "official_arabic_statutory_text",
            "article_by_article_verified": False,
            "verification_status":
                "official_boe_source_packet_owner_provided_not_live_html_verified",
            "notes": "Verbatim official Arabic statutory text from the Bureau of Experts "
                     "owner-provided source packet. Not summarized, paraphrased, normalized, or "
                     "OCR-corrected. article_by_article_verified is false because no direct "
                     "automated verification against live BOE HTML has been performed. OCR is a "
                     "supporting artifact only, not the source-confidence gate. Arabic is "
                     "governing; not legal advice.",
        },
    }


def build():
    with open(SRC, "r", encoding="utf-8") as fh:
        src = json.load(fh)
    arts = sorted(src["articles"], key=lambda a: a["article_number"])
    records = [build_record(a) for a in arts]

    payload = {
        "layer_id": "sa-companies-official-arabic-legal-llm-full",
        "law_id": LAW_ID,
        "title_ar": "نظام الشركات — الطبقة العربية الرسمية الجاهزة للنماذج اللغوية (281 مادة)",
        "title_en": "Companies Law — full official Arabic LLM-ready layer (281 articles)",
        "record_type": "official_arabic_article",
        "language": "ar",
        "governing_text_language": "ar",
        "record_count": len(records),
        "article_range": [1, TARGET],
        "source_candidate_file": os.path.relpath(SRC, ROOT),
        "schema": "schemas/official_arabic_legal_llm.schema.json",
        "separate_from": "data/arabic_legal_llm/ (old internally-reviewed summary/provision layer)",
        "not_legal_advice": True,
        "disclaimer_ar": "هذه طبقة استرجاعية جاهزة للنماذج اللغوية مبنية على النص العربي الرسمي "
                         "الكامل حرفيًّا من حزمة مصدر هيئة الخبراء المقدَّمة من المالك. لا تلخيص "
                         "ولا إعادة صياغة ولا تصحيح OCR. لم يُجرَ تحقق آلي مباشر مقابل صفحات "
                         "هيئة الخبراء الحية، لذا يبقى article_by_article_verified=false. "
                         "العربية هي اللغة الحاكمة. ليست استشارة قانونية.",
        "records": records,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("wrote official Arabic full LLM-ready layer: %d records (articles %d..%d) -> %s"
          % (len(records), records[0]["article_number"], records[-1]["article_number"],
             os.path.relpath(OUT, ROOT)))


def main():
    build()


if __name__ == "__main__":
    main()
