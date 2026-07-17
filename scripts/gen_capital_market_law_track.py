#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Capital Market Law track (نظام السوق المالية, Royal Decree
M/30, 2/6/1424H).

MIXED TIER — the single most complex verification case handled in this
corpus. The 2003 original text (67 articles) is fully verified with HIGH
confidence via laws.boe.gov.sa. The law has since been substantially
amended by Royal Decree M/16 (19/1/1441H), restructuring the
Market/Depository/Clearing-Center regime. Across three research passes,
CURRENT verbatim text was recovered for the large majority of articles —
either confirmed UNCHANGED from 2003, or independently fetched in full from
cma.gov.sa. For 12 articles at the core of the M/16 restructuring (1, 20,
21, 22, 23, 25, 26, 27, 28, 29, 30, 59), the exact current wording could
NOT be recovered despite three passes — these are ingested using the 2003
ORIGINAL text as a clearly-flagged HISTORICAL placeholder, NOT current law,
each carrying its own verification_tier distinct from the track's main
tier, plus a dedicated known_unresolved_discrepancies entry. A 68th record
(Article 20 مكرر) is reconstructed from a documented relocation description,
flagged with its own lower-confidence tier.

See sources/capital_market/law/official_source/
capital_market_law_official_source.json for the full methodology note and
all 16 documented unresolved discrepancies.

68 records: 42 اصلية / 25 معدلة / 0 ملغاة / 1 مضافة (Article 20 مكرر).
chapter_structure is empty (flat) — the current chapter map could not be
fully reconstructed given the Article-30 relocation; see the methodology
note for the two independently-confirmed chapter boundaries.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "capital_market", "law", "official_source",
                   "capital_market_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "capital_market", "law", "verified")
RECORDS = os.path.join(OUT_VER, "capital_market_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "capital_market_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "capital_market_arabic_legal_llm",
                        "capital_market_law_legal_llm_001_068.json")

LAW_ID = "sa-capital-market-law-m30-1424"
LAW_AR = "نظام السوق المالية"
TRACK_STATUS = "MIXED_TIER_SEE_PER_ARTICLE_VERIFICATION_TIER"
KEY_RE = r"capital_market_art_(\d{3})(?:_mukarrar_(\d+))?$"
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
    m = re.match(KEY_RE, key)
    n = int(m.group(1))
    mk = int(m.group(2)) if m.group(2) else 0
    return (n, mk)


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for key in keys:
        a = arts[key]
        m = re.match(KEY_RE, key)
        n = int(m.group(1))
        is_mukarrar = bool(m.group(2))
        ls = a.get("legal_status_ar")
        tier = a.get("verification_tier")
        text = a["text"]
        ver.append({"law_key": "capital_market", "law_component": "law", "language": "ar",
                    "record_layer": "CAPITAL_MARKET_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "verification_tier": tier,
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": ls == "معدلة",
                    "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "original_1424h_text": a.get("original_1424h_text"),
                    "official_text_status": TRACK_STATUS,
                    "governing_source_note": ("Arabic governs; this is a MIXED-TIER track — "
                                              "see verification_tier on this record and "
                                              "verification_methodology_note in the source "
                                              "artifact for the full caveat, especially if "
                                              "verification_tier is "
                                              "ORIGINAL_2003_TEXT_ONLY_CURRENT_WORDING_"
                                              "CONFIRMED_AMENDED_UNVERIFIED (2003 historical "
                                              "text shown, NOT current law) or "
                                              "RECONSTRUCTED_FROM_DOCUMENTED_RELOCATION_"
                                              "DESCRIPTION."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "record_id": "capital-market-law-llm-art-%s" % key.replace("capital_market_art_", ""),
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "capital_market/law/articles/%s" % key.replace("capital_market_art_", ""),
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام السوق المالية" % n],
                    "text_status": tier,
                    "source_trust": {"source_authority": ("Royal Decree — MIXED TIER, see "
                                                          "verification_tier"),
                                     "source_authority_ar": "مرسوم ملكي — طبقة موثوقية مختلطة، انظر verification_tier",
                                     "source_status": tier.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "capital_market",
               "layer": "CAPITAL_MARKET_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": TRACK_STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-capital-market-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (68 سجلاً؛ طبقة موثوقية مختلطة — انظر verification_tier لكل مادة)",
               "title_en": "Saudi Capital Market Law — Arabic LLM-ready layer (68 records, mixed verification tier)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 67], "text_status": TRACK_STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Capital Market Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
