#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Environmental Law track (نظام البيئة, Royal Decree M/165,
19/11/1441H, approving Council of Ministers Decision No. 729, 16/11/1441H).

STRONG TRIPLE-SOURCE VERIFICATION TIER — laws.boe.gov.sa's live portal was
unreachable this research pass (HTTP 503 direct; HTTP 422 via r.jina.ai
proxy). BOE's own content was instead recovered via the Wayback Machine
(the 15 October 2025 snapshot, cross-checked against the 24 September 2024
snapshot), and independently cross-verified against two further
independently-hosted full-text copies: a PDF hosted at green.org.sa and
nezams.com. All 49 articles matched verbatim across all three sources
EXCEPT ONE flagged point: Article 1's definition of "الجهة المختصة"
(Competent Authority), where BOE's OWN official per-article amendment-log
states current wording differs from BOE's OWN main running law-text body
— a genuine self-contradiction in BOE's own official data, persistent
across two Wayback snapshots over a year apart. This build treats the
amendment (Council of Ministers Decision No. 406, 14/5/1445H, adding
"المؤسسة العامة للمحافظة على الشعب المرجانية والسلاحف في البحر الأحمر" to
the definition) as operative, following the same reasoning precedent
already established for the Traffic Law track's "BOE portal lags behind
confirmed amendments" situations — see
sources/traffic/law/official_source/traffic_law_official_source.json.
The pre-amendment wording is preserved verbatim as original_1441h_text.

See sources/environmental/law/official_source/environmental_law_official_source.json
for the full methodology note and all documented unresolved discrepancies,
including this Article 1 self-contradiction, the indicative-only list of
multiple (non-consolidated) Implementing Regulations, and the Arabic-style
period thousand-separator convention preserved verbatim in monetary figures.

49 records: 48 اصلية / 1 معدلة (Article 1's "الجهة المختصة" definition,
amended by Council of Ministers Decision No. 406, 14/5/1445H; the other
definitions in Article 1 and all remaining 48 articles are unamended).
9 فصول (chapters) — this law has NO أبواب (Parts) tier, a single-level
chapter structure, confirmed by full-text search of all three sources.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "environmental", "law", "official_source",
                   "environmental_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "environmental", "law", "verified")
RECORDS = os.path.join(OUT_VER, "environmental_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "environmental_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "environmental_arabic_legal_llm",
                        "environmental_law_legal_llm_001_049.json")

LAW_ID = "sa-environmental-law-m165-1441"
LAW_AR = "نظام البيئة"
STATUS = "BOE_WAYBACK_X_GREEN_ORG_PDF_X_NEZAMS_TRIPLE_VERIFIED_ART1_BOE_SELF_CONTRADICTION"
KEY_RE = r"environmental_art_(\d{3})$"
AMENDED_KEYS = {"environmental_art_001"}
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
        ver.append({"law_key": "environmental", "law_component": "law", "language": "ar",
                    "record_layer": "ENVIRONMENTAL_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": is_amended, "is_added": False,
                    "amendment_history": a.get("history"),
                    "original_1441h_text": a.get("original_1441h_text"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track rests on a strong "
                                              "triple-source verification tier — BOE (via Wayback "
                                              "Machine), an independently-hosted green.org.sa PDF, "
                                              "and nezams.com all matched verbatim for 48 of 49 "
                                              "articles. The one exception, Article 1's definition "
                                              "of الجهة المختصة, rests on BOE's own official "
                                              "amendment-log self-contradicting BOE's own main "
                                              "article-text body — see "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact for the full caveat."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": is_amended, "is_added": False,
                    "record_id": "environmental-law-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "environmental/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام البيئة" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Decree M/165 — BOE portal (via "
                                                          "Wayback Machine) cross-verified against "
                                                          "an independently-hosted green.org.sa PDF "
                                                          "and nezams.com; one flagged article "
                                                          "(Article 1) rests on BOE's own "
                                                          "amendment-log self-contradicting BOE's "
                                                          "own main text, plus qanoonsa.com "
                                                          "corroboration"),
                                     "source_authority_ar": "مرسوم ملكي رقم (م/165) — بوابة هيئة الخبراء (عبر أرشيف الويب) مقارنة بملف PDF مستضاف بشكل مستقل على green.org.sa وبموقع nezams.com؛ مع تحفظ خاص بالمادة الأولى يقوم على تناقض ذاتي في سجل تعديلات بوابة هيئة الخبراء نفسها، مدعوماً بموقع qanoonsa.com",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "environmental",
               "layer": "ENVIRONMENTAL_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-environmental-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (49 مادة؛ نص موحّد: 48 أصلية، 1 معدّلة)",
               "title_en": "Saudi Environmental Law — Arabic LLM-ready layer (49 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 49], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Environmental Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
