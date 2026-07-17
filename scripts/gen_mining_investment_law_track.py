#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Mining Investment Law track (نظام الاستثمار التعديني, Royal
Decree M/140, 19/10/1441H).

DISTINCT VERIFICATION TIER — laws.boe.gov.sa's live portal was unreachable
this research pass (503/connection-reset via both WebFetch and direct
curl). Full text instead rests on a Wayback Machine snapshot of the BOE
portal's law-detail page, fetched directly via curl (not via r.jina.ai or
WebFetch, neither of which can reach archive.org), cross-verified
structurally against FAOLEX's PDF (decree/date/chapter/article-count
corroboration only — FAOLEX's own text extraction was severely
word-scrambled by a known RTL-PDF artifact and was never used as a
verbatim-text source). Further corroborated by taadeen.sa PDF metadata and
nezams.com.

See sources/mining_investment/law/official_source/
mining_investment_law_official_source.json for the full methodology note
and all documented unresolved discrepancies.

64 records (63 original-numbered + 1 مكرر): 63 اصلية / 0 معدلة / 1 مضافة
(Article 56 مكرر, added by Royal Decree M/27, 4/2/1444H, introducing
criminal penalties for unlicensed extraction). 13 articles (4, 6, 7, 8, 9,
10, 11, 14, 15, 16, 18, 19, 35) carry a documented commencement-date-only
administrative amendment (Royal Decree M/12, 8/1/1442H) — their
SUBSTANTIVE TEXT is unchanged, so per this corpus's text-change-based
status policy they remain اصلية, with the administrative note preserved in
their amendment_history. 8 chapters (أبواب).

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "mining_investment", "law", "official_source",
                   "mining_investment_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "mining_investment", "law", "verified")
RECORDS = os.path.join(OUT_VER, "mining_investment_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "mining_investment_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "mining_investment_arabic_legal_llm",
                        "mining_investment_law_legal_llm_001_064.json")

LAW_ID = "sa-mining-investment-law-m140-1441"
LAW_AR = "نظام الاستثمار التعديني"
STATUS = "BOE_PORTAL_WAYBACK_X_FAOLEX_CROSS_VERIFIED"
KEY_RE = r"mining_investment_art_(\d{3})(_mukarrar)?$"
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
    mk = 1 if m.group(2) else 0
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
        text = a["text"]
        suffix = key.replace("mining_investment_art_", "")
        ver.append({"law_key": "mining_investment", "law_component": "law", "language": "ar",
                    "record_layer": "MINING_INVESTMENT_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": ls == "معدلة",
                    "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track uses a distinct "
                                              "verification tier — a Wayback Machine snapshot "
                                              "of the BOE portal (fetched directly, not via "
                                              "r.jina.ai or WebFetch, neither of which can "
                                              "reach archive.org), cross-verified structurally "
                                              "against FAOLEX, because laws.boe.gov.sa's live "
                                              "portal was unreachable this research pass — see "
                                              "verification_methodology_note in the source "
                                              "artifact for the full caveat."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "record_id": "mining-investment-law-llm-art-%s" % suffix,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "mining_investment/law/articles/%s" % suffix,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام الاستثمار التعديني" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Decree — BOE portal via "
                                                          "Wayback Machine snapshot, "
                                                          "cross-verified structurally against "
                                                          "FAOLEX"),
                                     "source_authority_ar": "مرسوم ملكي — بوابة هيئة الخبراء عبر أرشيف Wayback Machine، مطابقة هيكلية مع قاعدة بيانات FAOLEX",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "mining_investment",
               "layer": "MINING_INVESTMENT_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-mining-investment-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (64 سجلاً؛ نص موحّد: 63 أصلية، 1 مضافة)",
               "title_en": "Saudi Mining Investment Law — Arabic LLM-ready layer (64 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 63], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Mining Investment Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
