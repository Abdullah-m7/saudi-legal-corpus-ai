#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation ("Executive List") of the
Anti-Narcotics and Psychotropic Substances Control Law track
(اللائحة التنفيذية لنظام مكافحة المخدرات والمؤثرات العقلية, Council of
Ministers Resolution No. 201, 10/6/1431H / 24 May 2010 CE).

DISTINCT, LOWER VERIFICATION TIER than the base law (anti_narcotics,
BOE_PROXY_X_NEZAMS_X_QADHA_REFERENCE_TRIPLE_VERIFIED) — disclosed
honestly rather than overstated. The official BOE portal
(laws.boe.gov.sa, lawId be479758-9a84-4e94-b1d3-a9a700f19454), the MOI
PDF ("Executive list for drugs.pdf"), and a Wayback Machine snapshot of
the BOE page were all attempted and ALL failed (BOE/MOI: HTTP 503 via
WebFetch and "Recv failure: Connection reset by peer" via direct curl;
Wayback: content-serving host blocked by sandbox egress policy, though
its "available" API confirmed a snapshot exists). The PRIMARY source
actually used is nezams.com's dedicated regulation page, fetched via
direct curl with a browser User-Agent (it 406s bot-like requests, 200s
browser-like ones) and parsed programmatically (regex tag-stripping +
HTML-entity unescaping + a dedicated HTML-<table>-to-linearized-text
converter for the two articles, 2 and 34, that embed drug/dosage
tables) -- no LLM summarization was used for extraction. This is a
SINGLE full-text primary source: qistas.com independently matched only
the enacting Council of Ministers resolution's PREAMBLE (word-for-word,
save for digit style) -- not any of the 40 مواد themselves -- and
almehleky.sa (a law-firm blog) gave only topical, non-verbatim
corroboration for 3 of the 40 articles (2, 20, 34). A fourth fallback,
a combined law+regulation PDF at zarah.com.sa, was fetched but rejected
as unusable: its text extraction exhibits systematic Arabic
ligature/digit-reversal corruption, AND it does not actually contain
the regulation's text at all (it stops at the base law's Article 74).

See sources/anti_narcotics_regulation/law/official_source/
anti_narcotics_regulation_official_source.json for the full methodology
note and every documented discrepancy.

STRUCTURE: exactly 40 مواد (articles), numbered 1-40, in a flat
sequence -- no باب/فصل structure and (unlike the base law) NO
unnumbered topical section headers either; nezams.com groups all 40
under one undifferentiated "المواد" heading. This Regulation is NOT
organized as a standalone substance schedule/قائمة at the top level,
despite its colloquial name -- the substance/dosage tables that do
exist are embedded within two of the 40 numbered مواد (Articles 2 and
34) and are linearized here as "[جدول]\\nrow | row\\n[/جدول]" blocks,
a structural/formatting transform only, not a paraphrase. All 40
articles are أصلية (unamended) per nezams.com's own page metadata
("التعديلات: لم يجر عليها تعديل") and an absence of any amending
instrument found via WebSearch.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "anti_narcotics_regulation", "law",
                   "official_source",
                   "anti_narcotics_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "anti_narcotics_regulation", "law",
                       "verified")
RECORDS = os.path.join(OUT_VER, "anti_narcotics_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "anti_narcotics_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "anti_narcotics_regulation_arabic_legal_llm",
                        "anti_narcotics_regulation_legal_llm_001_040.json")

LAW_ID = "sa-anti-narcotics-regulation-com201-1431"
LAW_AR = "اللائحة التنفيذية لنظام مكافحة المخدرات والمؤثرات العقلية"
STATUS = "NEZAMS_HTML_SINGLE_FULLTEXT_X_QISTAS_PREAMBLE_PARTIAL_MATCH"
KEY_RE = r"anti_narcotics_regulation_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة اللائحة النظام أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك جدول").split())


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
        ver.append({"law_key": "anti_narcotics_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "ANTI_NARCOTICS_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": is_amended, "is_added": False,
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track's SOLE full-text primary "
                                              "source is nezams.com (fetched via direct curl with a "
                                              "browser User-Agent, no LLM summarization), because the "
                                              "official BOE portal, the MOI PDF, and a Wayback Machine "
                                              "snapshot were all attempted and all failed. Only the "
                                              "enacting resolution's preamble (not the article text "
                                              "itself) was independently cross-matched, via qistas.com "
                                              "-- a materially lower verification tier than the base "
                                              "law's triple-verified tier, disclosed in full in the "
                                              "source artifact's verification_methodology_note."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": is_amended, "is_added": False,
                    "record_id": "anti-narcotics-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "anti_narcotics_regulation/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d اللائحة التنفيذية لنظام مكافحة المخدرات" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Council of Ministers Resolution No. 201 "
                                                          "(10/6/1431H) -- SINGLE full-text primary "
                                                          "source (nezams.com, direct curl, browser "
                                                          "User-Agent) x qistas.com preamble-only "
                                                          "partial match; official BOE portal, MOI PDF, "
                                                          "and Wayback Machine all unreachable"),
                                     "source_authority_ar": "قرار مجلس الوزراء رقم (201) — مصدر نصي كامل وحيد (نظم.كوم) مع تطابق جزئي لديباجة القرار عبر قسطاس.كوم؛ تعذر الوصول لبوابة هيئة الخبراء وملف وزارة الداخلية وأرشيف Wayback",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "anti_narcotics_regulation",
               "layer": "ANTI_NARCOTICS_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "decree_date_gregorian": src.get("decree_date_gregorian"),
               "publication_date_hijri": src.get("publication_date_hijri"),
               "publication_date_gregorian": src.get("publication_date_gregorian"),
               "base_law_reference": src.get("base_law_reference"),
               "consolidated_amended_law": False,
               "structural_note": src.get("structural_note"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-anti-narcotics-regulation-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (40 مادة؛ جميعها أصلية)",
               "title_en": ("Saudi Anti-Narcotics and Psychotropic Substances Control Law -- "
                            "Implementing Regulation ('Executive List') -- Arabic LLM-ready layer "
                            "(40 records)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 40], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Anti-Narcotics Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
