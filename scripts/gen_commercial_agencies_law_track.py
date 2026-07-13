#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Commercial Agencies Law track (نظام الوكالات التجارية م/11).

Source: the official text of the Bureau of Experts at the Council of Ministers
(laws.boe.gov.sa), captured from the Wayback Machine archive and CROSS-VERIFIED
across two independent-date snapshots (2023 + 2025): all 6 current article bodies
are byte-identical (zero differences). Both raw snapshots are committed under
inputs/commercial_agencies_boe_snapshots/ with recorded sha256, and the
concatenated corpus text carries a recorded sha256.

Royal Decree M/11 dated 20/2/1382H. IN FORCE (ساري). Consolidated: 3 اصلية /
3 معدلة (arts 4, 5, 6) / 0 ملغاة / 0 مضافة. Art 4 amended by M/32 (1400H) and
art 5 by M/8 (1393H) — each carries the current amended text and its original in
amendment_history. Art 6's own text was not replaced; M/5 (1389H) ADDED a
penalties-enforcement committee (recorded in art 6 history); BOE flags art 6 as
amended and the body is recorded exactly as BOE displays it. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "commercial_agencies", "law", "official_source",
                   "commercial_agencies_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "commercial_agencies", "law", "verified")
RECORDS = os.path.join(OUT_VER, "commercial_agencies_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "commercial_agencies_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "commercial_agencies_arabic_legal_llm",
                        "commercial_agencies_law_legal_llm_001_006.json")

LAW_ID = "sa-commercial-agencies-law-m11-1382"
LAW_AR = "نظام الوكالات التجارية"
STATUS = "BOE_OFFICIAL_PORTAL_ARCHIVE_CROSS_SNAPSHOT_VERIFIED"
KEY_RE = r"commercial_agencies_art_(\d{3})(_mukarrar)?$"
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
    return (int(m.group(1)), 1 if m.group(2) else 0)


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
        n, is_muk = int(m.group(1)), bool(m.group(2))
        suffix = "-mukarrar" if is_muk else ""
        ls = a.get("legal_status_ar")
        is_repealed = ls == "ملغاة"
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        text = a["text"]
        hist = a.get("history")
        ver.append({"law_key": "commercial_agencies", "law_component": "law", "language": "ar",
                    "record_layer": "COMMERCIAL_AGENCIES_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_muk, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": hist,
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; official BOE (Bureau of Experts) text "
                                              "cross-verified across two independent-date archive snapshots; "
                                              "amendment status flagged (see source artifact)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_muk, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "commercial-agencies-law-llm-art-%03d%s" % (n, suffix),
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s%s" % (LAW_AR, a["number_label_ar"],
                                                   " (ملغاة)" if is_repealed else ""),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "commercial_agencies/law/articles/%03d%s" % (n, suffix),
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام الوكالات التجارية" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": "Bureau of Experts at the Council of Ministers — official legislative portal",
                                     "source_authority_ar": "هيئة الخبراء بمجلس الوزراء — البوابة الرسمية للأنظمة",
                                     "source_status": "boe_official_portal_archive_cross_snapshot_verified",
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "commercial_agencies", "layer": "COMMERCIAL_AGENCIES_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "archive_snapshots": src["provenance"]["archive_snapshots"],
               "corpus_text_sha256": src["provenance"]["corpus_text_sha256"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-commercial-agencies-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (6 مواد؛ نص موحّد: 3 أصلية، 3 معدّلة)",
               "title_en": "Saudi Commercial Agencies Law — Arabic LLM-ready layer (6 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 6], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Commercial Agencies Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
