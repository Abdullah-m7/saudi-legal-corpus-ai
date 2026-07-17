#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Allegiance Commission Law track (نظام هيئة البيعة, Royal Order
A/135, 26/9/1427H).

DISTINCT VERIFICATION TIER — the BOE legal portal's exact LawDetails page for
this law was located (GUID 3213c2f6-eaf8-45dc-8f8c-a9a700f167ee) but was
UNREACHABLE by every method tried this research pass: direct fetch returned
HTTP 503; the r.jina.ai reader-proxy returned HTTP 422/timeout; and the
Wayback Machine, despite a valid archived snapshot existing, was blocked by
this sandbox's network egress policy. Instead, THREE INDEPENDENT ARABIC
SECONDARY SOURCES (ar.wikisource.org, islamport.com, ar.wikipedia.org) were
fetched and cross-compared directly, agreeing on all 25 articles almost
word-for-word — the strongest secondary-source tier used in this corpus
(stronger than the dual-source tier), though still not BOE-primary-verified.

See sources/allegiance_commission/law/official_source/
allegiance_commission_law_official_source.json for the full methodology
note and documented unresolved discrepancies — CRITICALLY including a
genuine, unresolved cross-track conflict: this law's own promulgation order
claims to amend Article 5(c) of the Basic Law of Governance, but that
track (already in this corpus) shows different wording. This is flagged,
not silently resolved, pending a dedicated verification pass.

Fresh issuance, no amendments found to this law's own text: all 25 اصلية,
flat structure with no chapter/section wrapper. One wording discrepancy in
Article 21 (تأجيل vs تعديل) is documented in the source artifact; this
track uses the majority (2-of-3 source) reading.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "allegiance_commission", "law", "official_source",
                   "allegiance_commission_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "allegiance_commission", "law", "verified")
RECORDS = os.path.join(OUT_VER, "allegiance_commission_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "allegiance_commission_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "allegiance_commission_arabic_legal_llm",
                        "allegiance_commission_law_legal_llm_001_025.json")

LAW_ID = "sa-allegiance-commission-law-a135-1427"
LAW_AR = "نظام هيئة البيعة"
STATUS = "TRIPLE_ARABIC_SECONDARY_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE"
KEY_RE = r"allegiance_commission_art_(\d{3})$"
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
        text = a["text"]
        ver.append({"law_key": "allegiance_commission", "law_component": "law", "language": "ar",
                    "record_layer": "ALLEGIANCE_COMMISSION_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": False, "is_added": False,
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track uses a distinct "
                                              "verification tier — triple independent Arabic "
                                              "secondary sources (ar.wikisource.org x "
                                              "islamport.com x ar.wikipedia.org), not a primary "
                                              "BOE-portal source, because this law's BOE page "
                                              "was located but unreachable by every method tried "
                                              "this research pass — see "
                                              "verification_methodology_note in the source "
                                              "artifact for the full caveat, including a "
                                              "documented cross-track conflict with the Basic "
                                              "Law of Governance track's Article 5(c)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": False, "is_added": False,
                    "record_id": "allegiance-commission-law-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "allegiance_commission/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام هيئة البيعة" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Order — triple independent "
                                                          "Arabic secondary sources (BOE page "
                                                          "located but unreachable, see "
                                                          "verification_methodology_note)"),
                                     "source_authority_ar": "أمر ملكي — ثلاثة مصادر عربية ثانوية مستقلة متطابقة (تعذر الوصول لصفحة بوابة هيئة الخبراء)",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "allegiance_commission",
               "layer": "ALLEGIANCE_COMMISSION_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": False,
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-allegiance-commission-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (25 مادة؛ إصدار طازج: 25 أصلية)",
               "title_en": "Saudi Allegiance Commission Law — Arabic LLM-ready layer (25 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 25], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Allegiance Commission Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
