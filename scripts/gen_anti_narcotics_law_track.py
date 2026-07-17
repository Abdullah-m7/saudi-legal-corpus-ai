#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Anti-Narcotics and Psychotropic Substances Control Law
track (نظام مكافحة المخدرات والمؤثرات العقلية, Royal Decree M/39,
8/7/1426H).

VERIFICATION TIER — the official BOE portal (laws.boe.gov.sa) returned
HTTP 503 on direct WebFetch for both its LawDetails and Viewer pages;
the r.jina.ai proxy successfully retrieved the complete Markdown-converted
page (Royal Decree preamble, Council of Ministers Resolution text, and all
74 articles verbatim). This became the primary extracted text and is
cross-verified word-for-word, article by article, against nezams.com
(independent Arabic legal-reference aggregator, raw HTML via r.jina.ai,
not LLM-summarized) — full agreement except one textual variant in Article
42 paragraph 1 (BOE's coherent "الدعوى" adopted over nezams.com's
apparent OCR/typo "الدعوة"; see known_unresolved_discrepancies). A third
independent source — qadha.org.sa's published reference book (ISBN
978-603-92112-4-2, 1445H) — additionally triple-verifies the highest-
stakes penalty articles (37, the death-penalty article, plus 38, 39, 40,
49). A Wayback Machine cross-check could NOT be completed (sandbox egress
policy blocked archive.org access; see the source artifact's
verification_methodology_note) — a documented gap, mitigated by the two
other independently-sourced full-text copies.

See sources/anti_narcotics/law/official_source/
anti_narcotics_law_official_source.json for the full methodology note and
documented unresolved discrepancies.

NO formal الباب (Part) / الفصل (Chapter) structure exists in this law —
confirmed by a full-text grep of a combined law+regulation reference PDF
finding zero باب/فصل structural markers. Instead the 74 sequential
articles carry unnumbered topical headers, modeled here as
chapter_structure entries with title_ar + article range only (no
باب/فصل labels). All 74 articles اصلية — no amending instrument to the
article text itself was found since 1426H (only the annexed substance
schedules were administratively updated under Article 70's delegated
authority, which is not a textual amendment to any article). An
Implementing Regulation exists (Council of Ministers Resolution 201,
10/6/1431H) but is not extracted in this track.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "anti_narcotics", "law", "official_source",
                   "anti_narcotics_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "anti_narcotics", "law", "verified")
RECORDS = os.path.join(OUT_VER, "anti_narcotics_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "anti_narcotics_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "anti_narcotics_arabic_legal_llm",
                        "anti_narcotics_law_legal_llm_001_074.json")

LAW_ID = "sa-anti-narcotics-law-m39-1426"
LAW_AR = "نظام مكافحة المخدرات والمؤثرات العقلية"
STATUS = "BOE_PROXY_X_NEZAMS_X_QADHA_REFERENCE_TRIPLE_VERIFIED"
KEY_RE = r"anti_narcotics_art_(\d{3})$"
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
        ver.append({"law_key": "anti_narcotics", "law_component": "law", "language": "ar",
                    "record_layer": "ANTI_NARCOTICS_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": is_amended, "is_added": False,
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track's primary source is "
                                              "the official BOE portal, extracted via the "
                                              "r.jina.ai proxy after direct WebFetch returned "
                                              "HTTP 503, then cross-verified word-for-word "
                                              "against nezams.com's independent raw-HTML "
                                              "transcription and (for the highest-stakes "
                                              "penalty articles) qadha.org.sa's published "
                                              "reference book — see verification_methodology_note "
                                              "in the source artifact for the full caveat."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": is_amended, "is_added": False,
                    "record_id": "anti-narcotics-law-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "anti_narcotics/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام مكافحة المخدرات والمؤثرات العقلية" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Decree — official BOE portal via "
                                                          "r.jina.ai proxy x nezams.com cross-"
                                                          "verification x qadha.org.sa reference "
                                                          "book (triple-verified for penalty "
                                                          "articles)"),
                                     "source_authority_ar": "مرسوم ملكي — بوابة هيئة الخبراء الرسمية (عبر وسيط r.jina.ai) بالتحقق المتقاطع مع نظم.كوم ومرجع قضاء.org.sa",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "anti_narcotics",
               "layer": "ANTI_NARCOTICS_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-anti-narcotics-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (74 مادة؛ جميعها أصلية)",
               "title_en": "Saudi Anti-Narcotics and Psychotropic Substances Control Law — Arabic LLM-ready layer (74 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 74], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Anti-Narcotics Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
