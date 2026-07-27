#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Frequency Spectrum Regulations for Radio Services and
Applications track (تنظيمات استخدامات الطيف الترددي للخدمات الراديوية
وتطبيقاتها, document code RS45, First Edition, CST Decision No. 559/1446,
dated 23/7/1446H = 23/1/2025G).

CST (Communications, Space & Technology Commission) instrument that
consolidates six prior CST spectrum regulations (WLAN; Maritime services;
Fixed Wireless Links; Amateur Radio services; IMT band allocation;
Broadcasting services) into one document made of a General Framework (15
numbered sections) plus six detailed technical annexes.

SCOPE OF THIS TRACK -- GENERAL FRAMEWORK ONLY (15 SECTIONS): the official
Arabic PDF's body pages are vector-rendered images with NO selectable text
layer (confirmed via pdfplumber/pdftotext, both returning ~0 characters per
body page). The 15-section General Framework (pages 4-10) was transcribed
verbatim via direct high-resolution (150-600 DPI) visual reading, with
section/clause counts cross-checked structurally (never for Arabic wording)
against CST's own English-language PDF of the same document, which DOES
carry a full selectable text layer. The six technical annexes (pages 11-78,
~87% of the document) are dense frequency-band/channel-plan tables rendered
as non-extractable images; they were NOT ingested this pass -- a deliberate,
fully-disclosed scope limitation, not an oversight. See this track's own
official_source.json (verification_methodology_note and
known_unresolved_discrepancies) for the full account, including how a
single ambiguous word in clause 15-4 was disambiguated.

All 15 ingested sections are اصلية (single, first-and-only edition since
23/1/2025; no subsequent amendment to this text identified this pass). No
legal text is altered. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "frequency_spectrum_regulation", "law", "official_source",
                   "frequency_spectrum_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "frequency_spectrum_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "frequency_spectrum_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "frequency_spectrum_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "frequency_spectrum_regulation_arabic_legal_llm",
                        "frequency_spectrum_regulation_legal_llm_001_015.json")

LAW_ID = "sa-frequency-spectrum-regulation-559-1446"
LAW_AR = "تنظيمات استخدامات الطيف الترددي للخدمات الراديوية وتطبيقاتها"
STATUS = "CST_OFFICIAL_PDF_PRIMARY_VISUAL_TRANSCRIPTION_EN_STRUCTURAL_CROSSCHECK"
KEY_RE = r"frequency_spectrum_regulation_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن الوثيقة التنظيمات أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم الهيئة الطيف الترددي").split())


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
        is_amended = ls == "معدلة"
        text = a["text"]
        section = a.get("section_ar", "")
        title = a.get("article_title_ar", "")
        label = a["number_label_ar"] + ((". " + title) if title else "")
        ver.append({"law_key": "frequency_spectrum_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "FREQUENCY_SPECTRUM_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "article_title_ar": title,
                    "section_ar": section,
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": is_amended,
                    "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; PRIMARY source is the "
                                              "official CST (Communications, Space & "
                                              "Technology Commission) Arabic PDF of "
                                              "'تنظيمات استخدامات الطيف الترددي للخدمات "
                                              "الراديوية وتطبيقاتها' (RS45, First "
                                              "Edition), fetched directly from "
                                              "cst.gov.sa. The PDF's body pages are "
                                              "vector-rendered images with no selectable "
                                              "text layer; this section's text was "
                                              "transcribed via direct high-resolution "
                                              "visual reading and cross-checked "
                                              "structurally (section/clause counts only, "
                                              "never wording) against CST's own English "
                                              "PDF of the same document. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the "
                                              "source artifact before relying on this "
                                              "track's text -- in particular the fact "
                                              "that this track covers ONLY the 15-"
                                              "section General Framework; the "
                                              "document's six technical annexes "
                                              "(frequency-band/channel-plan tables, "
                                              "~87% of the document by page count) were "
                                              "NOT ingested this pass."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": label,
                    "section_ar": section,
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": is_amended, "is_added": ls == "مضافة",
                    "record_id": "frequency-spectrum-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, label),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, label),
                    "article_path": "frequency_spectrum_regulation/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["القسم %d %s" % (n, LAW_AR),
                                          "%s القسم %d" % (LAW_AR, n),
                                          "%s من تنظيمات الطيف الترددي" % a["number_label_ar"]],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("CST Decision No. 559/1446, "
                                                          "dated 23/7/1446H = 23/1/2025G "
                                                          "-- cst.gov.sa (issuing "
                                                          "Authority's own site); "
                                                          "consolidates six prior CST "
                                                          "spectrum regulations"),
                                     "source_authority_ar": ("قرار هيئة الاتصالات "
                                                            "والفضاء والتقنية رقم "
                                                            "(559/1446) وتاريخ "
                                                            "23/7/1446هـ الموافق "
                                                            "23/1/2025م — الموقع الرسمي "
                                                            "لهيئة الاتصالات والفضاء "
                                                            "والتقنية (cst.gov.sa)؛ "
                                                            "دمجت ست لوائح طيف ترددي "
                                                            "سابقة"),
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "frequency_spectrum_regulation",
               "layer": "FREQUENCY_SPECTRUM_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "decree_date_gregorian": src.get("decree_date_gregorian"),
               "administering_authority_en": src.get("administering_authority_en"),
               "consolidated_amended_law": True,
               "chapter_structure": src["chapter_structure"],
               "preamble_ar": src.get("preamble_ar"),
               "amendment_history": src.get("amendment_history"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-frequency-spectrum-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية "
                                     "(15 قسما -- الإطار العام فقط، اصلية جميعها)",
               "title_en": ("Regulations for the Use of Radio Frequency Spectrum for "
                            "Radio Services and their Applications — Arabic LLM-ready "
                            "layer (15 records, General Framework only, all original/"
                            "اصلية)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 15], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Frequency Spectrum Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
