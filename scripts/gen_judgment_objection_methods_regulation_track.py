#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Executive Regulation for Methods of Objecting to Judgments
(اللائحة التنفيذية لطرق الاعتراض على الأحكام).

Source: the official MOJ legal-portal text (Minister of Justice Decision
512, 05/01/1445H), fetched article-by-article (get-Section-Changes, 0
divergences from statuteStructure) and cross-verified against the official
MOJ PDF. 62 articles across 5 chapters (الباب الأول..الخامس: أحكام عامة /
الاستئناف / النقض / التماس إعادة النظر / أحكام ختامية); section_ar carries
each article's chapter heading, matching this corpus's convention for
chaptered instruments. This PDF's raw text layer exhibits the known RTL
word-order glyph-extraction artifact seen elsewhere in this corpus (scores
very low, ~0.02-0.5), but the 300dpi tesseract-ara OCR channel and the
word-reversed text-layer channel together cleared 45 of 62 articles
outright; the other 17 (predominantly longer multi-paragraph articles
where line-break-induced word-reversal and/or OCR degrade) were visually
adjudicated against the rendered PDF pages, confirming verbatim match. This
regulation is IN FORCE. FRESH FULL ISSUANCE: all 62 اصلية (0 معدلة / 0
ملغاة / 0 مضافة) — supersedes both Chapter 11 of the Sharia Procedure
Law's implementing regulation and the standalone (now repealed) Executive
Regulation for Appeal Procedures.

SOURCE-LEVEL CLEANUP (already applied to official_source.json before this
generator runs): 6 decorative in-word tatweel characters (letter-tatweel-
letter, not immediately preceded by heh) stripped from 4 articles, and 11
CMS zero-width-non-joiner (U+200C) artifacts stripped from 3 articles —
both confirmed present identically in the portal DB and the official PDF's
own typesetting, both non-substantive formatting/markup artifacts.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "judgment_objection_methods", "regulation", "official_source",
                   "judgment_objection_methods_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "judgment_objection_methods", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "judgment_objection_methods_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "judgment_objection_methods_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "judgment_objection_methods_arabic_legal_llm",
                        "judgment_objection_methods_regulation_legal_llm_001_062.json")

LAW_ID = "sa-judgment-objection-methods-regulation-1445"
LAW_AR = "اللائحة التنفيذية لطرق الاعتراض على الأحكام"
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
KEY_RE = r"judgment_objection_methods_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def _sort_key(key):
    return int(re.match(KEY_RE, key).group(1))


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for key in keys:
        a = arts[key]
        n = int(re.match(KEY_RE, key).group(1))
        ls = a.get("legal_status_ar")
        text = a["text"]
        section = a.get("section_ar", "")
        ver.append({"law_key": "judgment_objection_methods", "law_component": "regulation", "language": "ar",
                    "record_layer": "JUDGMENT_OBJECTION_METHODS_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": section,
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "pdf_similarity": a.get("pdf_similarity"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; official MOJ portal text cross-verified "
                                              "against the official MOJ PDF (verbatim; 45 of 62 "
                                              "articles matched the >=0.90 floor outright via the "
                                              "300dpi tesseract-ara OCR channel and/or the "
                                              "word-reversed text-layer channel, the raw PDF text "
                                              "layer alone exhibiting the known RTL word-order "
                                              "glyph-extraction artifact seen elsewhere in this "
                                              "corpus and scoring very low; mean 0.8686, min 0.0443; "
                                              "the remaining 17 articles (predominantly longer "
                                              "multi-paragraph articles where line-break-induced "
                                              "word-reversal and/or OCR degrade) were read directly "
                                              "off all 10 rendered 200dpi PDF pages as a direct "
                                              "visual cross-check and confirmed verbatim, including 2 "
                                              "documented character-level cleanups: decorative "
                                              "in-word tatweel and CMS zero-width-non-joiner "
                                              "artifacts, both stripped per corpus convention and "
                                              "both confirmed present identically in the portal DB "
                                              "and the official PDF's own typesetting; all 62 "
                                              "articles across all 10 pages were visually read in "
                                              "full)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": section,
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "record_id": "judgment-objection-methods-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "judgment_objection_methods/regulation/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d طرق الاعتراض على الأحكام" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": "Ministry of Justice (MOJ) — official legal portal",
                                     "source_authority_ar": "وزارة العدل — المنصة القانونية الرسمية",
                                     "source_status": "moj_portal_api_cross_checked_official_pdf",
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "judgment_objection_methods",
               "layer": "JUDGMENT_OBJECTION_METHODS_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": False,
               "visually_adjudicated": src["stats"]["visually_adjudicated"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-judgment-objection-methods-regulation-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (62 مادة؛ إصدار جديد كامل: 62 أصلية)",
               "title_en": "Executive Regulation for Methods of Objecting to Judgments — Arabic LLM-ready layer (62 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 62], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Judgment Objection Methods Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
