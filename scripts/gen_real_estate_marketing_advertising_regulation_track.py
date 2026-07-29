#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Regulatory Bylaw on Real Estate Marketing and Advertising track
(اللائحة التنظيمية للتسويق والإعلانات العقارية), approved by the Board of
Directors of the Real Estate General Authority (REGA) by its own Resolution
No. (2/35/م26), dated 25/10/1447H = 13/4/2026G, implementing the Real Estate
Brokerage Law (Royal Decree No. M/130, dated 30/11/1443H) -- a VERY RECENT
instrument, one of the newest in this corpus.

VERIFICATION TIER -- see this track's own official_source.json for the full
account (verification_methodology_note / known_unresolved_discrepancies).
Summary:

TIER ASSESSED: TIER_1, per this corpus's own STATUS_TIER_MAP taxonomy
definition ("a primary PDF verified via an independent OCR/image pass of the
same document, no reachability gap"). PRIMARY SOURCE: rega.gov.sa (the
issuing authority itself) -- two independent pages on REGA's own domain were
reached this pass: (1) REGA's own dedicated regulation catalog page for this
Bylaw (fetched via WebFetch; a direct curl GET was blocked by the site's own
WAF/F5 edge protection, documented as a known_unresolved_discrepancy, not
silently worked around), confirming legislative status 'ساري' (in force,
NOT a draft), issue date 25/10/1447H, and publication date 14/11/1447H; and
(2) the actual Board Resolution PDF (and its annexed, approved Bylaw text)
linked directly from that same page, fetched via WebFetch and read in full.

ARTICLE TEXT -- INDEPENDENT VISUAL RE-EXTRACTION OF THE SAME PDF: this track
discovered that the PDF's own embedded text layer contains the same family of
systematic character-substitution corruption documented in this corpus's
sibling tracks (high_risk_professions_regulation, osh_service_providers_
regulation) for Microsoft-Word-exported Arabic PDFs (e.g. the Bylaw's own
title 'اللائحة' extracts corrupted as 'الالئحة'). NONE of the 12 article
texts were taken from that corrupted text layer: every one of the document's
8 pages was read as a rendered page image and independently transcribed by
direct visual reading of the displayed glyphs -- the "independent OCR /
rendered-page-image pass of the SAME official document" standard this corpus
uses elsewhere for Tier 1. The corrupted text layer was used only to
roughly navigate article boundaries, never as a source of final wording.

DRAFT-VS-ENACTED CHECK: istitlaa.ncc.gov.sa carries this Bylaw's PRIOR
public-consultation DRAFT page -- located via search this pass but
deliberately never fetched or used, per this task's explicit instruction to
exclude draft-consultation platforms. This track's text rests exclusively on
REGA's own post-approval regulation catalog page (marked 'ساري') and its
attached, approved Board Resolution PDF.

SECONDARY / PRESS CORROBORATION (structure and key provisions only, never
the source of Arabic wording): Saudi Press Agency/SPA, Argaam, Okaz, Amlak,
Eye of Riyadh, LexisNexis Middle East, and Gulf Construction Online all
independently corroborate the 12-article count, the M/130 decree basis, the
~1-2 May 2026 effective date, the 8 mandatory advertisement disclosures, the
independent-license requirement, and the full channel scope -- but none
publish the full verbatim article text, so none served as a wording source.

GAP NOT CLOSED THIS PASS: no direct Umm Al-Qura Gazette (uqn.gov.sa) page
for this specific Bylaw could be located via search this pass (unlike this
corpus's high_risk_professions_regulation and osh_service_providers_
regulation tracks, which both found and used a direct uqn.gov.sa entry).
Disclosed honestly in known_unresolved_discrepancies rather than silently
omitted.

12 articles, no chapter (فصل) subdivisions in the official document at all
(chapter_structure is an empty list, matching this corpus's convention for
chapterless regulations e.g. anti_smoking_regulation). All 12 are اصلية
(first, single, only edition; no subsequent amendment found this pass; the
Bylaw itself repeals two named prior Board Resolutions per its own Article
11). No article carries a distinct title beyond "المادة <ordinal>:" in the
source, so article_title_ar is left as an empty string throughout, matching
this corpus's convention for sibling tracks whose source does the same.

Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "real_estate_marketing_advertising_regulation", "law",
                   "official_source",
                   "real_estate_marketing_advertising_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "real_estate_marketing_advertising_regulation", "law",
                       "verified")
RECORDS = os.path.join(OUT_VER, "real_estate_marketing_advertising_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "real_estate_marketing_advertising_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "real_estate_marketing_advertising_regulation_arabic_legal_llm",
                        "real_estate_marketing_advertising_regulation_legal_llm_001_012.json")

LAW_ID = "sa-real-estate-marketing-advertising-regulation-1447"
LAW_AR = "اللائحة التنظيمية للتسويق والإعلانات العقارية"
STATUS = "REGA_BOARD_RESOLUTION_PDF_PRIMARY_VISUAL_REEXTRACTION_PRESS_CORROBORATED"
KEY_RE = r"real_estate_marketing_advertising_regulation_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم الهيئة المرخص المعلن").split())


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
        ver.append({"law_key": "real_estate_marketing_advertising_regulation",
                    "law_component": "regulation", "language": "ar",
                    "record_layer": "REAL_ESTATE_MARKETING_ADVERTISING_REGULATION_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; PRIMARY source is REGA's own "
                                              "official regulation catalog page (rega.gov.sa) "
                                              "and the Board Resolution PDF attached to it "
                                              "(rega.gov.sa/media/1ldhhazk/...), the issuing "
                                              "authority's own site -- two independent pages on "
                                              "the same official domain. This article's own text "
                                              "was independently re-extracted by direct visual "
                                              "reading of a rendered page image of the SAME "
                                              "official PDF, NOT from that PDF's own corrupted "
                                              "text layer (which silently substitutes certain "
                                              "Arabic letter pairs -- see "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track's text)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": label,
                    "section_ar": section,
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": is_amended, "is_added": ls == "مضافة",
                    "record_id": "real-estate-marketing-advertising-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, label),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, label),
                    "article_path": "real_estate_marketing_advertising_regulation/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "%s من اللائحة التنظيمية للتسويق والإعلانات العقارية"
                                          % a["number_label_ar"]],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("REGA Board of Directors Resolution No. "
                                                          "(2/35/m26), dated 25/10/1447H = "
                                                          "13/4/2026G -- cross-verified via "
                                                          "REGA's own regulation catalog page "
                                                          "(rega.gov.sa) and the Board Resolution "
                                                          "PDF attached to it"),
                                     "source_authority_ar": ("قرار مجلس إدارة الهيئة العامة للعقار "
                                                            "رقم (2/35/م26) وتاريخ 25/10/1447هـ "
                                                            "الموافق 13/4/2026م -- تم التحقق عبر "
                                                            "صفحة اللائحة الرسمية على rega.gov.sa "
                                                            "وملف قرار مجلس الإدارة المرفق بها"),
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "real_estate_marketing_advertising_regulation",
               "layer": "REAL_ESTATE_MARKETING_ADVERTISING_REGULATION_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-real-estate-marketing-advertising-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (12 مادة، "
                           "اصلية جميعها)",
               "title_en": ("Regulatory Bylaw on Real Estate Marketing and Advertising — Arabic "
                            "LLM-ready layer (12 records, all original/اصلية)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 12], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Real Estate Marketing/Advertising Regulation records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
