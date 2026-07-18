#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Finance Companies Control Law track (نظام مراقبة شركات
التمويل, Royal Decree M/51, 13/8/1433H).

VERIFICATION TIER -- STATUS constant
BOE_WAYBACK_ARCHIVE_X_BFC_GOV_PDF_X_NEZAMS_CROSS_VERIFIED_LIVE_BOE_503
reflects that laws.boe.gov.sa's LIVE portal was unreachable this pass
(HTTP 503 direct; HTTP 422 via r.jina.ai), matching this corpus's
established BOE-egress-blocked pattern -- BUT a Wayback Machine snapshot
of this exact BOE law page (2026-01-14) WAS reachable via direct curl,
and is treated as this track's PRIMARY source: it gives the full
verbatim original text of all 40 articles, the decree number/date, and a
tracked amendment annotation for Article 35. This was cross-verified
(programmatic, normalized, zero substantive discrepancies across all 40
original articles) against bfc.gov.sa's official PDF (OCR'd; a custom
subset font made raw pdftotext extraction unusable) and nezams.com's
clean HTML transcription (which also supplied the amendment-footnote
replacement text for every amended article, cross-checked against
qanoonsa.com's verbatim reproduction of Royal Decree M/272's actual
decree text, itself citing Umm al-Qura Gazette issue 5036, 28/6/2024).

41 records (40 articles + 1 مضافة): 28 اصلية / 12 معدلة / 1 مضافة across
THREE amendment waves -- M/21 (6/3/1440H, Article 5 only, partial gap
undocumented -- see known_unresolved_discrepancies), M/24 (15/3/1443H,
based on Council of Ministers Resolution 160, Article 35 only), and
M/272 (4/12/1445H, based on Council of Ministers Resolution 1016,
Articles 1, 5, 11, 12, 16, 17, 18, 19, 20, 21, 29, and the new Article
36 مكرر). See sources/finance_companies/law/official_source/
finance_companies_law_official_source.json for the full methodology
note and every documented unresolved discrepancy, including the
irrecoverable pre-1440H content of Article 5's deleted بند (خامساً),
and this track's decision NOT to ingest the companion Implementing
Regulation this pass (identified but not extracted -- 38 image-scanned
pages with its own independent, multi-wave amendment history).

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "finance_companies", "law", "official_source",
                   "finance_companies_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "finance_companies", "law", "verified")
RECORDS = os.path.join(OUT_VER, "finance_companies_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "finance_companies_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "finance_companies_arabic_legal_llm",
                        "finance_companies_law_legal_llm_001_041.json")

LAW_ID = "sa-finance-companies-control-law-m51-1433"
LAW_AR = "نظام مراقبة شركات التمويل"
STATUS = "BOE_WAYBACK_ARCHIVE_X_BFC_GOV_PDF_X_NEZAMS_CROSS_VERIFIED_LIVE_BOE_503"
KEY_RE = r"finance_companies_art_(\d{3})(?:_mukarrar(\d*))?$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك شركة التمويل شركات").split())


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
        text = a["text"]
        original_text = a.get("original_1433h_text") or a.get("original_1440h_text")
        ver.append({"law_key": "finance_companies", "law_component": "law", "language": "ar",
                    "record_layer": "FINANCE_COMPANIES_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "original_text": original_text,
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track rests on a BOE-via-"
                                              "Wayback-Machine archived snapshot as the PRIMARY "
                                              "source (live BOE unreachable, HTTP 503), cross-"
                                              "verified programmatically (zero substantive "
                                              "discrepancies) against bfc.gov.sa's official OCR'd "
                                              "PDF and nezams.com's HTML transcription; the 2024 "
                                              "amendment (Royal Decree M/272) text is qanoonsa.com's "
                                              "verbatim decree reproduction, cross-checked against "
                                              "nezams.com's footnotes. See verification_methodology_"
                                              "note and known_unresolved_discrepancies in the "
                                              "source artifact for full caveats, including the "
                                              "irrecoverable pre-1440H content of Article 5's "
                                              "deleted بند (خامساً), and that the companion "
                                              "Implementing Regulation is NOT ingested this pass."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "finance-companies-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "finance_companies/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام مراقبة شركات التمويل" % a["number_label_ar"]],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Decree M/51 — laws.boe.gov.sa "
                                                          "via Wayback Machine archive (primary), "
                                                          "cross-verified against bfc.gov.sa "
                                                          "official PDF and nezams.com; live BOE "
                                                          "unreachable (HTTP 503) this pass"),
                                     "source_authority_ar": "مرسوم ملكي رقم (م/51) — نسخة أرشيفية من بوابة هيئة الخبراء عبر Wayback Machine، مطابقة مع ملف بي إف سي الرسمي ونزامز.كوم",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "finance_companies",
               "layer": "FINANCE_COMPANIES_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-finance-companies-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (41 مادة؛ 28 أصلية، 12 معدّلة، 1 مضافة)",
               "title_en": "Saudi Finance Companies Control Law — Arabic LLM-ready layer (41 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 40], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Finance Companies Control Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
