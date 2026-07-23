#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Real Estate Transaction Tax Law track
(نظام ضريبة التصرفات العقارية, Royal Decree M/84, 19/3/1446H).

VERIFICATION TIER — full verbatim Arabic text of all 20 articles taken
from the laws.boe.gov.sa (BOE portal) lawId page
eef585a5-c63a-4906-a951-b208009b3eff, reached via the r.jina.ai read-proxy
after the live page returned HTTP 503 (the same primary-source channel this
corpus's VAT and income-tax ZATCA tracks used). The decree number/date,
the total article count (20), the flat structure (no chapter/فصل/باب
subdivisions), and the final article number were independently
cross-verified against nezams.com and qanoonsa.com. The Wayback Machine is
blocked at the network layer in this environment and was not part of this
track's verification chain.

See sources/rett/law/official_source/rett_law_official_source.json for the
full methodology note and all documented findings, including: (1) the
generic (NOT named) repeal in Article 20(2); (2) the predecessor royal
order (الأمر الملكي رقم أ/84 وتاريخ 14/2/1442هـ) that first imposed the 5%
RETT and which this Law elevates into primary legislation; and (3) the
absence of any chapter structure.

20 records, flat (no chapters): all 20 اصلية. This is a brand-new 2024
statute with NO amendments to date — no معدلة/ملغاة/مضافة articles, and
therefore no pre-amendment original-text gaps.

Administering authority: ZATCA (Zakat, Tax and Customs Authority) — a third
ZATCA tax-law family in this corpus alongside vat_law and income_tax_law.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "rett", "law", "official_source",
                   "rett_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "rett", "law", "verified")
RECORDS = os.path.join(OUT_VER, "rett_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "rett_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "rett_arabic_legal_llm",
                        "rett_law_legal_llm_001_020.json")

LAW_ID = "sa-rett-law-m84-1446"
LAW_AR = "نظام ضريبة التصرفات العقارية"
STATUS = "BOE_PORTAL_PRIMARY_X_SECONDARY_CROSS_VERIFIED"
KEY_RE = r"rett_art_(\d{3})$"
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
        ver.append({"law_key": "rett", "law_component": "law", "language": "ar",
                    "record_layer": "RETT_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": is_amended,
                    "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; verbatim text from the "
                                              "laws.boe.gov.sa (BOE portal) lawId page, "
                                              "reached via the r.jina.ai proxy after the "
                                              "live page returned HTTP 503, cross-verified "
                                              "for decree/count/flat-structure against "
                                              "nezams.com and qanoonsa.com — see "
                                              "verification_methodology_note in the source "
                                              "artifact, including the note that Article "
                                              "20(2)'s repeal is generic (not named) and "
                                              "that the Law has no chapter structure."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": is_amended, "is_added": ls == "مضافة",
                    "record_id": "rett-law-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "rett/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام ضريبة التصرفات العقارية" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Decree — BOE portal primary "
                                                          "text x secondary cross-verified"),
                                     "source_authority_ar": "مرسوم ملكي — نص بوابة هيئة الخبراء (BOE) الرسمي مطابق مع مصادر ثانوية مستقلة",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "rett",
               "layer": "RETT_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "publication_date_hijri": src.get("publication_date_hijri"),
               "administering_authority_en": src.get("administering_authority_en"),
               "consolidated_amended_law": False,
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-rett-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (20 مادة؛ نص أصلي: 20 أصلية)",
               "title_en": "Saudi Real Estate Transaction Tax Law — Arabic LLM-ready layer (20 records, original)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 20], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready RETT Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
