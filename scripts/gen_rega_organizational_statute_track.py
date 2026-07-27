#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Statute of the General Authority for Real Estate track
(تنظيم الهيئة العامة للعقار, Council of Ministers Resolution No. 239,
25/4/1438H, amended by Resolutions 693/1441H, 69/1443H, 426/1443H and
16/1447H).

VERIFICATION TIER -- see sources/rega_organizational_statute/law/
official_source/rega_organizational_statute_official_source.json's
verification_methodology_note for the full account. Summary:

PRIMARY SOURCE: REGA's own official website (rega.gov.sa), which hosts the
base statute and all four amendment decrees as directly-downloadable scanned
PDFs. UNLIKE several sibling tracks in this corpus, laws.boe.gov.sa (HTTP 503
every attempt) and the Wayback Machine (confirmed blocked at the tool/network
level this pass, not merely unattempted) were both unavailable this pass --
this track rests on a different verification tier than its BOE-Wayback-
sourced siblings, honestly documented rather than silently upgraded.

ALL FIVE PDFs ARE SCANNED IMAGES WITH NO TEXT LAYER (confirmed via
pdftotext and PyMuPDF both returning zero characters). Per this track's task
brief and this corpus's contractors_classification_law/
high_risk_professions_regulation precedent, no OCR tool was invoked --
every page was rendered to a 200 DPI PNG and read directly by this pass.

FOUR CONFIRMED AMENDMENTS, safely reconstructable (unlike this corpus's
tvtc_organizational_statute Article 4 precedent, where layered partial
'add a seat, no stated position' amendments could NOT be safely merged):
  - Article 4 paragraph 1 (board composition) was fully replaced THREE
    times in succession (Resolutions 693/partial, 69/complete, 16/complete);
    since Resolutions 69 and 16 are each a complete, self-contained
    substitution of the whole paragraph, this track safely ingests
    Resolution 16's text (the chronologically last complete substitution)
    as the current text, with the superseded intermediate texts recorded
    in history without merging.
  - Articles 1, 5, 6, 9 and 13bis: renamed المحافظ -> الرئيس التنفيذي
    (Resolution 426) and/or received clean, fully-numbered paragraph
    substitutions/additions (Resolutions 69/426) -- none required this
    track to invent an unstated insertion point.
  - Article 8: fully replaced (Resolution 426) -- CEO now appointed by
    Board resolution on the Chairman's nomination, replacing the original
    Royal Order appointment mechanism.
  - Article 3: صدر and paragraphs 4/6 replaced, paragraphs 19-20 added
    (Resolution 69) -- adds 'التسجيل العيني للعقارات' to the Authority's
    primary purpose.
  - Article 11/1/ج: one clause amended (Resolution 69, inserting
    'وفقاً للأنظمة').

16 records: 7 اصلية, 8 معدلة, 0 ملغاة, 1 مضافة (Article 13bis). Flat
structure, no أبواب/فصول. No inline per-article titles in the source -- no
title_ar field is used.

A CONFIRMED, UNRESOLVED TEXTUAL INCONSISTENCY is carried forward honestly:
Article 1's own definition of 'الوزير' still reads 'وزير الإسكان' verbatim,
never textually updated by any of the four amendment decrees read this
pass, even though Article 4's own government-body list has since been
completely replaced twice with a renamed ministry. See
known_unresolved_discrepancies, key rega_article1_wazir_definition_not_
updated_confirmed_gap.

No legal text is altered beyond whitespace normalization needed to render
the scanned PDFs' visual layout as plain sequential text, and splicing each
amendment decree's own quoted replacement text into the position its own
operative clause specifies. Arabic governs; no translation/paraphrase/
interpretation performed on the Arabic text. Read-only over input;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "rega_organizational_statute", "law", "official_source",
                   "rega_organizational_statute_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "rega_organizational_statute", "law", "verified")
RECORDS = os.path.join(OUT_VER, "rega_organizational_statute_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "rega_organizational_statute_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "rega_organizational_statute_arabic_legal_llm",
                        "rega_organizational_statute_legal_llm_001_016.json")

LAW_ID = "sa-rega-organizational-statute-239-1438"
LAW_AR = "تنظيم الهيئة العامة للعقار"
TOP_STATUS = ("MIXED_TIER_SEE_PER_ARTICLE_STATUS_REGA_OWN_SITE_SCANNED_PDF_DIRECT_VISUAL_READ_"
              "X_NEZAMS_COM_PARTIAL_CROSSCHECK_LIVE_BOE_AND_WAYBACK_BOTH_UNREACHABLE_THIS_PASS")
KEY_RE = r"rega_organizational_statute_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = {
    "rega_organizational_statute_art_001",
    "rega_organizational_statute_art_003",
    "rega_organizational_statute_art_004",
    "rega_organizational_statute_art_005",
    "rega_organizational_statute_art_006",
    "rega_organizational_statute_art_008",
    "rega_organizational_statute_art_009",
    "rega_organizational_statute_art_011",
}
ADDED_KEYS = {"rega_organizational_statute_art_013_mukarrar"}
REPEALED_KEYS = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام التنظيم اللائحة أحكام يجب يجوز "
            "عليه دون فيما منه منها وإذا حال وله ولها الهيئة المجلس الرئيس بوجه خاص").split())


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
        ver.append({"law_key": "rega_organizational_statute", "law_component": "law",
                    "language": "ar",
                    "record_layer": "REGA_ORGANIZATIONAL_STATUTE_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": TOP_STATUS,
                    "governing_source_note": ("Arabic governs; this track rests PRIMARILY on "
                                              "REGA's own official website (rega.gov.sa), which "
                                              "hosts the base statute and all four amendment "
                                              "decrees as directly-downloadable scanned PDFs "
                                              "(no text layer -- read via direct visual "
                                              "transcription of 200 DPI page renders, not OCR). "
                                              "laws.boe.gov.sa (HTTP 503) and the Wayback Machine "
                                              "(confirmed blocked at the tool/network level) were "
                                              "both unavailable this pass -- see "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track's tier as "
                                              "equivalent to this corpus's BOE-Wayback-sourced "
                                              "sibling tracks. Article 4 paragraph 1 was fully "
                                              "replaced three times in succession (Resolutions "
                                              "693, 69, 16); this record carries Resolution 16's "
                                              "own complete text (the chronologically last "
                                              "complete substitution), safely superseding the "
                                              "earlier complete/partial texts without merging."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "rega-organizational-statute-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "rega_organizational_statute/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من تنظيم الهيئة العامة للعقار" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Council of Ministers Resolution No. "
                                                          "(239), 25/4/1438H — rega.gov.sa's own "
                                                          "hosted scanned PDFs (base statute + "
                                                          "four amendment decrees), direct visual "
                                                          "read; live BOE (HTTP 503) and the "
                                                          "Wayback Machine (blocked) both "
                                                          "unreachable this pass; nezams.com "
                                                          "partial cross-check"),
                                     "source_authority_ar": "قرار مجلس الوزراء رقم (239) وتاريخ 25/4/1438هـ — ملفات PDF ممسوحة ضوئياً مستضافة على موقع الهيئة العامة للعقار ذاته (rega.gov.sa)، قُرئت بصرياً مباشرة؛ تعذّر الوصول لهيئة الخبراء المباشرة (503) ولأرشيف Wayback (محظور) هذه الجولة؛ مطابقة جزئية مع nezams.com",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "rega_organizational_statute",
               "layer": "REGA_ORGANIZATIONAL_STATUTE_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": TOP_STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-rega-organizational-statute-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (16 مادة؛ 7 أصلية و8 معدلة ومادة واحدة مضافة)",
               "title_en": "Statute of the General Authority for Real Estate — Arabic LLM-ready layer (16 records: 7 original, 8 amended, 1 added)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 15], "text_status": TOP_STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready REGA Organizational Statute records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
