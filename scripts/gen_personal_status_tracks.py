#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Personal Status Law and its implementing regulation tracks.

نظام الأحوال الشخصية (م/73، 6/8/1443هـ — 252 articles) and its لائحة
(Supreme Order 59641, 17/8/1446هـ — 41 articles), both fetched article-by-
article from the official MOJ legal-portal database and cross-verified against
the official MOJ PDF from the same portal (see the source artifacts). Both
are in force and unamended (every article 'اصلية'). Arabic governs; no
translation, paraphrase, or legal interpretation. Read-only over inputs;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك").split())

TRACKS = [
    {"key": "law", "dir": "law", "law_id": "sa-personal-status-law-m73-1443",
     "doc_ar": "نظام الأحوال الشخصية", "doc_en": "Saudi Personal Status Law",
     "component": "law", "n": 252, "rid": "personal-status-law-llm-art",
     "query_doc": "نظام الأحوال الشخصية"},
    {"key": "reg", "dir": "regulation", "law_id": "sa-personal-status-implementing-regulation",
     "doc_ar": "لائحة نظام الأحوال الشخصية",
     "doc_en": "Implementing Regulation of the Personal Status Law",
     "component": "implementing_regulation", "n": 41, "rid": "personal-status-reg-llm-art",
     "query_doc": "لائحة نظام الأحوال الشخصية"},
]


def _kw(text, k=6, fallback="الأحوال الشخصية"):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [fallback]


def build(t):
    src_p = os.path.join(ROOT, "sources", "personal_status", t["dir"], "official_source",
                         "personal_status_%s_official_source.json" % t["dir"])
    out_ver = os.path.join(ROOT, "sources", "personal_status", t["dir"], "verified")
    rec_p = os.path.join(out_ver, "personal_status_%s_verified_records.jsonl" % t["dir"])
    sum_p = os.path.join(out_ver, "personal_status_%s_verified_summary.json" % t["dir"])
    llm_p = os.path.join(ROOT, "data", "personal_status_arabic_legal_llm",
                         "personal_status_%s_legal_llm_001_%03d.json" % (t["dir"], t["n"]))

    src = json.load(open(src_p, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=lambda k: int(re.search(r"_art_(\d{3})$", k).group(1)))
    os.makedirs(out_ver, exist_ok=True)
    os.makedirs(os.path.dirname(llm_p), exist_ok=True)

    ver, llm = [], []
    for key in keys:
        a = arts[key]
        n = int(re.search(r"_art_(\d{3})$", key).group(1))
        text = a["text"]
        ver.append({"law_key": "personal_status", "law_component": t["component"],
                    "language": "ar",
                    "record_layer": "PERSONAL_STATUS_%s_ARABIC_VERIFIED_TEXT" % t["dir"].upper(),
                    "article_number": n, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": a.get("legal_status_ar"),
                    "pdf_similarity": a.get("pdf_similarity"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; official MOJ legal-portal database "
                                              "text cross-verified against the official MOJ PDF "
                                              "(see source artifact)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": t["law_id"], "law_component": t["component"],
                    "article_number": n, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "record_id": "%s-%03d" % (t["rid"], n),
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (t["doc_ar"], a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (t["doc_ar"], a["number_label_ar"]),
                    "article_path": "personal_status/%s/articles/%03d" % (t["dir"], n),
                    "keywords_ar": _kw(text, fallback=t["query_doc"]),
                    "search_queries_ar": ["المادة %d %s" % (n, t["query_doc"]),
                                          "%s المادة %d" % (t["query_doc"], n),
                                          "المادة %d من %s" % (n, t["doc_ar"])],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": "Ministry of Justice (MOJ) — official legal portal",
                                     "source_authority_ar": "وزارة العدل — المنصة القانونية الرسمية",
                                     "source_status": "moj_portal_api_cross_checked_official_pdf",
                                     "source_document_ar": t["doc_ar"],
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(rec_p, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "personal_status",
               "layer": "PERSONAL_STATUS_%s_ARABIC_VERIFIED_TEXT" % t["dir"].upper(),
               "record_count": len(ver), "official_text_status": STATUS,
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "source_artifact": os.path.relpath(src_p, ROOT)},
              open(sum_p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-personal-status-%s-arabic-legal-llm-full" % t["dir"],
               "law_id": t["law_id"], "law_component": t["component"],
               "title_ar": t["doc_ar"] + " — الطبقة العربية الجاهزة للنماذج اللغوية (%d مادة)" % len(llm),
               "title_en": t["doc_en"] + " — Arabic LLM-ready layer (%d records)" % len(llm),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, t["n"]], "text_status": STATUS,
               "not_legal_advice": True, "records": llm},
              open(llm_p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote personal_status %s: %d verified + %d LLM-ready records" % (t["dir"], len(ver), len(llm)))


def main():
    for t in TRACKS:
        build(t)


if __name__ == "__main__":
    main()
