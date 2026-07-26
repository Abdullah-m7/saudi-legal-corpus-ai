#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Debt Collection Regulations and Procedures track (ضوابط
وإجراءات التحصيل, SAMA Circular No. 106889333, dated 6/9/1446H = 6/3/2025G).

Standalone SAMA instrument governing debt-collection communication and
procedures for financing entities (banks and SAMA-supervised finance
companies) and third parties acting on their behalf -- CONFIRMED DISTINCT
from this corpus's already-ingested finance_companies_regulation track (the
Implementing Regulation of the Finance Companies Control Law): that track's
own Article 96 (الباب العشرون: تحصيل الديون) only governs a finance
company's outsourcing of collection tasks to a third party, and explicitly
cross-references THIS present instrument by name as an external minimum
standard ("ما جاء في ضوابط وإجراءات التحصيل الصادرة عن البنك") -- read
directly from finance_companies_regulation's own already-ingested text, not
assumed.

VERIFICATION TIER -- see debt_collection_regulation_official_source.json's
verification_methodology_note for the full account. Summary:

PRIMARY SOURCE: rulebook.sama.gov.sa (SAMA's own official Rulebook portal),
Arabic full-text 'entiresection' view (https://rulebook.sama.gov.sa/ar/
entiresection/10400, HTTP 200, fetched directly via curl, born-digital
structured HTML -- no OCR needed). Arabic governs; the equivalent English
entiresection view was fetched and used ONLY for structural cross-
verification (chapter/article count and titles), never as a source of
Arabic wording.

5 chapters (الفصول), 11 articles (المواد) -- matching this track's
commissioning brief and independently confirmed by both the Arabic and
English entiresection views. Chapter Five ('أحكام ختامية' / Final
Provisions) carries NO numbered article of its own on the source page (in
either language) -- its own unnumbered closing text (including the explicit
supersession statement) is preserved verbatim in this track's own
'closing_provisions_ar' field, NOT fabricated into a 12th article.

PREDECESSOR ('FIRST EDITION'): Chapter Five's own text states this edition
supersedes 'ضوابط وإجراءات التحصيل للعملاء الأفراد (الإصدار الأول)' --
independently confirmed as a genuine, distinct predecessor circular (No.
391000083340, dated 26/7/1439H = 11/4/2018G) via that predecessor's OWN
rulebook.sama.gov.sa page, marked 'No longer applicable' and itself stating
it was replaced by Circular 106889333. The predecessor is NOT ingested here
(supersession graph is out of scope for this track per its own
commissioning instructions) -- documented for context only.

All 11 articles are اصلية (single, first-and-only-confirmed edition since
6/3/2025; no subsequent amendment to this text identified this pass). No
legal text is altered. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "debt_collection_regulation", "law", "official_source",
                   "debt_collection_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "debt_collection_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "debt_collection_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "debt_collection_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "debt_collection_regulation_arabic_legal_llm",
                        "debt_collection_regulation_legal_llm_001_011.json")

LAW_ID = "sa-debt-collection-regulation-106889333-1446"
LAW_AR = "ضوابط وإجراءات التحصيل"
STATUS = "SAMA_RULEBOOK_PRIMARY_AR_EN_BILINGUAL_HTML_CROSS_VERIFIED"
KEY_RE = r"debt_collection_regulation_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة الضوابط أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم جهات التمويل العميل").split())


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
        label = a["number_label_ar"] + ((": " + title) if title else "")
        ver.append({"law_key": "debt_collection_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "DEBT_COLLECTION_REGULATION_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; PRIMARY source is "
                                              "rulebook.sama.gov.sa (SAMA's own official "
                                              "Rulebook portal), Arabic 'entiresection' "
                                              "full-text view (node 10400), HTTP 200, "
                                              "born-digital structured HTML (no OCR). "
                                              "Cross-checked structurally (chapter/article "
                                              "count and titles) against the equivalent "
                                              "English entiresection view -- English was "
                                              "NEVER used as a source of Arabic wording. "
                                              "See verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track's text "
                                              "-- in particular Chapter Five's unnumbered "
                                              "closing text (preserved separately, not "
                                              "fabricated as a 12th article) and the "
                                              "confirmed, distinct, un-ingested 2018 first "
                                              "edition this track supersedes."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": label,
                    "section_ar": section,
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": is_amended, "is_added": ls == "مضافة",
                    "record_id": "debt-collection-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, label),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, label),
                    "article_path": "debt_collection_regulation/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "%s من ضوابط وإجراءات التحصيل" % a["number_label_ar"]],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("SAMA Circular No. 106889333, "
                                                          "dated 6/9/1446H = 6/3/2025G -- "
                                                          "rulebook.sama.gov.sa (issuing "
                                                          "Authority's own site); supersedes "
                                                          "the confirmed, distinct 2018 First "
                                                          "Edition (Circular No. "
                                                          "391000083340, 26/7/1439H)"),
                                     "source_authority_ar": ("تعميم البنك المركزي السعودي "
                                                            "رقم (106889333) وتاريخ "
                                                            "6/9/1446هـ الموافق 6/3/2025م — "
                                                            "الموقع الرسمي لبوابة SAMA "
                                                            "Rulebook (rulebook.sama.gov.sa)؛ "
                                                            "حلت محل الإصدار الأول (تعميم "
                                                            "391000083340، 26/7/1439هـ)"),
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "debt_collection_regulation",
               "layer": "DEBT_COLLECTION_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "decree_date_gregorian": src.get("decree_date_gregorian"),
               "administering_authority_en": src.get("administering_authority_en"),
               "consolidated_amended_law": False,
               "chapter_structure": src["chapter_structure"],
               "closing_provisions_ar": src.get("closing_provisions_ar"),
               "amendment_history": src.get("amendment_history"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-debt-collection-regulation-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (11 مادة، اصلية جميعها)",
               "title_en": ("Debt Collection Regulations and Procedures — Arabic "
                            "LLM-ready layer (11 records, all original/اصلية)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 11], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Debt Collection Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
