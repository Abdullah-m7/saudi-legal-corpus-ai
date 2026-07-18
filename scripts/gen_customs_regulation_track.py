#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the customs_regulation track (اللائحة التنفيذية لنظام (قانون)
الجمارك الموحد لدول مجلس التعاون لدول الخليج العربية -- Implementing
Regulation of the GCC Unified Customs Law, Ministerial/Committee
Resolution No. 2748, 25/11/1423H; amended 6 times by Resolutions 2997,
3766, 939, 986, 955, 1374, none individually attributable to specific
articles from the available source -- see known_unresolved_discrepancies).

SINGLE-SOURCE TIER -- STATUS constant
ZATCA_PDF_PRIMARY_SINGLE_SOURCE_BOE_UNREACHABLE, shared with the
customs_law track (both were extracted from the SAME ZATCA consolidated
PDF and cleaned with the SAME ligature/lam-drop/tanwin/paren-order
normalizer -- see customs_law_official_source.json's
verification_methodology_note for the shared fix methodology).
laws.boe.gov.sa was retried this pass for this Regulation specifically and
confirmed unreachable (curl: connection reset; WebFetch: HTTP 503).

Article 1 (Book 1) is a single, very long article covering customs
valuation methodology with internal ordinal-clause structure (أولاً
through ثامناً) plus an interpretive annex -- preserved whole, not split.
Three Books (3, 6, 7) had a substantive legal-basis chapeau paragraph
relocated from stray mid-heading placement to their first article's body
(Articles 14, 26, 29). All fixes and gaps are recorded in
customs_regulation_official_source.json's verification_methodology_note
and known_unresolved_discrepancies -- this script performs NO further
text transformation.

No legal text is altered by this script. Arabic governs; no translation/
paraphrase/interpretation. Read-only over input; deterministic over
outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "customs", "regulation", "official_source",
                   "customs_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "customs", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "customs_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "customs_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "customs_regulation_arabic_legal_llm",
                        "customs_regulation_legal_llm_001_036.json")

LAW_ID = "sa-customs-regulation-res2748-1423"
LAW_AR = "اللائحة التنفيذية لنظام (قانون) الجمارك الموحد لدول مجلس التعاون لدول الخليج العربية"
STATUS = "ZATCA_PDF_PRIMARY_SINGLE_SOURCE_BOE_UNREACHABLE"
KEY_RE = r"customs_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة النظام القانون أحكام يجب يجوز "
            "عليه دون فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك هذه الجمركية الجمارك "
            "البضاعة البضائع").split())


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
        n = a["article_number"]
        is_mukarrar = bool(a.get("is_mukarrar"))
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        text = a["text"]
        ver.append({"law_key": "customs", "law_component": "regulation", "language": "ar",
                    "record_layer": "CUSTOMS_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "mukarrar_suffix": a.get("mukarrar_suffix"),
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "title_ar": a.get("title_ar", ""),
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "original_1423h_text": a.get("original_1423h_text"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track rests on ZATCA's "
                                              "own official consolidated PDF as the sole "
                                              "full-text primary source (single-source "
                                              "tier), shared with the customs_law track. "
                                              "See verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact for the full caveats, including that "
                                              "none of this Regulation's 6 amendments could "
                                              "be attributed to specific articles, and "
                                              "Article 1's exceptional length/table content "
                                              "carries a higher residual line-wrap-artifact "
                                              "risk than this track's other 35 articles."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "mukarrar_suffix": a.get("mukarrar_suffix"),
                    "article_key": key,
                    "article_title_ar": a["number_label_ar"] + (" — " + a["title_ar"] if a.get("title_ar") else ""),
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "customs-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s: %s" % (LAW_AR, a["number_label_ar"], a.get("title_ar", "")),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "customs/regulation/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s اللائحة التنفيذية للجمارك" % a["number_label_ar"],
                                          "اللائحة التنفيذية لنظام الجمارك الموحد %s" % a["number_label_ar"],
                                          "%s من اللائحة التنفيذية لنظام الجمارك الموحد" % a["number_label_ar"]],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Ministerial/Committee Resolution 2748 — "
                                                          "ZATCA official consolidated PDF (sole "
                                                          "primary source); laws.boe.gov.sa "
                                                          "confirmed unreachable"),
                                     "source_authority_ar": "قرار وزاري رقم (2748) — ملف PDF الرسمي الموحد لهيئة الزكاة والضريبة والجمارك (ZATCA)، المصدر الأساسي الوحيد",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "customs",
               "layer": "CUSTOMS_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-customs-regulation-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (36 مادة؛ 34 أصلية، 2 مضافة)",
               "title_en": "Implementing Regulation of the GCC Unified Customs Law — Arabic LLM-ready layer (36 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 34], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Customs Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
