#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Anti-Harassment Law track (نظام مكافحة جريمة التحرش, Royal
Decree M/96, 16/9/1439H).

DISTINCT VERIFICATION TIER, with two sub-tiers within this single track.
(1) BOE_PORTAL_MULTI_SOURCE_CROSS_CHECKED for the 7 unamended articles
(1-5, 7, 8): full verbatim text from the Bureau of Experts (BOE) legal
portal at laws.boe.gov.sa, reached via WebFetch through an
https://r.jina.ai/<url> reader-proxy prefix, cross-checked against four
independent secondary Saudi legal-reference sites plus an independent
journalist's account, all agreeing with no divergence. (2)
SECONDARY_PRESS_CONVERGENCE_AMENDMENT_UNCONFIRMED_VERBATIM for article 6's
third paragraph, added by Royal Decree M/48 (1/6/1442H): the amendment's
EXISTENCE is confirmed with high confidence (Umm Al-Qura Gazette's own
indexed page title, two independent contemporaneous news outlets, matching
decree date), but the EXACT wording has two candidate versions, neither
read off a fully-rendered primary document — this track uses the longer
candidate (see the source artifact's verification_methodology_note), with
the shorter alternate preserved in known_unresolved_discrepancies rather
than silently discarded. This is a genuinely weaker verification tier than
every MOJ-portal-sourced track in this corpus. Repository owner explicitly
reviewed and approved this specific handling.

Consolidated amended law: 7 اصلية / 1 معدلة (art 6) / 0 ملغاة / 0 مضافة (8
total). Articles are numbered by ordinal position 1..8 (no مكرر), flat
structure with no chapter/section wrapper.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "anti_harassment", "law", "official_source",
                   "anti_harassment_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "anti_harassment", "law", "verified")
RECORDS = os.path.join(OUT_VER, "anti_harassment_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "anti_harassment_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "anti_harassment_arabic_legal_llm",
                        "anti_harassment_law_legal_llm_001_008.json")

LAW_ID = "sa-anti-harassment-law-m96-1439"
LAW_AR = "نظام مكافحة جريمة التحرش"
KEY_RE = r"anti_harassment_art_(\d{3})$"
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
        tier = a["verification_tier"]
        is_amended = ls == "معدلة"
        ver.append({"law_key": "anti_harassment", "law_component": "law", "language": "ar",
                    "record_layer": "ANTI_HARASSMENT_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "verification_tier": tier,
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": is_amended, "is_added": False,
                    "amendment_history": a.get("history"),
                    "official_text_status": tier,
                    "governing_source_note": ("Arabic governs; this track uses a distinct "
                                              "verification tier — see this article's own "
                                              "verification_tier field and the source "
                                              "artifact's verification_methodology_note for "
                                              "the full caveat (article 6 specifically rests "
                                              "on secondary press convergence for its 2021 "
                                              "amendment, not a fully-rendered primary "
                                              "document)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": is_amended, "is_added": False,
                    "record_id": "anti-harassment-law-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "anti_harassment/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام مكافحة جريمة التحرش" % n],
                    "text_status": tier,
                    "source_trust": {"source_authority": ("Royal Decree — Bureau of Experts "
                                                          "(BOE) portal, distinct tier (see "
                                                          "verification_tier)"),
                                     "source_authority_ar": "مرسوم ملكي — بوابة هيئة الخبراء، درجة توثيق مميزة (انظر verification_tier)",
                                     "source_status": tier.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"],
                                     "verification_tier": tier},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "anti_harassment", "layer": "ANTI_HARASSMENT_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "official_text_status": "MIXED_TIER_SEE_PER_ARTICLE_VERIFICATION_TIER",
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "verification_methodology_note": src["verification_methodology_note"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-anti-harassment-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (8 مواد؛ نص موحّد: 7 أصلية، 1 معدّلة)",
               "title_en": "Saudi Anti-Harassment Law — Arabic LLM-ready layer (8 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 8], "text_status": "MIXED_TIER_SEE_PER_ARTICLE_VERIFICATION_TIER",
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Anti-Harassment Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
