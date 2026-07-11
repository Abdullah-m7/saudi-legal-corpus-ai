#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the GTPL Implementing Regulation track (157 articles).

Source: the committed official Ministry of Finance consolidated PDF (April 2024,
law linked with regulation). Because the PDF's ToUnicode layer corrupts
lam-alef ligatures and bidi ordering, the Arabic was re-extracted at glyph
level (x-coordinate reordering, digit-run restoration, ligature repair) — a
pipeline validated against the independently captured GTPL law text (mean
token similarity 0.996 over 99/99 articles) — and duplicate article copies in
the interleaved layout were adjudicated against the rendered pages and
external official wording. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic/idempotent over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "gtpl", "regulation", "official_source",
                   "gtpl_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "gtpl", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "gtpl_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "gtpl_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "gtpl_arabic_legal_llm",
                        "gtpl_regulation_legal_llm_001_157.json")

LAW_ID = "sa-gtpl-m128-1440"
REG_AR = "اللائحة التنفيذية لنظام المنافسات والمشتريات الحكومية"
STATUS = "REEXTRACTED_FROM_OFFICIAL_MOF_PDF_CROSS_CHECKED"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [REG_AR]


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    n_total = src["article_count"]
    arts = src["articles"]
    os.makedirs(OUT_VER, exist_ok=True)
    ver, llm = [], []
    for n in range(1, n_total + 1):
        text = arts[str(n)]
        ver.append({"law_key": "gtpl", "law_component": "implementing_regulation",
                    "language": "ar", "record_layer": "GTPL_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "article_key": "gtpl_reg_art_%03d" % n,
                    "article_text_verified": text, "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; re-extracted from the official MOF "
                                              "consolidated PDF and cross-checked (see source artifact)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "implementing_regulation",
                    "article_number": n, "article_key": "gtpl_reg_art_%03d" % n,
                    "article_title_ar": "المادة %d" % n,
                    "record_id": "gtpl-reg-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — المادة %d" % (REG_AR, n),
                    "retrieval_title_ar": "%s - المادة %d" % (REG_AR, n),
                    "article_path": "gtpl/regulation/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, REG_AR),
                                          "%s المادة %d" % (REG_AR, n)],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": "Ministry of Finance",
                                     "source_authority_ar": "وزارة المالية",
                                     "source_status": "reextracted_from_official_mof_pdf_cross_checked",
                                     "source_document_ar": REG_AR},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})
    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "gtpl", "layer": "GTPL_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": n_total, "official_text_status": STATUS,
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-gtpl-regulation-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "implementing_regulation",
               "title_ar": REG_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (157 مادة)",
               "title_en": "GTPL Implementing Regulation — Arabic LLM-ready layer (157 articles)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": n_total,
               "article_range": [1, n_total], "text_status": STATUS,
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready GTPL-regulation records" % (n_total, n_total))


if __name__ == "__main__":
    main()
