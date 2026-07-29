#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Regulation of Real Estate Auctions track (اللائحة التنظيمية
للمزادات العقارية, issued by a Resolution of the Board of Directors of the
General Authority for Real Estate / REGA, dated 01/12/1444H = 19/06/2023G,
published in full in the Umm Al-Qura Official Gazette on 09/02/1445H =
25/08/2023G). The regulation is issued pursuant to the Implementing Regulation
of the Real Estate Brokerage Law and, through it, the Real Estate Brokerage
Law itself (Royal Decree No. م/130 dated 30/11/1443H, based on Council of
Ministers Resolution No. 679 dated 29/11/1443H) -- both already tracked
independently in this corpus (sources/real_estate_brokerage,
sources/real_estate_brokerage_regulation) and NOT touched by this generator.

VERIFICATION TIER -- see real_estate_auctions_regulation_official_source.json's
own verification_methodology_note for the full account. Summary:

DUAL PRIMARY SOURCES, ALL 12 ARTICLES: uqn.gov.sa (Umm Al-Qura Official
Gazette, the constitutionally designated publication organ) and rega.gov.sa
(the issuing authority's own official regulatory site) were BOTH reached
directly this pass (HTTP 200, fetched via curl/urllib, not through a
summarizing tool) and BOTH reproduce the regulation's full 12-article text
with no reachability gap. A full programmatic diff (after normalizing purely
cosmetic tashkeel/dash/colon-placement differences caused by each site's own
HTML rendering) found 10 of 12 articles byte-identical, with a small
phrase-level wording variance in Article 2 item 5 and Article 10 item 1 (see
known_unresolved_discrepancies). Per this corpus's convention, the Official
Gazette (uqn.gov.sa) text governs for those two articles. Secondary
corroboration on article count (12) and legal content came from argaam.com and
aleqt.com ("الاقتصادية", a mainstream Saudi business newspaper).

No board-resolution number was located for this specific regulation on any
source checked this pass (unlike its sibling Implementing Regulation, decree
132/ق) -- disclosed as an honest gap, not filled with an invented number.

This regulation uses no formal numbered "الفصل" chapters in its own official
text (unlike its sibling Implementing Regulation and
osh_service_providers_regulation) -- only short un-numbered topical section
headers, reproduced verbatim in chapter_structure with an empty label_ar.

All 12 articles are اصلية (single, first-and-only-confirmed edition since
25/08/2023; no subsequent amendment identified this pass). No legal text is
altered. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "real_estate_auctions_regulation", "law", "official_source",
                   "real_estate_auctions_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "real_estate_auctions_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "real_estate_auctions_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "real_estate_auctions_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "real_estate_auctions_regulation_arabic_legal_llm",
                        "real_estate_auctions_regulation_legal_llm_001_012.json")

LAW_ID = "sa-real-estate-auctions-regulation-1444"
LAW_AR = "اللائحة التنظيمية للمزادات العقارية"
KEY_RE = r"real_estate_auctions_regulation_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم الهيئة المرخص المزاد العقاري العقارية").split())


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
        status = a["status"]
        source_tier = a.get("source_tier")
        rega_check = a.get("rega_site_cross_check")
        ver.append({"law_key": "real_estate_auctions_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "REAL_ESTATE_AUCTIONS_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "article_title_ar": title,
                    "section_ar": section,
                    "article_text_verified": text,
                    "verification_status": status,
                    "source_tier": source_tier,
                    "rega_site_cross_check": rega_check,
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": is_amended,
                    "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "official_text_status": status,
                    "governing_source_note": ("Arabic governs. Verbatim text taken from "
                                              "uqn.gov.sa (Umm Al-Qura Official Gazette), the "
                                              "constitutionally designated publication organ, "
                                              "cross-verified in full against rega.gov.sa "
                                              "(the issuing authority's own official site). "
                                              "10 of 12 articles are byte-identical between "
                                              "the two primary sources after normalizing "
                                              "cosmetic HTML-rendering differences; this "
                                              "article's own rega_site_cross_check field "
                                              "records whether a small documented wording "
                                              "variance exists (Articles 2 and 10 only) -- see "
                                              "verification_methodology_note and "
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
                    "record_id": "real-estate-auctions-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, label),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, label),
                    "article_path": "real_estate_auctions_regulation/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "%s من اللائحة التنظيمية للمزادات العقارية"
                                          % a["number_label_ar"]],
                    "text_status": status,
                    "source_trust": {"source_authority": ("Resolution of the Board of Directors "
                                                          "of the General Authority for Real "
                                                          "Estate (REGA), dated 01/12/1444H = "
                                                          "19/06/2023G (Gregorian calculated, "
                                                          "not stated verbatim in any source "
                                                          "found) -- published in full in Umm "
                                                          "Al-Qura Official Gazette, 09/02/1445H "
                                                          "= 25/08/2023G. No board-resolution "
                                                          "number was located for this "
                                                          "instrument this pass. This article: "
                                                          "verbatim from uqn.gov.sa (Umm Al-Qura "
                                                          "Official Gazette), cross-verified "
                                                          "against rega.gov.sa (REGA's own "
                                                          "site)" + (" -- small documented "
                                                          "wording variance on rega.gov.sa, "
                                                          "Gazette text adopted as governing"
                                                          if rega_check ==
                                                          "MINOR_WORDING_VARIANCE_DOCUMENTED"
                                                          else ", byte-identical")),
                                     "source_authority_ar": ("قرار مجلس إدارة الهيئة العامة "
                                                            "للعقار (REGA)، بتاريخ 01/12/1444هـ "
                                                            "الموافق 19/06/2023م (تاريخ محسوب "
                                                            "تقويمياً) — منشورة كاملة في جريدة "
                                                            "أم القرى الرسمية بتاريخ 09/02/1445هـ "
                                                            "الموافق 25/08/2023م. لم يُعثر على "
                                                            "رقم قرار مجلس الإدارة هذه الجولة. "
                                                            "هذه المادة: نص حرفي من جريدة أم "
                                                            "القرى (uqn.gov.sa)، مقاطع مع نص "
                                                            "موقع الهيئة الرسمي (rega.gov.sa)"
                                                            + (" — بفارق صياغة طفيف موثّق على "
                                                               "موقع الهيئة، واعتُمد نص الجريدة "
                                                               "الرسمية كنص حاكم"
                                                               if rega_check ==
                                                               "MINOR_WORDING_VARIANCE_DOCUMENTED"
                                                               else "، مطابق حرفياً")),
                                     "source_status": status.lower(),
                                     "source_tier": source_tier,
                                     "rega_site_cross_check": rega_check,
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": status},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "real_estate_auctions_regulation",
               "layer": "REAL_ESTATE_AUCTIONS_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "source_tier_counts": src.get("source_tier_counts"),
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
    json.dump({"layer_id": "sa-real-estate-auctions-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (12 مادة، اصلية جميعها)",
               "title_en": ("Regulation of Real Estate Auctions — Arabic LLM-ready layer "
                            "(12 records, all original/اصلية)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 12], "consolidated_amended_law": False,
               "status_counts": src["status_counts"],
               "source_tier_counts": src.get("source_tier_counts"),
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Real Estate Auctions Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
