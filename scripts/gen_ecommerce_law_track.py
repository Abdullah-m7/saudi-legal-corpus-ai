#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the E-Commerce Law track (نظام التجارة الإلكترونية, Royal
Decree M/126, 7/11/1440H).

DISTINCT VERIFICATION TIER — laws.boe.gov.sa's live portal was unreachable
this research pass. Full text instead rests on a Wayback Machine snapshot
of the BOE portal (fetched directly, not via r.jina.ai or WebFetch,
neither of which can reliably reach archive.org), cross-verified against
nezams.com. Only one Wayback snapshot was successfully fetched this pass
(a second, differently-dated snapshot for byte-identity cross-checking
hit repeated network-level connection resets) — a lighter cross-
verification than some other tracks' two-snapshot pattern, flagged as a
candidate for a follow-up confirmation pass.

See sources/ecommerce/law/official_source/ecommerce_law_official_source.json
for the full methodology note and all documented unresolved discrepancies.

26 records, all اصلية — a fresh, still-unamended 2019 law. NO chapter
(فصل) divisions — a flat sequence, confirmed both by the absence of any
chapter heading and by the BOE portal's own per-article amendment/repeal
CSS-class markers being absent from every article.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "ecommerce", "law", "official_source",
                   "ecommerce_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "ecommerce", "law", "verified")
RECORDS = os.path.join(OUT_VER, "ecommerce_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "ecommerce_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "ecommerce_arabic_legal_llm",
                        "ecommerce_law_legal_llm_001_026.json")

LAW_ID = "sa-ecommerce-law-m126-1440"
LAW_AR = "نظام التجارة الإلكترونية"
STATUS = "BOE_PORTAL_WAYBACK_X_NEZAMS_CROSS_VERIFIED"
KEY_RE = r"ecommerce_art_(\d{3})$"
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
        ver.append({"law_key": "ecommerce", "law_component": "law", "language": "ar",
                    "record_layer": "ECOMMERCE_LAW_ARABIC_VERIFIED_TEXT",
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
                                              "verification tier — a Wayback Machine "
                                              "snapshot of the BOE portal (fetched "
                                              "directly), cross-verified against "
                                              "nezams.com, because laws.boe.gov.sa's live "
                                              "portal was unreachable this research pass — "
                                              "see verification_methodology_note in the "
                                              "source artifact for the full caveat."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": is_amended, "is_added": False,
                    "record_id": "ecommerce-law-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "ecommerce/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام التجارة الإلكترونية" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Decree — BOE portal via "
                                                          "Wayback Machine snapshot, "
                                                          "cross-verified against "
                                                          "nezams.com"),
                                     "source_authority_ar": "مرسوم ملكي — بوابة هيئة الخبراء عبر أرشيف Wayback Machine، مطابقة مع نزامز.كوم",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "ecommerce",
               "layer": "ECOMMERCE_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-ecommerce-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (26 مادة؛ جميعها أصلية)",
               "title_en": "Saudi E-Commerce Law — Arabic LLM-ready layer (26 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 26], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready E-Commerce Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
