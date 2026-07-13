#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Commercial Papers Law track (نظام الأوراق التجارية م/37).

Source: the official text published by the Bureau of Experts at the Council of
Ministers (laws.boe.gov.sa). The BOE portal is not directly reachable from the
build environment, so the consolidated text was captured from the Wayback
Machine archive of the official BOE LawDetails page and CROSS-VERIFIED across two
independent-date snapshots (2021 + 2025): all 121 current article bodies are
byte-identical between them (zero differences). Both raw snapshots are committed
under inputs/commercial_papers_boe_snapshots/ with recorded sha256, and the
concatenated corpus text carries a recorded sha256 in the source artifact.

Royal Decree M/37 dated 11/10/1383H (24/2/1964). IN FORCE (ساري). Consolidated:
118 اصلية / 3 معدلة (arts 118, 119, 120, amended by Royal Decree M/45 dated
12/9/1409H — each carries the current amended text and its original 1383H text in
amendment_history) / 0 ملغاة / 0 مضافة. Article 38 is recorded with its ORIGINAL
text (اصلية); an official interpretation (Council of Ministers Decision No. 251,
23/4/1442H) of the phrase «لدى الاطلاع» is preserved in its history — the article
text itself was not changed. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "commercial_papers", "law", "official_source",
                   "commercial_papers_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "commercial_papers", "law", "verified")
RECORDS = os.path.join(OUT_VER, "commercial_papers_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "commercial_papers_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "commercial_papers_arabic_legal_llm",
                        "commercial_papers_law_legal_llm_001_121.json")

LAW_ID = "sa-commercial-papers-law-m37-1383"
LAW_AR = "نظام الأوراق التجارية"
STATUS = "BOE_OFFICIAL_PORTAL_ARCHIVE_CROSS_SNAPSHOT_VERIFIED"
KEY_RE = r"commercial_papers_art_(\d{3})(_mukarrar)?$"
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
        ver.append({"law_key": "commercial_papers", "law_component": "law", "language": "ar",
                    "record_layer": "COMMERCIAL_PAPERS_LAW_ARABIC_VERIFIED_TEXT",
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
                    "record_id": "commercial-papers-law-llm-art-%03d%s" % (n, suffix),
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s%s" % (LAW_AR, a["number_label_ar"],
                                                   " (ملغاة)" if is_repealed else ""),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "commercial_papers/law/articles/%03d%s" % (n, suffix),
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام الأوراق التجارية" % n],
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
    json.dump({"law_key": "commercial_papers", "layer": "COMMERCIAL_PAPERS_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "archive_snapshots": src["provenance"]["archive_snapshots"],
               "corpus_text_sha256": src["provenance"]["corpus_text_sha256"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-commercial-papers-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (121 مادة؛ نص موحّد: 118 أصلية، 3 معدّلة)",
               "title_en": "Saudi Commercial Papers Law — Arabic LLM-ready layer (121 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 121], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Commercial Papers Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
