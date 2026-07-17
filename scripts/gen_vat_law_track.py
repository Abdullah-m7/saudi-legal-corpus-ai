#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Value Added Tax Law track (نظام ضريبة القيمة المضافة,
Royal Decree M/113, 2/11/1438H).

DISTINCT VERIFICATION TIER — current-consolidated text rests on TWO
independent official sources in agreement: ZATCA's own official
consolidated Arabic PDF (source of the two amended articles' current
text), cross-verified against laws.boe.gov.sa (reached via the r.jina.ai
proxy) for all other articles and for decree/preamble metadata. The
Wayback Machine was unreachable this pass (TLS connection reset) and was
not part of this track's verification chain.

See sources/vat/law/official_source/vat_law_official_source.json for the
full methodology note and all documented unresolved discrepancies,
including the IMPORTANT LIMITATION that neither amended article's
pre-amendment original text was captured to primary-source confidence
this pass — no original_1438h_text fields are fabricated for either.

53 records, 18 chapters (فصول): 51 اصلية / 2 معدلة (Article 2 — VAT rate
raised from 5% to 15% by Royal Order A/638, 15/10/1441H; Article 49 —
appeal-body reference updated by Royal Decree M/52, 28/4/1441H).

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "vat", "law", "official_source",
                   "vat_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "vat", "law", "verified")
RECORDS = os.path.join(OUT_VER, "vat_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "vat_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "vat_arabic_legal_llm",
                        "vat_law_legal_llm_001_053.json")

LAW_ID = "sa-vat-law-m113-1438"
LAW_AR = "نظام ضريبة القيمة المضافة"
STATUS = "ZATCA_OFFICIAL_PDF_X_BOE_PORTAL_CROSS_VERIFIED"
KEY_RE = r"vat_art_(\d{3})$"
AMENDED_KEYS = {"vat_art_002", "vat_art_049"}
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
        ver.append({"law_key": "vat", "law_component": "law", "language": "ar",
                    "record_layer": "VAT_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": is_amended, "is_added": False,
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track uses a distinct "
                                              "verification tier — ZATCA's own official "
                                              "consolidated PDF cross-verified against the "
                                              "BOE portal (via r.jina.ai, live page "
                                              "returned HTTP 503) — see "
                                              "verification_methodology_note in the source "
                                              "artifact for the full caveat, including the "
                                              "limitation that pre-amendment original text "
                                              "is NOT included for either amended article "
                                              "this pass."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": is_amended, "is_added": False,
                    "record_id": "vat-law-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "vat/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام ضريبة القيمة المضافة" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Decree — ZATCA official "
                                                          "PDF x BOE portal cross-verified"),
                                     "source_authority_ar": "مرسوم ملكي — ملف PDF رسمي من هيئة الزكاة والضريبة والجمارك مطابق مع بوابة هيئة الخبراء",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "vat",
               "layer": "VAT_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-vat-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (53 مادة؛ نص موحّد: 51 أصلية، 2 معدّلة)",
               "title_en": "Saudi Value Added Tax Law — Arabic LLM-ready layer (53 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 53], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready VAT Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
