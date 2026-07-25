#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Credit Information Law track (نظام المعلومات الائتمانية,
Royal Decree M/37, 5/7/1429H).

VERIFICATION TIER — TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED per this corpus's
4-tier taxonomy (reports/verification_tiers/VERIFICATION_TIERS_METHODOLOGY_AR.md).
laws.boe.gov.sa's LIVE portal returned HTTP 503 (WebFetch) and a raw TCP
connection reset (direct curl, exit 35) on every attempt this research pass;
the r.jina.ai read-proxy returned HTTP 422 (15s navigation timeout) — both
consistent with this corpus's documented BOE-egress-blocked pattern. A Wayback
Machine snapshot of the exact BOE lawId page (63dc01a6-fc5c-4600-9171-
a9a700f2d222, timestamp 20260215023401) was located via the archive.org
availability API and fetched successfully via direct curl with a browser
User-Agent header (WebFetch itself cannot reach web.archive.org at all) —
yielding the full verbatim text of all 17 articles as the sole official/
primary source. Cross-verified against two independent non-official secondary
sources: nezams.com (topic-by-topic match on every article, decree number,
hijri date, 17-article count, explicit no-amendment note) and saudipedia.com
(decree, 5/7/1429H = 8 July 2008G issuance date, 17-article count, subject
matter, identical three-item penalty structure). One minor discrepancy
(WebFetch's own AI-summarized Gregorian date for nezams.com, "28 June 2008")
was identified and resolved in favor of the two directly-sourced dates (BOE's
own date field and saudipedia.com), not adopted. See sources/credit_information/
law/official_source/credit_information_law_official_source.json for the full
methodology note.

17 articles, FLAT structure (no فصل/باب divisions). ALL 17 اصلية — a
dedicated search pass ("تعديل نظام المعلومات الائتمانية") found no evidence
of any amendment or repeal of any article since the law's 2008 enactment; this
is a documented honest negative finding. No known_unresolved_discrepancies at
the article-text level for this pass (a positive finding of clean three-source
congruence, not an omission). No predecessor-law repeal is named: Article 17
carries only a general, non-specific repeal clause. No overlap with this
corpus's existing sama_law, banking_control_law or finance_companies_law
tracks (verified by reading their registry entries — distinct subject
matter). A companion Implementing Regulation exists (issued by the SAMA
Governor per Article 16) but is out of scope for this pass, per this corpus's
established precedent of tracking a law's Implementing Regulation separately.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "credit_information", "law", "official_source",
                   "credit_information_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "credit_information", "law", "verified")
RECORDS = os.path.join(OUT_VER, "credit_information_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "credit_information_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "credit_information_arabic_legal_llm",
                        "credit_information_law_legal_llm_001_017.json")

LAW_ID = "sa-credit-information-law-m37-1429"
LAW_AR = "نظام المعلومات الائتمانية"
STATUS = "BOE_WAYBACK_PRIMARY_X_NEZAMS_X_SAUDIPEDIA_TRIPLE_CROSS_VERIFIED_LIVE_BOE_UNREACHABLE"
KEY_RE = r"credit_information_art_(\d{3})$"
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
        ver.append({"law_key": "credit_information", "law_component": "law", "language": "ar",
                    "record_layer": "CREDIT_INFORMATION_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": is_amended, "is_added": False,
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track uses "
                                              "TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED — a single "
                                              "official/primary channel (a Wayback Machine snapshot "
                                              "of the BOE lawId page) cross-checked against "
                                              "non-official secondary sources (nezams.com, "
                                              "saudipedia.com), because laws.boe.gov.sa's live "
                                              "portal returned HTTP 503 / connection reset on every "
                                              "attempt this research pass — see "
                                              "verification_methodology_note in the source "
                                              "artifact for the full caveat."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": is_amended, "is_added": False,
                    "record_id": "credit-information-law-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "credit_information/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام المعلومات الائتمانية" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Decree — Wayback Machine archive "
                                                          "of the BOE lawId page (current/only "
                                                          "official channel reached), "
                                                          "cross-checked against nezams.com and "
                                                          "saudipedia.com; BOE live portal "
                                                          "unreachable this pass"),
                                     "source_authority_ar": "مرسوم ملكي — أرشيف بوابة هيئة الخبراء عبر Wayback Machine (القناة الرسمية الوحيدة التي أمكن الوصول إليها)، مطابقة nezams.com وsaudipedia.com",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "credit_information",
               "layer": "CREDIT_INFORMATION_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "verification_tier": "TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED",
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": False,
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-credit-information-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (17 مادة؛ جميعها أصلية)",
               "title_en": "Credit Information Law — Arabic LLM-ready layer (17 records, all original)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 17], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Credit Information Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
