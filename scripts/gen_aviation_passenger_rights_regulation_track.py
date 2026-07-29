#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Passenger Rights Protection Regulation track
(لائحة حماية حقوق المسافرين), issued by the Board of Directors of the
General Authority of Civil Aviation (GACA) per Resolution No. (574/36) dated
18/11/1444H (= 7/6/2023G), and published in the Umm Al-Qura Official Gazette
(uqn.gov.sa), Issue No. 4995, dated 9 Safar 1445H = 25 August 2023G.

VERIFICATION TIER -- see this track's own official_source.json for the full
account (verification_methodology_note / known_unresolved_discrepancies).
Summary:

TIER: TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED. The Umm Al-Qura Official
Gazette portal (uqn.gov.sa/details?p=23521) was fetched directly this pass
(HTTP 200) and reproduces the Regulation's FULL running text as born-digital
HTML -- used as the governing text for all 30 articles. GACA's own site
(gaca.gov.sa, three candidate URLs) was confirmed UNREACHABLE this pass (TLS
connection reset / 503 on every attempt, via both curl and WebFetch).
Cross-checked against qanoonsa.com/p/499513/ (full running text, word-for-
word substantively identical) and aunklaw.com/17-4/ (structural/decision-
number corroboration), plus a third-party-hosted copy of the born-digital
PDF at c.ekstatic.net (structural cross-check only -- its own text layer has
the same Word-export 'لا'-ligature-reversal bug documented elsewhere in this
corpus, so it was never used as a wording source).

30 articles across 3 أبواب (NOT فصول -- this Regulation's own top-level
divisions are genuinely titled الباب), all اصلية (single, first-and-only
edition; no amendment found this pass). This track's own commissioning
brief's "expected article count: 62" figure was checked, not assumed, and
corrected to the actual, source-confirmed count of 30 -- see
known_unresolved_discrepancies in the source artifact.

Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "aviation_passenger_rights_regulation", "law",
                   "official_source", "aviation_passenger_rights_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "aviation_passenger_rights_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "aviation_passenger_rights_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "aviation_passenger_rights_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "aviation_passenger_rights_regulation_arabic_legal_llm",
                        "aviation_passenger_rights_regulation_legal_llm_001_030.json")

LAW_ID = "sa-aviation-passenger-rights-regulation-1444"
LAW_AR = "لائحة حماية حقوق المسافرين"
STATUS = ("UQN_GAZETTE_OFFICIAL_PRIMARY_X_QANOONSA_FULLTEXT_X_AUNKLAW_STRUCTURAL_"
          "CROSS_VERIFIED_GACA_GOV_SA_UNREACHABLE")
KEY_RE = r"aviation_passenger_rights_regulation_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم الناقل الجوي المسافر").split())


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
        ver.append({"law_key": "aviation_passenger_rights_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "AVIATION_PASSENGER_RIGHTS_REGULATION_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; PRIMARY source is the Umm "
                                              "Al-Qura Official Gazette portal (uqn.gov.sa, "
                                              "entry details?p=23521), a government-operated "
                                              "portal separate from GACA, reproducing the "
                                              "Regulation's full running text as born-digital "
                                              "HTML. GACA's own site (gaca.gov.sa) was "
                                              "confirmed unreachable this pass. Cross-checked "
                                              "against qanoonsa.com (full text, word-for-word "
                                              "substantively identical) and aunklaw.com "
                                              "(structural/decision-number corroboration) -- "
                                              "see verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track's text."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": label,
                    "section_ar": section,
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": is_amended, "is_added": ls == "مضافة",
                    "record_id": "aviation-passenger-rights-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, label),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, label),
                    "article_path": "aviation_passenger_rights_regulation/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "%s من لائحة حماية حقوق المسافرين"
                                          % a["number_label_ar"]],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("GACA Board of Directors "
                                                          "Resolution No. (574/36) dated "
                                                          "18/11/1444H approving the "
                                                          "Regulation -- cross-verified via "
                                                          "the Umm Al-Qura Official Gazette "
                                                          "(uqn.gov.sa, entry p=23521, Issue "
                                                          "No. 4995, dateline 9/2/1445H = "
                                                          "25/8/2023G) as the reached primary "
                                                          "source; GACA's own site "
                                                          "(gaca.gov.sa) was unreachable this "
                                                          "pass"),
                                     "source_authority_ar": ("قرار مجلس إدارة الهيئة العامة "
                                                            "للطيران المدني رقم (574/36) "
                                                            "وتاريخ 18/11/1444هـ باعتماد "
                                                            "اللائحة -- تم التحقق عبر جريدة "
                                                            "أم القرى الرسمية (uqn.gov.sa، "
                                                            "p=23521، العدد 4995، بتاريخ "
                                                            "9/2/1445هـ الموافق 25/8/2023م) "
                                                            "بوصفها المصدر الرسمي الذي تم "
                                                            "الوصول إليه فعلياً؛ تعذّر "
                                                            "الوصول إلى موقع الهيئة ذاته "
                                                            "(gaca.gov.sa) هذه الجولة"),
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "aviation_passenger_rights_regulation",
               "layer": "AVIATION_PASSENGER_RIGHTS_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "decree_date_gregorian": src.get("decree_date_gregorian"),
               "administering_authority_en": src.get("administering_authority_en"),
               "consolidated_amended_law": False,
               "chapter_structure": src["chapter_structure"],
               "gazette_publication": src.get("gazette_publication"),
               "amendment_history": src.get("amendment_history"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-aviation-passenger-rights-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (30 مادة، "
                           "اصلية جميعها)",
               "title_en": ("Passenger Rights Protection Regulation — Arabic LLM-ready layer "
                            "(30 records, all original/اصلية)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 30], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Aviation Passenger Rights Regulation records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
