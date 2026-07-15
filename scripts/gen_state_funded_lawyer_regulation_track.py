#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Mechanism for a Defendant in Major/Serious Crimes to Seek
Legal Counsel at the State's Expense (آلية الاستعانة بمحام على نفقة الدولة
للمتهم في الجرائم الكبيرة).

Source: the official MOJ legal-portal text (Minister of Justice Decision
1529, 06/05/1439H), fetched item-by-item (get-Section-Changes, 0 divergences
from statuteStructure) and cross-verified against the official MOJ PDF.
Despite the document's own title containing the word "آلية", the MOJ
portal's own legalType classification for this instrument is "لائحة"
(regulation), not "آلية" — hence law_component="regulation" per this
corpus's convention of following the portal's own classification rather
than the document's title word. Items are labeled with Arabic ordinal words
(أولاً..حادي عشر), not مادة-numbered; number_label_ar carries the portal's
own label verbatim. This PDF's raw text layer exhibits the known RTL
word-order glyph-extraction artifact seen elsewhere in this corpus (scores
low, mean ~0.40), but the 300dpi tesseract-ara OCR channel and the per-line
word-reversed text-layer channel together cleared 6 of 11 items outright
(1, 4, 6, 8, 10, 11); the other 5 (items 2, 3, 5, 7, 9) scored 0.8700-0.8867
— below floor mostly due to short item length amplifying minor OCR
list-numbering/digit artifacts (e.g. OCR misread "المادة (٩٦)" as "(17)" in
item 3) — and were visually adjudicated against the rendered PDF pages,
confirming verbatim match including the digits OCR had misread. This
regulation is IN FORCE. FRESH FULL ISSUANCE: all 11 اصلية (0 معدلة / 0 ملغاة
/ 0 مضافة). No source anomalies found. Implements the Criminal Procedure
Law's court-appointed-counsel provision (نظام الإجراءات الجزائية art 139,
already in this corpus as jza_law_art_139) via the Criminal Procedure
Regulation's arts 96/97 (already in this corpus as jza_reg_art_096/097),
whose own art 97 §3 names this instrument as the "آلية" it implements.

Articles are numbered by their ordinal position (1..11; no مكرر), flat
structure with no chapter/section wrapper (section_ar empty for every
article). No legal text is altered. Arabic governs; no translation/
paraphrase/interpretation. Read-only over input; deterministic over
outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "state_funded_lawyer", "regulation", "official_source",
                   "state_funded_lawyer_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "state_funded_lawyer", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "state_funded_lawyer_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "state_funded_lawyer_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "state_funded_lawyer_arabic_legal_llm",
                        "state_funded_lawyer_regulation_legal_llm_001_011.json")

LAW_ID = "sa-state-funded-lawyer-regulation-1439"
LAW_AR = "آلية الاستعانة بمحام على نفقة الدولة للمتهم في الجرائم الكبيرة"
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
KEY_RE = r"state_funded_lawyer_art_(\d{3})$"
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
        ver.append({"law_key": "state_funded_lawyer", "law_component": "regulation", "language": "ar",
                    "record_layer": "STATE_FUNDED_LAWYER_REGULATION_ARABIC_VERIFIED_TEXT",
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
                                              "against the official MOJ PDF (verbatim; 6 of 11 items "
                                              "matched the >=0.90 floor outright via the 300dpi "
                                              "tesseract-ara OCR channel or the per-line word-reversed "
                                              "PDF text-layer channel, the raw PDF text layer alone "
                                              "exhibiting the known RTL word-order glyph-extraction "
                                              "artifact seen elsewhere in this corpus and scoring low; "
                                              "mean 0.9216, min 0.8700; the remaining 5 items (2, 3, 5, "
                                              "7, 9) were read directly off the rendered 200dpi PDF "
                                              "pages as a direct visual cross-check and confirmed "
                                              "verbatim, including internal article cross-reference "
                                              "digits that the OCR channel had misread; all 11 items / "
                                              "both pages were visually read in full)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "record_id": "state-funded-lawyer-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "state_funded_lawyer/regulation/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["البند %s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s البند %s" % (LAW_AR, a["number_label_ar"]),
                                          "محام على نفقة الدولة %s" % a["number_label_ar"]],
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
    json.dump({"law_key": "state_funded_lawyer", "layer": "STATE_FUNDED_LAWYER_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": False,
               "visually_adjudicated": src["stats"]["visually_adjudicated"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-state-funded-lawyer-regulation-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (11 بنداً؛ إصدار جديد كامل: 11 أصلية)",
               "title_en": "Mechanism for a Defendant in Major/Serious Crimes to Seek Legal Counsel at the State's Expense — Arabic LLM-ready layer (11 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 11], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready State-Funded Lawyer Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
