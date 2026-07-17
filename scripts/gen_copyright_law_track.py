#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Copyright Law track (نظام حماية حقوق المؤلف, Royal Decree
M/41, 2/7/1424H).

DISTINCT VERIFICATION TIER — laws.boe.gov.sa was unreachable this research
pass (direct connection reset; r.jina.ai reader-proxy timed out twice;
Wayback Machine blocked/403 in this sandbox). PRIMARY WORKING SOURCE:
qadha.org.sa (الجمعية العلمية القضائية السعودية), a Saudi judicial-studies
professional association's full verbatim article-by-article compilation,
footnoted with the exact 2018 amendment decision text. Cross-checked
structurally against WIPO Lex (entry sa062, chapter/article count/order
confirmed; the PDF itself extracted with word-internal character scrambling
and could not be used for verbatim wording) and spot-checked against an
independent blog (almirjah.wordpress.com).

*** CRITICAL: this law is confirmed REPEALED effective 2026-08-01 by Royal
Decree M/169 (14/08/1447H). The new law's full Arabic text could not be
verified this pass and is explicitly NOT ingested — this track represents
the currently in-force text as of the build date, with the repeal flagged
in the source artifact's verification_methodology_note and
known_unresolved_discrepancies. A follow-up ingestion pass for M/169 is
recommended once its primary text is verifiable. ***

Consolidated amended law: 19 اصلية / 9 معدلة / 0 ملغاة / 0 مضافة (28 total
articles). The 2018 amendment (Council of Ministers Resolution 536,
19/10/1439H) replaced Ministry/Minister references with the Saudi Authority
for Intellectual Property (SAIP) and its Board throughout. Articles are
numbered by ordinal position 1..28, no مكرر, organized under 7 chapters
(plus article 1's own definitions heading) with section_ar carrying each
article's chapter heading.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "copyright", "law", "official_source",
                   "copyright_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "copyright", "law", "verified")
RECORDS = os.path.join(OUT_VER, "copyright_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "copyright_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "copyright_arabic_legal_llm",
                        "copyright_law_legal_llm_001_028.json")

LAW_ID = "sa-copyright-law-m41-1424"
LAW_AR = "نظام حماية حقوق المؤلف"
STATUS = "SECONDARY_SOURCE_STRUCTURAL_WIPO_CROSS_CHECK_BOE_UNREACHABLE"
KEY_RE = r"copyright_art_(\d{3})$"
AMENDED_KEYS = {"copyright_art_%03d" % n for n in (1, 7, 8, 16, 21, 22, 24, 25, 26)}
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك").split())

REPEAL_NOTICE = ("Superseded effective 2026-08-01 by Royal Decree M/169 (14/08/1447H) — "
                 "the new law's text is not yet verifiable and is not ingested; this "
                 "record reflects the text in force as of the build date.")


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
        ver.append({"law_key": "copyright", "law_component": "law", "language": "ar",
                    "record_layer": "COPYRIGHT_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": is_amended, "is_added": False,
                    "amendment_history": a.get("history"),
                    "original_2003_text": a.get("original_2003_text"),
                    "official_text_status": STATUS,
                    "superseding_law_notice": REPEAL_NOTICE,
                    "governing_source_note": ("Arabic governs; this track uses a distinct "
                                              "verification tier — qadha.org.sa's compiled "
                                              "text structurally cross-checked against WIPO "
                                              "Lex, because laws.boe.gov.sa was unreachable "
                                              "this research pass — see this article's own "
                                              "status field and the source artifact's "
                                              "verification_methodology_note for the full "
                                              "caveat, INCLUDING that this law is superseded "
                                              "effective 2026-08-01 by Royal Decree M/169."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": is_amended, "is_added": False,
                    "record_id": "copyright-law-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "copyright/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام حماية حقوق المؤلف" % n],
                    "text_status": STATUS,
                    "superseding_law_notice": REPEAL_NOTICE,
                    "source_trust": {"source_authority": ("Royal Decree — qadha.org.sa compiled "
                                                          "text (Saudi judicial-studies "
                                                          "association), WIPO Lex structural "
                                                          "cross-check, laws.boe.gov.sa "
                                                          "unreachable this pass"),
                                     "source_authority_ar": "مرسوم ملكي — نص مجمّع من الجمعية العلمية القضائية السعودية، تحقق هيكلي مقارنة بـ WIPO Lex",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "copyright",
               "layer": "COPYRIGHT_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "chapter_structure": src["chapter_structure"],
               "superseding_law_notice": REPEAL_NOTICE,
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-copyright-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (28 مادة؛ نص موحّد: 19 أصلية، 9 معدّلة؛ يُلغى في 2026-08-01)",
               "title_en": "Saudi Copyright Law — Arabic LLM-ready layer (28 records, consolidated, superseded 2026-08-01)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 28], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "superseding_law_notice": REPEAL_NOTICE,
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Copyright Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
