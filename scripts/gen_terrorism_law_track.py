#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Law on Combating Crimes of Terrorism and its Financing track (نظام مكافحة جرائم الإرهاب وتمويله م/21).

Source: the official MOJ legal-portal text (Royal Decree M/21, 12/2/1439H),
fetched article-by-article (get-Section-Changes) and cross-verified against the
official MOJ PDF (90/99 MATCHES_PDF outright, mean 0.955; the 9 long articles (1,
3, 10, 39, 43, 50, 56, 82, 83) had their PDF text-layer reorder/split clauses —
every word present, the few unigram gaps being OCR gluing the trailing comma to a
word — and were adjudicated visually verbatim on the rendered pages). This law is
IN FORCE. CONSOLIDATED AMENDED: 88 اصلية / 8 معدلة (arts 4, 9, 12, 63, 67, 70, 71,
83) / 0 ملغاة / 3 مضافة (arts 59 مكرر, 63 مكرر, 81 مكرر); each amended/added article
carries its full version history. SUPERSESSION: it replaced the older Law of
Terrorism Crimes and its Financing (M/16, 1435H). The section-API status equals
the statuteStructure/PDF status for every article (no dual-status divergence).

Articles are numbered by their ordinal position in the official statute structure
(1..96) plus three مكرر articles (59, 63, 81 مكرر). number_label_ar preserves each
article's official label (article 75's portal-doubled label de-duplicated).
No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "terrorism", "law", "official_source",
                   "terrorism_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "terrorism", "law", "verified")
RECORDS = os.path.join(OUT_VER, "terrorism_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "terrorism_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "terrorism_arabic_legal_llm",
                        "terrorism_law_legal_llm_001_099.json")

LAW_ID = "sa-terrorism-law-m21-1439"
LAW_AR = "نظام مكافحة جرائم الإرهاب وتمويله"
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
KEY_RE = r"terrorism_art_(\d{3})(_mukarrar)?$"
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
        ls = a.get("legal_status_ar")
        text = a["text"]
        ver.append({"law_key": "terrorism", "law_component": "law", "language": "ar",
                    "record_layer": "TERRORISM_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_muk, "article_key": key,
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
                                              "the official MOJ PDF (verbatim; low-similarity long articles "
                                              "adjudicated visually on the rendered pages)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_muk, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "record_id": "terrorism-law-llm-art-%03d%s" % (n, "-mukarrar" if is_muk else ""),
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "terrorism/law/articles/%03d%s" % (n, "_mukarrar" if is_muk else ""),
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام مكافحة جرائم الإرهاب وتمويله" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": "Ministry of Justice (MOJ) — official legal portal",
                                     "source_authority_ar": "وزارة العدل — المنصة القانونية الرسمية",
                                     "source_status": "moj_portal_api_cross_checked_official_pdf",
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "terrorism", "layer": "TERRORISM_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "visually_adjudicated": src["stats"]["visually_adjudicated"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-terrorism-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (99 مادة؛ 88 أصلية / 8 معدلة / 3 مضافة)",
               "title_en": "Saudi Law on Combating Crimes of Terrorism and its Financing — Arabic LLM-ready layer (99 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 96], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Law on Combating Crimes of Terrorism and its Financing records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
