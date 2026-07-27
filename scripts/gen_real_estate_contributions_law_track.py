#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Real Estate Contributions Law track (نظام المساهمات
العقارية, Royal Decree M/203, 28/12/1444H -- the currently in-force law governing
real-estate collective-investment / crowdfunding-style development schemes,
licensed by the General Authority for Real Estate (REGA) with Capital Market
Authority (CMA) co-regulation of fundraising and certificate offerings).

BRAND-NEW BASE-LAW TRACK -- this statute was NOT previously in this corpus. It was
built from scratch this pass. This is a DIFFERENT, distinct instrument from this
corpus's pre-existing real_estate_finance_law and investment_law tracks (neither
of which was touched this pass): it governs pooled/collective real-estate
development "contributions" (مساهمات عقارية), not general real estate finance or
general investment.

WHICH INSTRUMENT, AND HOW CONFIRMED -- نظام المساهمات العقارية is a single,
self-standing Royal-Decree law (M/203, 28/12/1444H, on CoM Resolution 881,
23/12/1444H). Confirmed via cross-checked independent official sources:
(1) laws.boe.gov.sa carries it under its own dedicated lawId
5efb6f40-d859-47e6-9c8a-b04500943ecc (seen via WebSearch), but was unreachable
this pass (see TIER note below); (2) rega.gov.sa (the General Authority for Real
Estate -- the administering authority) hosts the official scanned Royal-Decree
PDF itself (Bureau-of-Experts-stamped, King-signed, 11 pages), fetched directly
via curl (HTTP 200); (3) the Umm Al-Qura Gazette's own website
(www.uqn.gov.sa/details?p=23304) independently reproduces the full Council of
Ministers Resolution (881) text, fetched directly via curl (HTTP 200); (4)
qanoonsa.com (an independent secondary aggregator) confirms the decree metadata,
7-chapter structure, and specific article content.

SUPERSESSION -- the Law replaces weaker Ministry of Commerce administrative
controls that previously governed the offering of real estate contributions, but
Article 38 repeals conflicting rules ONLY via a generic formula ("ويلغي كل ما
يتعارض معه من أحكام") without naming the predecessor instrument by number/date
anywhere in the Law's text, the Royal Decree preamble, or CoM Resolution 881.
See known_unresolved_discrepancies in the source artifact.

VERIFICATION TIER -- TIER_1_PRIMARY_MULTI_SOURCE. laws.boe.gov.sa (this corpus's
usual primary source) was checked FIRST per standard methodology but was
unreachable this pass (WebFetch: HTTP 503; direct curl: connection reset), and
its web.archive.org snapshot was blocked by this session's egress policy (not
circumvented further). However, TWO OTHER independent official/primary sources
were reached and cross-verified against each other and against the full-text
extraction used for storage:
  (1) rega.gov.sa's own officially-hosted scanned PDF of the Royal Decree (Bureau
      of Experts at the Council of Ministers letterhead, King's signature, official
      seals on every page) -- all 11 pages were read visually page-by-page (a pass
      equivalent to independent OCR/rendered-page-image verification of the SAME
      official document) and compared word-for-word against the nezams.com
      full-text extraction used for the stored `text` field: the preamble, CoM
      Resolution 881, and all 38 articles across all 7 chapters matched exactly,
      with one immaterial digit-script rendering variance flagged (Article 32,
      the fine amount -- see known_unresolved_discrepancies).
  (2) the Umm Al-Qura Gazette's own website, independently reproducing CoM
      Resolution 881's full text -- matches (1) and nezams.com exactly.
Given this exact-match, full-document cross-verification across two independent
official sources (plus a third independent secondary aggregator, qanoonsa.com),
this track is classified TIER_1 despite laws.boe.gov.sa itself being unreachable
this pass -- see the source artifact's verification_methodology_note for the full
account and an explicit recommendation to re-check laws.boe.gov.sa once reachable.

38 articles, 7 chapters (فصول); all 38 اصلية; 0 معدلة, 0 ملغاة, 0 مضافة (the Law
has had no amendments per nezams.com: "لم يجرى عليه تعديل"). Diacritics
(tashkeel) are stripped uniformly from article bodies (not from preamble_ar /
com_resolution_ar, which retain nezams.com's own partial tashkeel, consistent
with this corpus's convention for BOE-family tracks). The source uses Western
digits throughout except ONE deliberately-preserved instance (Article 7: "١٥٪" in
Arabic-Indic digits, confirmed present identically in the official scan too) --
not silently normalized, per this corpus's no-silent-correction policy.

IMPLEMENTING REGULATION -- identified via multiple independent signals
(eparticipation.my.gov.sa public-consultation page, rega.gov.sa's own
regulations section, argaam.com press coverage, qanoonsa.com) but NOT built this
pass: its precise ministerial-decision number/date and full verbatim text could
not be pinned down and verified within reasonable effort this pass. Flagged as a
follow-up candidate track (real_estate_contributions_law_regulation,
law_component "regulation").

Arabic governs; no translation/paraphrase/interpretation. Read-only over input;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "real_estate_contributions_law", "law", "official_source",
                   "real_estate_contributions_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "real_estate_contributions_law", "law", "verified")
RECORDS = os.path.join(OUT_VER, "real_estate_contributions_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "real_estate_contributions_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "real_estate_contributions_law_arabic_legal_llm",
                        "real_estate_contributions_law_legal_llm_001_038.json")

LAW_ID = "sa-real-estate-contributions-law-m203-1444"
LAW_AR = "نظام المساهمات العقارية"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"real_estate_contributions_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة اللوائح أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم النظام الهيئة المجلس الرئيس المساهمة العقارية المرخص له").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def _sort_key(key):
    m = re.match(KEY_RE, key)
    n = int(m.group(1))
    suf = m.group(2)
    if suf is None:
        return (n, 0)
    if suf == "":
        return (n, 1)
    return (n, 1 + int(suf))


def _top_status(key):
    if key in AMENDED_KEYS:
        return STATUS_AMENDED
    if key in ADDED_KEYS:
        return STATUS_ADDED
    return STATUS_UNCHANGED


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for idx, key in enumerate(keys, start=1):
        a = arts[key]
        m = re.match(KEY_RE, key)
        n = int(m.group(1))
        is_mukarrar = bool(a.get("is_mukarrar"))
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        is_repealed = ls == "ملغاة"
        text = a["text"]
        top_status = _top_status(key)
        text_complete = a.get("text_complete", True)
        ver.append({"law_key": "real_estate_contributions_law", "law_component": "law",
                    "language": "ar",
                    "record_layer": "REAL_ESTATE_CONTRIBUTIONS_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "text_complete": text_complete,
                    "amendment_history": a.get("history"),
                    "official_text_status": top_status,
                    "governing_source_note": ("Arabic governs; this is the currently in-force "
                                              "Real Estate Contributions Law (Royal Decree "
                                              "M/203, 28/12/1444H), a brand-new base-law track "
                                              "built from scratch this pass (not previously in "
                                              "this corpus; distinct from this corpus's "
                                              "real_estate_finance_law and investment_law "
                                              "tracks). laws.boe.gov.sa was checked FIRST per "
                                              "standard methodology but unreachable this pass "
                                              "(connection reset / HTTP 503); its web.archive.org "
                                              "snapshot was blocked by session egress policy. "
                                              "TWO other independent official sources were "
                                              "reached and cross-verified instead: rega.gov.sa's "
                                              "own officially-hosted scanned Royal-Decree PDF "
                                              "(read visually page-by-page, 11/11 pages, "
                                              "equivalent to an independent OCR pass) and the "
                                              "Umm Al-Qura Gazette's own website "
                                              "(uqn.gov.sa/details?p=23304); both matched the "
                                              "nezams.com full-text extraction used for storage "
                                              "exactly, aside from one immaterial digit-script "
                                              "variance (Article 32). TIER_1_PRIMARY_MULTI_"
                                              "SOURCE. See verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track -- notably "
                                              "that the predecessor Ministry of Commerce "
                                              "instrument is not named by number/date anywhere "
                                              "in the Law's own text, and the Implementing "
                                              "Regulation was not ingested this pass."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "real-estate-contributions-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "real_estate_contributions_law/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام المساهمات العقارية" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree No. (M/203), "
                                                          "28/12/1444H (Council of Ministers "
                                                          "Resolution 881, 23/12/1444H; Shura "
                                                          "Council Resolutions 305/45 and "
                                                          "152/21) — the currently in-force "
                                                          "Real Estate Contributions Law. "
                                                          "Verbatim text from nezams.com, "
                                                          "cross-verified word-for-word against "
                                                          "rega.gov.sa's officially-hosted "
                                                          "scanned Royal-Decree PDF (visual "
                                                          "page-by-page read, 11/11 pages) and "
                                                          "the Umm Al-Qura Gazette's own website "
                                                          "(uqn.gov.sa/details?p=23304); "
                                                          "laws.boe.gov.sa itself unreachable "
                                                          "this pass. TIER_1_PRIMARY_MULTI_"
                                                          "SOURCE."),
                                     "source_authority_ar": "المرسوم الملكي رقم (م/203) وتاريخ 28/12/1444هـ (قرار مجلس الوزراء رقم (881) وتاريخ 23/12/1444هـ؛ قرارا مجلس الشورى رقم (305/45) و(152/21)) — نظام المساهمات العقارية النافذ حالياً. النص الحرفي من nezams.com، مُتحقَّق منه كلمة بكلمة مقابل النسخة الرسمية المصوَّرة من rega.gov.sa (قراءة بصرية صفحة بصفحة، 11/11 صفحة) ومقابل موقع جريدة أم القرى الرسمي (uqn.gov.sa/details?p=23304)؛ laws.boe.gov.sa نفسه غير قابل للوصول هذه الجولة. المستوى TIER_1_PRIMARY_MULTI_SOURCE.",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "real_estate_contributions_law",
               "layer": "REAL_ESTATE_CONTRIBUTIONS_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "council_of_ministers_decision": src.get("council_of_ministers_decision"),
               "shura_council_decision": src.get("shura_council_decision"),
               "gazette_publication_hijri": src.get("gazette_publication_hijri"),
               "legal_status_ar": src.get("legal_status_ar"),
               "supersedes_ar": src.get("supersedes_ar"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-real-estate-contributions-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (38 مادة؛ 38 أصلية، 0 معدلة، 0 مضافة، 0 ملغاة؛ 7 فصول)",
               "title_en": ("The Saudi Arabian Real Estate Contributions Law (Royal Decree "
                            "M/203, 28/12/1444H) — Arabic LLM-ready layer (38 records: 38 "
                            "original, 0 amended, 0 added, 0 repealed; 7 chapters)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 38], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Real Estate Contributions Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
