#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Labor Annex 3 and Annex 4 tracks.

Annex 3: ضوابط وقواعد ممارسة نشاط التوسط في توظيف السعوديين — 20 articles.
Annex 4: قواعد ممارسة نشاط الاستقدام وتقديم الخدمات العمالية — 72 articles.
Both from the official HRSD Labor implementing-regulation PDF (same committed
file as the regulation and annex 1 tracks), OCR-verified per article (see the
source artifacts). Printed latin bullet glyphs and the printed ERP phrase in
annex 4 are kept verbatim. Arabic governs; no translation, paraphrase, or
legal interpretation. Read-only over inputs; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATUS = "HRSD_OFFICIAL_PDF_OCR_CROSS_CHECKED"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي هذه القواعد").split())

TRACKS = [
    {"annex": 3, "law_id": "sa-labor-saudization-mediation-rules",
     "doc_ar": "ضوابط وقواعد ممارسة نشاط التوسط في توظيف السعوديين",
     "doc_en": "Saudi-Employment Mediation Rules (Labor Annex 3)",
     "component": "recruitment_mediation_rules", "n": 20,
     "llm_name": "labor_annex3_legal_llm_001_020.json",
     "query_doc": "ضوابط التوسط في توظيف السعوديين"},
    {"annex": 4, "law_id": "sa-labor-recruitment-services-rules",
     "doc_ar": "قواعد ممارسة نشاط الاستقدام وتقديم الخدمات العمالية",
     "doc_en": "Recruitment and Labor-Services Rules (Labor Annex 4)",
     "component": "recruitment_services_rules", "n": 72,
     "llm_name": "labor_annex4_legal_llm_001_072.json",
     "query_doc": "قواعد نشاط الاستقدام"},
]


def _kw(text, k=6, fallback="لائحة"):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [fallback]


def build(track):
    n_annex = track["annex"]
    src_path = os.path.join(ROOT, "sources", "labor", "annex%d" % n_annex,
                            "official_source", "labor_annex%d_official_source.json" % n_annex)
    out_ver = os.path.join(ROOT, "sources", "labor", "annex%d" % n_annex, "verified")
    records_path = os.path.join(out_ver, "labor_annex%d_verified_records.jsonl" % n_annex)
    summary_path = os.path.join(out_ver, "labor_annex%d_verified_summary.json" % n_annex)
    llm_path = os.path.join(ROOT, "data", "labor_arabic_legal_llm", track["llm_name"])

    src = json.load(open(src_path, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=lambda k: int(re.search(r"_art_(\d{3})$", k).group(1)))
    os.makedirs(out_ver, exist_ok=True)

    ver, llm = [], []
    for key in keys:
        a = arts[key]
        n = int(re.search(r"_art_(\d{3})$", key).group(1))
        text = a["text"]
        ver.append({"law_key": "labor", "law_component": track["component"],
                    "language": "ar",
                    "record_layer": "LABOR_ANNEX%d_ARABIC_VERIFIED_TEXT" % n_annex,
                    "article_number": n, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "ocr_similarity": a.get("ocr_similarity"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; annex %d of the official HRSD "
                                              "PDF, verified against rendered-page OCR (see "
                                              "source artifact)." % n_annex),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": track["law_id"], "law_component": track["component"],
                    "article_number": n, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "record_id": "labor-annex%d-llm-art-%03d" % (n_annex, n),
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s (%s)" % (track["doc_ar"], a["number_label_ar"],
                                                      a.get("section_ar", "")),
                    "retrieval_title_ar": "%s - %s" % (track["doc_ar"], a["number_label_ar"]),
                    "article_path": "labor/annex%d/articles/%03d" % (n_annex, n),
                    "keywords_ar": _kw(text, fallback=track["query_doc"]),
                    "search_queries_ar": ["المادة %d %s" % (n, track["query_doc"]),
                                          "%s المادة %d" % (track["query_doc"], n),
                                          "المادة %d من %s" % (n, track["doc_ar"])],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": "Ministry of Human Resources and Social Development (HRSD)",
                                     "source_authority_ar": "وزارة الموارد البشرية والتنمية الاجتماعية",
                                     "source_status": "hrsd_official_pdf_ocr_cross_checked",
                                     "source_document_ar": track["doc_ar"],
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(records_path, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "labor",
               "layer": "LABOR_ANNEX%d_ARABIC_VERIFIED_TEXT" % n_annex,
               "record_count": len(ver), "official_text_status": STATUS,
               "sections": src["stats"].get("sections", []),
               "source_artifact": os.path.relpath(src_path, ROOT)},
              open(summary_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-labor-annex%d-arabic-legal-llm-full" % n_annex,
               "law_id": track["law_id"], "law_component": track["component"],
               "title_ar": track["doc_ar"] + " — الطبقة العربية الجاهزة للنماذج اللغوية (%d مادة)" % len(llm),
               "title_en": track["doc_en"] + " — Arabic LLM-ready layer (%d records)" % len(llm),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, track["n"]], "text_status": STATUS,
               "not_legal_advice": True, "records": llm},
              open(llm_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote annex %d: %d verified + %d LLM-ready records" % (n_annex, len(ver), len(llm)))


def main():
    for track in TRACKS:
        build(track)


if __name__ == "__main__":
    main()
