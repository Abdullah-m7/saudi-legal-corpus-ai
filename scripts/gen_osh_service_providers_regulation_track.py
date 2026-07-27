#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the OSH Service Providers Licensing/Accreditation Regulation track
(لائحة ترخيص واعتماد مزاولي ومقدمي خدمات السلامة والصحة المهنية, Ministerial
Decision No. 64764, dated 13/5/1447H = 4/11/2025G, issued by the Minister of
Human Resources and Social Development in his capacity as Chairman of the
National Committee for Occupational Safety and Health / NCOSH -- published in
full in Umm Al-Qura Official Gazette Issue No. 5138, dated 20/7/1447H =
9/1/2026G).

A sibling instrument, the Regulation of Work in High-Risk Professions
(Ministerial Decision No. 64762, same date/Council meeting), was issued the
same day under an adjacent decision number. That sibling is a WHOLLY SEPARATE
regulation tracked independently elsewhere in this corpus -- this generator
does not touch its track_id or files.

VERIFICATION TIER -- see osh_service_providers_regulation_official_source.json's
own verification_methodology_note for the full account. Summary:

PRIMARY SOURCE (Articles 1-29 only): uqn.gov.sa (Umm Al-Qura Official Gazette,
the issuing authority's own site), the regulation's own dedicated page
(https://uqn.gov.sa/details?p=28770, HTTP 200, fetched directly via curl,
born-digital structured HTML -- no OCR needed). Parsed with BeautifulSoup in
document order; Word-pasted <table> markup (Articles 18-19) was converted
row-by-row into prose, never naive tag-stripped. The page's own
#article-content element reproduces the preamble and Articles 1-29 in full
(Chapters 1-5) but its own HTML markup ends immediately after Article 29 --an
unexplained CMS rendering gap on the government's own page for this specific
document, not a scope decision by this track.

SECONDARY SOURCES: qanoonsa.com (https://qanoonsa.com/p/513807/) reproduces
the FULL 38-article/6-chapter text; a full programmatic diff against
uqn.gov.sa's own text for Articles 1-29 found ZERO substantive wording
differences (only cosmetic tashkeel-stripping and slash-spacing convention
differences). ajel.sa (https://ajel.sa/local/d3rdg2bnfo) independently quotes
the decree's own preamble/operative text and Articles 1-17 verbatim, matching
both other sources. Lexis Middle East independently confirms the 38-article/
6-chapter structure (chapter-to-article-range boundaries matching exactly),
though only via a WebFetch-tool-mediated read (a direct curl GET of its own
page returned HTTP 404 this pass).

PER-ARTICLE CONFIDENCE SPLIT: Articles 1-29 carry status
UQN_GAZETTE_OFFICIAL_PRIMARY_TEXT_AR_CROSS_VERIFIED_AJEL_QANOONSA (source_tier
"primary"); Articles 30-38 (9 of 38) carry status
QANOONSA_SECONDARY_TEXT_UQN_PRIMARY_PAGE_TRUNCATED_STRUCTURALLY_XVERIFIED_LEXIS
(source_tier "secondary_only") since uqn.gov.sa's own page did not reach that
far this pass. See known_unresolved_discrepancies in the source artifact for
every non-obvious judgment call in this build (the Article 18 duplicate-table
exclusion, the Article 19 genuine last-row content gap, argaam.com's
inconsistent 29-article/5-chapter undercount, the istitlaa.ncc.gov.sa
unreachable draft-consultation page, the calculated Gregorian decree date,
etc.) before relying on this track's text.

All 38 articles are اصلية (single, first-and-only-confirmed edition since
4/11/2025; no subsequent amendment to this text identified this pass). No
legal text is altered. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "osh_service_providers_regulation", "law", "official_source",
                   "osh_service_providers_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "osh_service_providers_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "osh_service_providers_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "osh_service_providers_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "osh_service_providers_regulation_arabic_legal_llm",
                        "osh_service_providers_regulation_legal_llm_001_038.json")

LAW_ID = "sa-osh-service-providers-regulation-64764-1447"
LAW_AR = "لائحة ترخيص واعتماد مزاولي ومقدمي خدمات السلامة والصحة المهنية"
KEY_RE = r"osh_service_providers_regulation_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم المجلس الترخيص الاعتماد").split())


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
        ver.append({"law_key": "osh_service_providers_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "OSH_SERVICE_PROVIDERS_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "article_title_ar": title,
                    "section_ar": section,
                    "article_text_verified": text,
                    "verification_status": status,
                    "source_tier": source_tier,
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": is_amended,
                    "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "official_text_status": status,
                    "governing_source_note": ("Arabic governs. Articles 1-29: taken verbatim "
                                              "from uqn.gov.sa (Umm Al-Qura Official Gazette, "
                                              "the issuing authority's own site), cross-verified "
                                              "against ajel.sa and qanoonsa.com with zero "
                                              "substantive divergence found. Articles 30-38: "
                                              "uqn.gov.sa's own page did not reach this far this "
                                              "pass -- text taken from qanoonsa.com only, "
                                              "structurally (not verbatim) cross-verified via "
                                              "Lexis Middle East's independent chapter/article-"
                                              "range count. See verification_methodology_note "
                                              "and known_unresolved_discrepancies in the source "
                                              "artifact -- in particular the Article 18 "
                                              "duplicate-table exclusion and the Article 19 "
                                              "genuine last-row content gap -- before relying on "
                                              "this track's text."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": label,
                    "section_ar": section,
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": is_amended, "is_added": ls == "مضافة",
                    "record_id": "osh-service-providers-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, label),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, label),
                    "article_path": "osh_service_providers_regulation/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "%s من لائحة ترخيص واعتماد مزاولي ومقدمي خدمات السلامة والصحة المهنية"
                                          % a["number_label_ar"]],
                    "text_status": status,
                    "source_trust": {"source_authority": ("Ministerial Decision (Minister of "
                                                          "HRSD, Chairman of NCOSH) No. 64764, "
                                                          "dated 13/5/1447H = 4/11/2025G -- "
                                                          "published in full in Umm Al-Qura "
                                                          "Official Gazette Issue No. 5138, "
                                                          "20/7/1447H = 9/1/2026G. This article: "
                                                          + ("uqn.gov.sa primary text"
                                                             if source_tier == "primary"
                                                             else "qanoonsa.com secondary text "
                                                                  "(uqn.gov.sa's own page did not "
                                                                  "reach this article this pass)")),
                                     "source_authority_ar": ("قرار وزير الموارد البشرية والتنمية "
                                                            "الاجتماعية رئيس المجلس الوطني للسلامة "
                                                            "والصحة المهنية رقم (64764) وتاريخ "
                                                            "13/5/1447هـ الموافق 4/11/2025م — "
                                                            "منشورة كاملة في جريدة أم القرى، العدد "
                                                            "(5138) وتاريخ 20/7/1447هـ الموافق "
                                                            "9/1/2026م. هذه المادة: "
                                                            + ("نص أساسي من uqn.gov.sa"
                                                               if source_tier == "primary"
                                                               else "نص ثانوي من qanoonsa.com "
                                                                    "(صفحة uqn.gov.sa الرسمية لم "
                                                                    "تصل إلى هذه المادة هذه "
                                                                    "الجولة)")),
                                     "source_status": status.lower(),
                                     "source_tier": source_tier,
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": status},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "osh_service_providers_regulation",
               "layer": "OSH_SERVICE_PROVIDERS_REGULATION_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-osh-service-providers-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (38 مادة، اصلية جميعها)",
               "title_en": ("OSH Service Providers Licensing/Accreditation Regulation — Arabic "
                            "LLM-ready layer (38 records, all original/اصلية)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 38], "consolidated_amended_law": False,
               "status_counts": src["status_counts"],
               "source_tier_counts": src.get("source_tier_counts"),
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready OSH Service Providers Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
