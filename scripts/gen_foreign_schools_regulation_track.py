#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Foreign Schools Regulation track (لائحة المدارس الأجنبية,
Council of Ministers Resolution No. 26, 4/2/1418H).

NOTE ON RESOLUTION NUMBER: the task brief that requested this track referred
to "Resolution No. 36"; every source independently checked this pass --
nezams.com, bibliotdroit.com, multiple web-search results, and this corpus's
own general_education_law_official_source.json (which lists this exact
regulation by name among the seven Council-of-Ministers-level instruments
Clause Fourth of Resolution 103 repeals) -- agrees the correct number is
(26). This track uses (26); see known_unresolved_discrepancies for the
explicit correction.

STANDALONE track (no base_law_key): predates general_education_law by ~29
years and is not that Law's formal implementing regulation. As with
private_schools_regulation, general_education_law_official_source.json
confirms this regulation is named for future repeal (Clause Fourth of CoM
Resolution 103) once the new Law -- NOT YET IN FORCE as of this pass, see
that track -- takes effect, subject to a one-year phased transition. As of
today this regulation remains fully in force (ساري).

21 articles, flat (no أبواب/فصول). 19 اصلية, 2 معدلة:
  - Article 5: amended by CoM Resolution 220, 10/8/1424H (removed the
    three-year cap on admitting returning-from-abroad Saudi students).
  - Article 9: amended by CoM Resolution 141, 10/3/1439H (added a paragraph
    on foreign embassies purchasing school land/buildings).

VERIFICATION TIER: TIER_2. laws.boe.gov.sa has a confirmed lawId for this
regulation but returned HTTP 503 on every direct-fetch attempt this pass
(consistent with this corpus's documented pattern for this domain); the
Ministry of Education's own site returned 404 for a guessed PDF filename;
Wayback Machine is blocked in this environment. Verification instead rests
on two independent non-governmental legal-portal sources (nezams.com,
bibliotdroit.com), both fetched directly (HTTP 200) and cross-checked
word-for-word identical for the preamble and all 19 unamended articles;
nezams.com additionally quotes both amendments' post-amendment text
verbatim in quotation marks with resolution number/date. Full account in
sources/foreign_schools_regulation/law/official_source/
foreign_schools_regulation_official_source.json's verification_methodology_note.

TASHKEEL/layout artifacts normalised in the display layer only by this
generator; no legal text altered. Arabic governs; no translation/paraphrase/
interpretation performed. Read-only over input; deterministic over outputs.
Standalone track -- no shared pipeline files modified.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "foreign_schools_regulation", "law", "official_source",
                   "foreign_schools_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "foreign_schools_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "foreign_schools_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "foreign_schools_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "foreign_schools_regulation_arabic_legal_llm",
                        "foreign_schools_regulation_legal_llm_001_021.json")

LAW_ID = "sa-foreign-schools-regulation-26-1418h"
LAW_AR = "لائحة المدارس الأجنبية"
KEY_RE = r"foreign_schools_regulation_art_(\d{3})$"

STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم الوزارة الوزير المدارس الأجنبية").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def _clean(text):
    text = re.sub(r"[‎‏‪-‮]", "", text)
    text = text.replace(" ", " ")
    text = text.replace("“", '"').replace("”", '"')
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s+\n", "\n", text)
    text = re.sub(r"\s([،.:؛؟])", r"\1", text)
    return text.strip()


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=lambda k: int(re.match(KEY_RE, k).group(1)))
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for key in keys:
        a = arts[key]
        n = int(re.match(KEY_RE, key).group(1))
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        is_repealed = ls == "ملغاة"
        text = _clean(a["text"])
        ver.append({"law_key": "foreign_schools_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "FOREIGN_SCHOOLS_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": bool(a.get("is_mukarrar")),
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history") or [],
                    "official_text_status": src.get("legal_status_ar"),
                    "governing_source_note": (
                        "Arabic governs; this track's text rests on two "
                        "independent non-governmental legal-portal sources "
                        "(nezams.com, bibliotdroit.com), word-for-word identical "
                        "on cross-check, after laws.boe.gov.sa (confirmed lawId, "
                        "but HTTP 503 on every fetch attempt) and moe.gov.sa (404 "
                        "on the only guessed filename) both proved unreachable "
                        "this pass -> TIER_2. The task brief's stated resolution "
                        "number (36) was corrected to the verified number (26); "
                        "see known_unresolved_discrepancies. This regulation is "
                        "explicitly named for future repeal (one-year phased "
                        "transition) by general_education_law (not yet in force) "
                        "-- see that track before relying on long-term status."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": bool(a.get("is_mukarrar")), "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "foreign-schools-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "foreign_schools_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من لائحة المدارس الأجنبية"
                                          % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": (
                        "Two independent non-governmental legal-portal sources "
                        "(nezams.com, bibliotdroit.com), word-for-word cross-"
                        "verified; laws.boe.gov.sa lawId confirmed but "
                        "unreachable (HTTP 503) -> TIER_2."),
                                     "source_authority_ar": (
                        "بوابتان قانونيتان مستقلتان غير حكوميتين (nezams.com، "
                        "bibliotdroit.com)، متطابقتان حرفياً؛ lawId مؤكد على "
                        "laws.boe.gov.sa لكن تعذر الوصول (HTTP 503) -> TIER_2."),
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "foreign_schools_regulation",
               "layer": "FOREIGN_SCHOOLS_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "base_law_key": src.get("base_law_key"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "chapter_structure": src["chapter_structure"],
               "amendment_history": src.get("amendment_history", []),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-foreign-schools-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (21 مادة)",
               "title_en": ("Foreign Schools Regulation — Arabic LLM-ready "
                            "layer (21 records)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 21],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Foreign Schools Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
