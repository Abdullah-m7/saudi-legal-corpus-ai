#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Regulation on the Marriage of a Saudi Man to a Non-Saudi Woman
and a Saudi Woman to a Non-Saudi Man (لائحة زواج السعودي بغير سعودية والسعودية
بغير سعودي).

Source: the official MOJ legal-portal text (Minister of Interior Decision
6874, 20/12/1422H — NOT a Minister of Justice or Council of Ministers
instrument, though hosted on the MOJ portal), fetched article-by-article
(get-Section-Changes, 0 divergences from statuteStructure) and cross-verified
against the official MOJ PDF, independently corroborated by the separately
fetched official issuance instrument (أداة الإصدار). This PDF's raw text
layer exhibits the known RTL word-order glyph-extraction artifact seen
elsewhere in this corpus (scores low, mean ~0.34), but the per-line
word-reversed text-layer channel and the 300dpi tesseract-ara OCR channel are
clean and all 11 of 11 articles matched the >=0.90 floor outright (mean
0.9426, min 0.9282) — no visual-only adjudication needed, though all 11 were
additionally read in full against rendered 200dpi/400dpi PDF page images as a
direct visual cross-check. This regulation is IN FORCE. FRESH FULL ISSUANCE:
all 11 اصلية (0 معدلة / 0 ملغاة / 0 مضافة). Substantive dependencies found in
the article text (not the portal's otherRelatedLegal list, which is empty
for this statute): Article 5 references نظام الأحوال المدنية (not yet
ingested under that law_key); Articles 3/4/6/7 assign roles to المحاكم
الشرعية and الممثليات السعودية; Articles 9-10 assign roles to ديوان المظالم
and وزير الداخلية.

Articles are numbered by their ordinal position (1..11; no مكرر), flat
structure with no chapter/section wrapper (section_ar empty for every
article). DOCUMENTED SOURCE ANOMALY: article 4 spells "وأباء" (fathers) with
a plain hamza-on-alef rather than the standard alef-madda spelling "وآباء" —
confirmed present independently in both the portal DB text and the rendered
official PDF glyphs (the document's separate summary/abstract block spells
the same word correctly, so the divergence is specific to Article 4's own
operative text) — preserved verbatim, not corrected.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "marriage_non_saudi", "regulation", "official_source",
                   "marriage_non_saudi_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "marriage_non_saudi", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "marriage_non_saudi_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "marriage_non_saudi_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "marriage_non_saudi_arabic_legal_llm",
                        "marriage_non_saudi_regulation_legal_llm_001_011.json")

LAW_ID = "sa-marriage-non-saudi-regulation-1422"
LAW_AR = "لائحة زواج السعودي بغير سعودية والسعودية بغير سعودي"
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
KEY_RE = r"marriage_non_saudi_art_(\d{3})$"
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
        ver.append({"law_key": "marriage_non_saudi", "law_component": "regulation", "language": "ar",
                    "record_layer": "MARRIAGE_NON_SAUDI_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "pdf_similarity": a.get("pdf_similarity"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; official MOJ portal text cross-verified "
                                              "against the official MOJ PDF (verbatim; all 11 articles "
                                              "matched the >=0.90 floor outright via the per-line "
                                              "word-reversed PDF text-layer channel or the 300dpi "
                                              "tesseract-ara OCR channel, the raw PDF text layer alone "
                                              "exhibiting the known RTL word-order glyph-extraction "
                                              "artifact seen elsewhere in this corpus and scoring low; "
                                              "mean 0.9426, min 0.9282; all 11 articles were "
                                              "additionally read in full against the rendered "
                                              "200dpi/400dpi PDF page images as a direct visual "
                                              "cross-check, alongside the separately-fetched official "
                                              "issuance instrument)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "record_id": "marriage-non-saudi-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "marriage_non_saudi/regulation/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d لائحة زواج السعودي بغير سعودية" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": "Ministry of Interior — official MOJ legal portal",
                                     "source_authority_ar": "وزارة الداخلية — المنصة القانونية الرسمية لوزارة العدل",
                                     "source_status": "moj_portal_api_cross_checked_official_pdf",
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "marriage_non_saudi", "layer": "MARRIAGE_NON_SAUDI_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": False,
               "visually_adjudicated": src["stats"]["visually_adjudicated"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-marriage-non-saudi-regulation-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (11 مادة؛ إصدار جديد كامل: 11 أصلية)",
               "title_en": "Regulation on the Marriage of a Saudi Man to a Non-Saudi Woman and a Saudi Woman to a Non-Saudi Man — Arabic LLM-ready layer (11 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 11], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Marriage Non-Saudi Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
