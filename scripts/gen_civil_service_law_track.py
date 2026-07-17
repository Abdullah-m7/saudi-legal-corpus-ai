#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Civil Service Law track (نظام الخدمة المدنية, Royal Decree
M/49, 10/7/1397H) — the general public-sector employment statute, distinct
from the Labor Law (نظام العمل, private sector) already in this corpus.

VERIFICATION TIER — laws.boe.gov.sa's live portal was unreachable this
research pass (503 via WebFetch, 422 via r.jina.ai, connection error via
direct curl). Full text instead rests on a Wayback Machine snapshot of the
BOE portal's law-detail page, fetched directly via curl (not via r.jina.ai
or WebFetch, neither of which can reach archive.org), cross-verified
article-by-article (all 44 article-entries, 100%) against a direct fetch
of nezams.com. The six-article amendment package under Royal Decree M/139
(19/10/1441H) was additionally corroborated via independent SPA/Okaz news
coverage.

See sources/civil_service/law/official_source/
civil_service_law_official_source.json for the full methodology note and
all documented unresolved discrepancies.

44 records (40 numbered + 4 مكرر additions: 15 مكرر, 25 مكرر, 36 مكرر,
37 مكرر): 20 اصلية / 19 معدلة / 1 ملغاة (Article 3) / 4 مضافة. 3 أبواب,
with الباب الثاني further divided into 6 فصول. Article 3 was repealed by
Royal Decree M/95 (15/9/1439H) with no replacement text; its pre-repeal
1397H text is preserved per this corpus's policy of never deleting
repealed articles. 19 amended articles carry a genuinely-recovered
original_1397h_text field (never fabricated); three of those (Articles
20, 29, 35) were amended TWICE, with the first (intermediate) amendment
recorded only in `history`, not as a separate original-text field.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "civil_service", "law", "official_source",
                   "civil_service_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "civil_service", "law", "verified")
RECORDS = os.path.join(OUT_VER, "civil_service_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "civil_service_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "civil_service_arabic_legal_llm",
                        "civil_service_law_legal_llm_001_044.json")

LAW_ID = "sa-civil-service-law-m49-1397"
LAW_AR = "نظام الخدمة المدنية"
STATUS = "BOE_WAYBACK_X_NEZAMS_FULL_CROSS_VERIFIED"
KEY_RE = r"civil_service_art_(\d{3})(_mukarrar)?$"
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
        original = a.get("original_1397h_text")
        suffix = key.replace("civil_service_art_", "")
        ver.append({"law_key": "civil_service", "law_component": "law", "language": "ar",
                    "record_layer": "CIVIL_SERVICE_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "original_1397h_text": original,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": ls == "معدلة",
                    "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track's full text rests on "
                                              "a Wayback Machine snapshot of the BOE portal "
                                              "(fetched directly via curl, not via r.jina.ai or "
                                              "WebFetch, neither of which can reach "
                                              "archive.org), cross-verified article-by-article "
                                              "(100% of all 44 article-entries) against a direct "
                                              "fetch of nezams.com, because laws.boe.gov.sa's "
                                              "live portal was unreachable this research pass — "
                                              "see verification_methodology_note in the source "
                                              "artifact for the full caveat."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "record_id": "civil-service-law-llm-art-%s" % suffix,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "original_1397h_text": original,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "civil_service/law/articles/%s" % suffix,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام الخدمة المدنية" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Decree M/49 — BOE portal via "
                                                          "Wayback Machine snapshot, "
                                                          "cross-verified article-by-article "
                                                          "against nezams.com"),
                                     "source_authority_ar": "مرسوم ملكي رقم (م/49) — بوابة هيئة الخبراء عبر أرشيف Wayback Machine، مطابقة كاملة مع nezams.com",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "civil_service",
               "layer": "CIVIL_SERVICE_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-civil-service-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (44 سجلاً؛ نص موحّد: 20 أصلية، 19 معدلة، 1 ملغاة، 4 مضافة)",
               "title_en": "Saudi Civil Service Law — Arabic LLM-ready layer (44 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 40], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Civil Service Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
