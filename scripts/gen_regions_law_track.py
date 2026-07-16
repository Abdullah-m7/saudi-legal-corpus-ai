#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Regions/Provinces Law track (نظام المناطق, Royal Order A/92,
27/8/1412H).

DISTINCT VERIFICATION TIER — laws.boe.gov.sa was NOT reachable for this
law's specific LawDetails page across roughly 20 attempts over 45+ minutes
this research pass (direct curl, curl+r.jina.ai with varied timeout/
wait-for-selector/engine headers, and WebFetch+r.jina.ai) — consistent
network-idle timeouts, a Cloudflare 524, and rate-limit blocks. The same
method successfully fetched a different BOE law page in 19s in this same
session, so this appears to be a page-specific hang rather than a systemic
block; a follow-up attempt from a fresh session is recommended. Neither of
this corpus's two established verification methods (MOJ portal DB x
official PDF, or BOE-portal-via-Wayback byte-identical cross-snapshot) was
available. Instead, full text rests on CROSS-VERIFIED AGREEMENT BETWEEN TWO
INDEPENDENT ARABIC SECONDARY SOURCES: islamport.com ("الموسوعة الشاملة")
and nezams.com — substantively identical, only trivial OCR/spelling slips
found and corrected against the cross-source. FAOLEX's English PDF
(faolex.fao.org/docs/pdf/sau213421.pdf) was used only as a WEAKER
meaning-level cross-check (English, not Arabic) and was confirmed
INCOMPLETE (omits article 41) and carrying an internal date error. This is
a distinct, clearly-flagged tier: genuine same-language (Arabic-Arabic)
two-source convergence, stronger than an English-only fallback, but still
short of this corpus's gold-standard BOE/MOJ structured-portal primary
source.

See sources/regions/law/official_source/regions_law_official_source.json
for the full methodology note and documented unresolved discrepancies.

Consolidated amended law: 31 اصلية / 9 معدلة / 0 ملغاة / 1 مضافة (41 total
articles). A single consolidating amendment, Royal Order A/21 dated
30/3/1414H, amended articles 3, 7, 9, 10, 11, 12, 13, 16, 37, and added
article 41. Articles are numbered by ordinal position 1..41, no مكرر, flat
structure with no chapter/section wrapper (section_ar empty for every
article).

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "regions", "law", "official_source",
                   "regions_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "regions", "law", "verified")
RECORDS = os.path.join(OUT_VER, "regions_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "regions_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "regions_arabic_legal_llm",
                        "regions_law_legal_llm_001_041.json")

LAW_ID = "sa-regions-law-a92-1412"
LAW_AR = "نظام المناطق"
STATUS = "DUAL_ARABIC_SECONDARY_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE"
KEY_RE = r"regions_art_(\d{3})$"
AMENDED_KEYS = {"regions_art_%03d" % n for n in (3, 7, 9, 10, 11, 12, 13, 16, 37)}
ADDED_KEYS = {"regions_art_041"}
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
        is_added = ls == "مضافة"
        text = a["text"]
        ver.append({"law_key": "regions", "law_component": "law", "language": "ar",
                    "record_layer": "REGIONS_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track uses a distinct "
                                              "verification tier — dual independent Arabic "
                                              "secondary sources (islamport.com x nezams.com), "
                                              "not a primary BOE-portal source, because this "
                                              "law's BOE LawDetails page could not be reached "
                                              "across roughly 20 attempts this research pass — "
                                              "see verification_methodology_note in the source "
                                              "artifact for the full caveat."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "regions-law-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "regions/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام المناطق" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Order — dual independent Arabic "
                                                          "secondary sources (BOE portal page "
                                                          "unreachable this pass, see "
                                                          "verification_methodology_note)"),
                                     "source_authority_ar": "أمر ملكي — مصدران عربيان ثانويان مستقلان متطابقان (تعذر الوصول لصفحة بوابة هيئة الخبراء)",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "regions",
               "layer": "REGIONS_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-regions-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (41 مادة؛ نص موحّد: 31 أصلية، 9 معدّلة، 1 مضافة)",
               "title_en": "Saudi Regions/Provinces Law — Arabic LLM-ready layer (41 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 41], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Regions/Provinces Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
