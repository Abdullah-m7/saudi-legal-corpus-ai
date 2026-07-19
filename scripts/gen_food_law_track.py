#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Food Law track (نظام الغذاء, Royal Decree M/1,
6/1/1436H / 30 Oct 2014G).

VERIFICATION TIER -- see sources/food/law/official_source/
food_law_official_source.json's verification_methodology_note for the full
account. Summary:

PRIMARY SOURCE ACCESS FAILED MORE SEVERELY THAN THIS CORPUS'S USUAL PATTERN:
laws.boe.gov.sa's live portal was unreachable this pass (503 / connection
reset, both via direct curl and via WebFetch, against both the LawDetails
page and its own hosted English-translation PDF). UNLIKE this corpus's usual
fallback, the Wayback Machine was ALSO unreachable: archive.org's own
'/wayback/available' lookup confirmed a snapshot exists, but the actual
snapshot-content host, web.archive.org, was blocked outright by this
session's egress policy (both via direct curl and via the WebFetch tool).

ACTUAL SOURCE USED: an official SFDA-published PDF (اللائحة التنفيذية لنظام
الغذاء, https://www.sfda.gov.sa/sites/default/files/2021-04/...pdf) that
interleaves this base law's own articles (bordered boxes, bare spelled-
ordinal headers) with its Implementing Regulation's own articles (unboxed,
numeric headers suffixed "من اللائحة"). Every one of the 44 recovered
articles' text was independently visually read from a 400dpi render of each
of the document's 41 pages (an initial Tesseract OCR pass was used only for
triage -- it was found to silently drop at least one entire bordered box,
Article 4, confirmed recovered only by direct visual reading).

44 of this law's 45 total articles recovered (Articles 2-45); Article 1
(تعريفات/definitions) is NOT reproduced anywhere in the SFDA source document
and could not be verified from any other fetchable source to verbatim
standard -- EXCLUDED per this corpus's standing instruction, not fabricated.

44 records: 44 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة (absence-of-evidence finding
only -- BOE's own amendment changelog, this corpus's definitive amendment-
detection source, was completely inaccessible this pass). 12 chapters (فصول)
confirmed, matching aggregated WebSearch results describing BOE's own
translation title ("45 articles divided in XII Chapters"). Chapters 4 and 5
share an IDENTICAL title ("تداول الغذاء") in the source itself -- a genuine
anomaly, preserved verbatim, not silently renamed.

REPEAL FINDING: Article 45 (final article) carries ONLY a generic,
non-specific repeal clause ("يلغي كل ما يتعارض معه من أحكام") -- no named
predecessor food-safety law is identified anywhere in the recovered text.
Confirmed negative finding for this pass's supersession-graph question.

COMPANION INSTRUMENT NOT INGESTED: اللائحة التنفيذية لنظام الغذاء (this law's
own Implementing Regulation, ~85 articles across 12 chapters, amended
repeatedly at SFDA Board level -- e.g. Board Decisions 4/44, 4/48, 5/44, the
last reported by okaz.com.sa around 8 May 2026G) is NOT ingested this pass
(one-law-per-pass rule; also materially higher amendment churn and article
count than the base law).

No legal text is altered beyond whitespace normalization. Arabic governs; no
translation/paraphrase/interpretation. Read-only over input; deterministic
over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "food", "law", "official_source",
                   "food_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "food", "law", "verified")
RECORDS = os.path.join(OUT_VER, "food_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "food_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "food_arabic_legal_llm",
                        "food_law_legal_llm_001_044.json")

LAW_ID = "sa-food-law-m1-1436"
LAW_AR = "نظام الغذاء"
STATUS_UNCHANGED = ("SFDA_PDF_VISUAL_TRANSCRIPTION_SINGLE_SOURCE_LIVE_BOE_AND_"
                    "WAYBACK_BOTH_UNREACHABLE")
KEY_RE = r"food_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = set()
ADDED_KEYS = set()
REPEALED_KEYS = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك الغذاء الغذائية الغذائي الهيئة").split())


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
        ver.append({"law_key": "food", "law_component": "law",
                    "language": "ar",
                    "record_layer": "FOOD_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": top_status,
                    "governing_source_note": ("Arabic governs; this track rests on ONE "
                                              "official/primary source (an SFDA-published "
                                              "PDF combining this base law's own text with "
                                              "its Implementing Regulation, visually "
                                              "transcribed page-by-page this pass), since "
                                              "laws.boe.gov.sa was completely unreachable "
                                              "this pass -- both its live portal (503 / "
                                              "connection reset) AND the Wayback Machine "
                                              "(web.archive.org blocked by egress policy). "
                                              "Cross-checked against saudipedia.com (exact "
                                              "Gregorian-date match), FAOLEX metadata (decree "
                                              "identity and 180-day commencement clause), and "
                                              "aggregated WebSearch results describing BOE's "
                                              "own hosted English-translation title (45 "
                                              "articles, XII chapters) -- but NOT independently "
                                              "cross-verified word-for-word against a second "
                                              "full-text copy of the law. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track's text."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "food-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "food/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام الغذاء" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree M/1 (6/1/1436H) — "
                                                          "SFDA-published PDF, visually "
                                                          "transcribed page-by-page this "
                                                          "pass; laws.boe.gov.sa (live and "
                                                          "via Wayback Machine) completely "
                                                          "unreachable this pass"),
                                     "source_authority_ar": "المرسوم الملكي رقم (م/1) وتاريخ 6/1/1436هـ — نص مستخرج بصرياً من وثيقة رسمية صادرة عن الهيئة العامة للغذاء والدواء؛ بوابة هيئة الخبراء (مباشرة وعبر أرشيف Wayback) غير متاحة هذه الجولة",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "food",
               "layer": "FOOD_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "article_count": src["article_count"],
               "total_articles_in_law": src.get("total_articles_in_law"),
               "excluded_article_numbers": src.get("excluded_article_numbers", []),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-food-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (44 مادة من أصل 45؛ المادة الأولى مستبعدة)",
               "title_en": "Saudi Arabian Food Law — Arabic LLM-ready layer (44 of 45 articles; Article 1 excluded)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [2, 45], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Food Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
