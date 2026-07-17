#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Cooperative Insurance Companies Control Law track (نظام
مراقبة شركات التأمين التعاوني, Royal Decree M/32, 2/6/1424H).

DISTINCT VERIFICATION TIER — laws.boe.gov.sa and the Wayback Machine were
both unreachable this research pass. Full current-consolidated text
instead rests on misa.gov.sa's official bilingual PDF (explicitly
headering all three decrees: M/32 original, M/30 and M/12 amendments),
cross-verified article-by-article against nezams.com's raw HTML
transcription. For the 17 unamended articles, this track follows
nezams.com's wording (pre-2020 regulator name «مؤسسة النقد العربي
السعودي») rather than misa.gov.sa's (current name throughout) — a
documented, flagged discrepancy, not silently normalized.

See sources/insurance_control/law/official_source/
insurance_control_law_official_source.json for the full methodology note
and all documented unresolved discrepancies, including the IMPORTANT
LIMITATION that pre-amendment original text for 6 of the 8 amended
articles (2, 3, 6, 18, 19, 20) was located by the research pass but not
transcribed into this build, and for 2 further articles (21, 22) was not
even located — no original_text fields are fabricated for any of them.

25 records, no chapters: 17 اصلية / 8 معدلة (two amendment waves: M/30,
27/5/1434H, touching article 22 and first-amending article 20; M/12,
23/1/1443H, touching articles 2, 3, 6, 18, 19, 21, and second-amending
article 20).

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "insurance_control", "law", "official_source",
                   "insurance_control_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "insurance_control", "law", "verified")
RECORDS = os.path.join(OUT_VER, "insurance_control_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "insurance_control_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "insurance_control_arabic_legal_llm",
                        "insurance_control_law_legal_llm_001_025.json")

LAW_ID = "sa-insurance-control-law-m32-1424"
LAW_AR = "نظام مراقبة شركات التأمين التعاوني"
STATUS = "MISA_OFFICIAL_PDF_X_NEZAMS_CROSS_VERIFIED_BOE_UNREACHABLE"
KEY_RE = r"insurance_control_art_(\d{3})$"
AMENDED_KEYS = {"insurance_control_art_%03d" % n for n in (2, 3, 6, 18, 19, 20, 21, 22)}
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
        ver.append({"law_key": "insurance_control", "law_component": "law", "language": "ar",
                    "record_layer": "INSURANCE_CONTROL_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": is_amended, "is_added": False,
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track uses a distinct "
                                              "verification tier — misa.gov.sa's official "
                                              "bilingual PDF (headering all three decrees), "
                                              "cross-verified against nezams.com, because "
                                              "laws.boe.gov.sa and the Wayback Machine were "
                                              "both unreachable this research pass — see "
                                              "verification_methodology_note in the source "
                                              "artifact for the full caveat, including the "
                                              "limitation that pre-amendment original text is "
                                              "NOT included for any of the 8 amended articles "
                                              "this pass."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": is_amended, "is_added": False,
                    "record_id": "insurance-control-law-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "insurance_control/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام مراقبة شركات التأمين التعاوني" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Decree — misa.gov.sa "
                                                          "official bilingual PDF x "
                                                          "nezams.com cross-verified, "
                                                          "laws.boe.gov.sa unreachable"),
                                     "source_authority_ar": "مرسوم ملكي — ملف PDF رسمي من وزارة الاستثمار مطابق مع نزامز.كوم (بوابة هيئة الخبراء غير متاحة)",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "insurance_control",
               "layer": "INSURANCE_CONTROL_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-insurance-control-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (25 مادة؛ نص موحّد: 17 أصلية، 8 معدّلة)",
               "title_en": "Saudi Cooperative Insurance Companies Control Law — Arabic LLM-ready layer (25 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 25], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Insurance Control Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
