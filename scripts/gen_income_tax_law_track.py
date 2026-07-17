#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Income Tax Law track (نظام ضريبة الدخل, Royal Decree M/1,
15/1/1425H).

DISTINCT VERIFICATION TIER — current-consolidated text rests on FOUR
sources checked this pass, with cross-verification achieved for every one
of the 81 articles from at least two independent sources in agreement
(BOE via Wayback + nezams.com at minimum), and the large majority also
cross-checked against ZATCA's own official consolidated PDF and/or
gstc.gov.sa's older PDF (3-4-source agreement). IMPORTANT LIMITATION —
Chapter 10 (Articles 44-55, the Natural Gas Investment Tax chapter, fully
replaced by Royal Decree M/70, 11/7/1439H): BOTH government-authority PDF
sources (ZATCA and gstc.gov.sa) print only a bare repeal notice for this
entire 12-article chapter, omitting the substantive replacement text —
the mirror image of this corpus's VAT-law-track finding. The full current
text for Articles 44-55 rests on TWO sources only (BOE via Wayback,
cross-verified word-for-word against nezams.com), not the usual 3-4.

See sources/income_tax/law/official_source/
income_tax_law_official_source.json for the full methodology note and all
14 documented unresolved discrepancies, including the IMPORTANT LIMITATION
that NO original_1425h_text field is populated for ANY article this pass —
the research report described having seen pre-amendment "before" text for
six articles but never transcribed it verbatim into deliverable form, and
Chapter 10's pre-1425h-replacement text is independently confirmed
unrecoverable from any of the four sources checked. No original text is
fabricated to fill either gap.

81 records, 16 chapters (فصول): 52 اصلية / 29 معدلة (10 individually
confirmed via BOE's own "changed" flag and/or explicit report annotation:
1, 2, 6, 7, 8, 21, 56, 59, 66, 67; 12 from Chapter 10's full M/70
replacement: 44-55; 7 lower-confidence articles marked معدلة on ZATCA
footnote/ledger evidence alone with no clause-level effect ever stated in
the report: 9, 12, 13, 17, 43, 63, 65). Article 66 carries a documented,
unresolved dual-date conflict for Royal Decree M/52 (28/4/1441H per ZATCA
vs 28/7/1441H per BOE) — both dates are recorded in its history entry.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "income_tax", "law", "official_source",
                   "income_tax_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "income_tax", "law", "verified")
RECORDS = os.path.join(OUT_VER, "income_tax_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "income_tax_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "income_tax_arabic_legal_llm",
                        "income_tax_law_legal_llm_001_081.json")

LAW_ID = "sa-income-tax-law-m1-1425"
LAW_AR = "نظام ضريبة الدخل"
STATUS = "BOE_WAYBACK_X_ZATCA_PDF_X_GSTC_PDF_X_NEZAMS_CROSS_VERIFIED_CH10_BOE_ONLY"
KEY_RE = r"income_tax_art_(\d{3})$"
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
        is_amended = ls == "معدلة"
        text = a["text"]
        ver.append({"law_key": "income_tax", "law_component": "law", "language": "ar",
                    "record_layer": "INCOME_TAX_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": is_amended, "is_added": False,
                    "amendment_history": a.get("history"),
                    "original_1425h_text": a.get("original_1425h_text"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track uses a distinct "
                                              "verification tier — BOE (via Wayback) x "
                                              "ZATCA official PDF x gstc.gov.sa PDF x "
                                              "nezams.com cross-verified for 69 of 81 "
                                              "articles, but Chapter 10 (Articles 44-55) "
                                              "rests on BOE + nezams.com only (2 sources) "
                                              "since ZATCA's and gstc's PDFs both print a "
                                              "bare repeal notice for that entire chapter "
                                              "— see verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact for the full caveats, including that "
                                              "no original_1425h_text is populated for any "
                                              "article this pass and that Article 66 carries "
                                              "an unresolved dual-date conflict for Royal "
                                              "Decree M/52."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": is_amended, "is_added": False,
                    "record_id": "income-tax-law-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "income_tax/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام ضريبة الدخل" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Decree — BOE (Wayback) x "
                                                          "ZATCA official PDF x gstc.gov.sa "
                                                          "PDF x nezams.com cross-verified; "
                                                          "Chapter 10 (Arts. 44-55) BOE + "
                                                          "nezams.com only"),
                                     "source_authority_ar": "مرسوم ملكي — بوابة هيئة الخبراء (عبر أرشيف Wayback) مطابقة مع ملف PDF الرسمي لهيئة الزكاة والضريبة والجمارك (ZATCA) وملف gstc.gov.sa وموقع nezams.com؛ الفصل العاشر (المواد 44-55) عبر بوابة هيئة الخبراء وnezams.com فقط",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "income_tax",
               "layer": "INCOME_TAX_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-income-tax-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (81 مادة؛ نص موحّد: 52 أصلية، 29 معدّلة)",
               "title_en": "Saudi Income Tax Law — Arabic LLM-ready layer (81 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 81], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Income Tax Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
