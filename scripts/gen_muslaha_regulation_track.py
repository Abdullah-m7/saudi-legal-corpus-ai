#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Rules for the Work of Conciliation Offices and its Procedures
(قواعد العمل في مكاتب المصالحة وإجراءاته).

Source: the official MOJ legal-portal text (Minister of Justice Decision 5595,
29/11/1440H), fetched article-by-article (get-Section-Changes) and
cross-verified against the official MOJ PDF (24/26 numbered articles matched
outright, mean 0.9464, min 0.627; articles 1 and 26 fell below the automated
floor and were adjudicated visually verbatim on the rendered pages). This
regulation is IN FORCE, replacing the prior Ministerial Decision 53792
(27/7/1435H) rules per its own final article (26). FRESH FULL ISSUANCE: all
26 numbered records اصلية (0 معدلة / 0 ملغاة / 0 مضافة).

In addition to the 26 numbered articles, the official source carries a 3-part
case-category schedule (annex) listing maximum conciliation-session timelines
by case type (General, Personal Status, Criminal) — 17 rows total, each
verified row-for-row against the rendered official PDF pages (table-extraction
noise put all 3 tables below the automated floor; every row was confirmed
visually verbatim).

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "muslaha", "regulation", "official_source",
                   "muslaha_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "muslaha", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "muslaha_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "muslaha_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "muslaha_arabic_legal_llm",
                        "muslaha_regulation_legal_llm_001_029.json")

LAW_ID = "sa-muslaha-regulation-5595-1440"
LAW_AR = "قواعد العمل في مكاتب المصالحة وإجراءاته"
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
KEY_RE = r"muslaha_art_(\d{3})$"
N_ART = 26
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


def _table_text(category_ar, columns, rows):
    """Deterministic mechanical linearization of a printed schedule table.

    Every cell verbatim from the source artifact; only column labels and
    separators added.
    """
    lines = [category_ar]
    for row in rows:
        cells = ["%s: %s" % (columns[i], row[i]) for i in range(len(columns)) if str(row[i]).strip()]
        lines.append(" | ".join(cells))
    return "\n".join(lines)


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    tables = src["annex_tables"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for key in keys:
        a = arts[key]
        n = int(re.match(KEY_RE, key).group(1))
        ls = a.get("legal_status_ar")
        text = a["text"]
        ver.append({"law_key": "muslaha", "law_component": "regulation", "language": "ar",
                    "record_layer": "MUSLAHA_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "pdf_similarity": a.get("pdf_similarity"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; official MOJ text cross-verified against "
                                              "the official MOJ PDF (verbatim; low-similarity articles "
                                              "adjudicated visually on the rendered pages)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "record_id": "muslaha-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "muslaha/regulation/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d قواعد العمل في مكاتب المصالحة" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": "Ministry of Justice (MOJ) — official legal portal",
                                     "source_authority_ar": "وزارة العدل — المنصة القانونية الرسمية",
                                     "source_status": "moj_portal_api_cross_checked_official_pdf",
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    for i, tkey in enumerate(sorted(tables), start=N_ART + 1):
        t = tables[tkey]
        text = _table_text(t["category_ar"], t["columns"], t["rows"])
        ver.append({"law_key": "muslaha", "law_component": "regulation", "language": "ar",
                    "record_layer": "MUSLAHA_REGULATION_ANNEX_TABLE_VERIFIED",
                    "article_key": tkey, "article_number": i, "is_mukarrar": False,
                    "number_label_ar": t["category_ar"],
                    "section_ar": "الجدول الملحق - آجال إجراءات المصالحة حسب نوع القضية",
                    "article_text_verified": text,
                    "verification_status": t["status"],
                    "legal_status_ar": t.get("legal_status_ar"),
                    "row_count": len(t["rows"]),
                    "table_linearization_note": ("Mechanical linearization of the printed schedule table: "
                                                 "every cell verbatim; only column labels and separators "
                                                 "added."),
                    "pdf_similarity": t.get("pdf_similarity"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; every row checked verbatim against the "
                                              "rendered official MOJ PDF pages."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation",
                    "article_key": tkey, "article_number": i, "is_mukarrar": False,
                    "article_title_ar": t["category_ar"],
                    "section_ar": "الجدول الملحق - آجال إجراءات المصالحة حسب نوع القضية",
                    "legal_status_ar": t.get("legal_status_ar"),
                    "record_id": "muslaha-regulation-llm-%s" % tkey,
                    "record_type": "verified_arabic_table", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "row_count": len(t["rows"]),
                    "llm_title_ar": "%s — الجدول الملحق — %s" % (LAW_AR, t["category_ar"]),
                    "retrieval_title_ar": "%s - الجدول الملحق - %s" % (LAW_AR, t["category_ar"]),
                    "article_path": "muslaha/regulation/annex_tables/%s" % tkey,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["الجدول الملحق قواعد العمل في مكاتب المصالحة %s" % t["category_ar"],
                                          "آجال إجراءات المصالحة %s" % t["category_ar"],
                                          "%s قواعد العمل في مكاتب المصالحة" % t["category_ar"]],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": "Ministry of Justice (MOJ) — official legal portal",
                                     "source_authority_ar": "وزارة العدل — المنصة القانونية الرسمية",
                                     "source_status": "moj_portal_api_cross_checked_official_pdf",
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": t.get("legal_status_ar"),
                                     "verification_status": t["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "muslaha", "layer": "MUSLAHA_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": False,
               "visually_adjudicated": src["stats"]["visually_adjudicated"],
               "annex_tables": len(tables),
               "annex_table_rows": sum(len(t["rows"]) for t in tables.values()),
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-muslaha-regulation-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (26 مادة + جدول ملحق من 3 أقسام؛ إصدار جديد كامل)",
               "title_en": "Saudi Rules for the Work of Conciliation Offices and its Procedures — Arabic LLM-ready layer (29 records: 26 articles + 3 annex tables)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 26], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Rules for the Work of Conciliation Offices records "
          "(26 articles + 3 annex tables)" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
