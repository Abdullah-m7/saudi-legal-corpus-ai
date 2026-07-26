#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Private (National) Schools Regulation track (لائحة تنظيم
المدارس الأهلية, Council of Ministers Resolution No. 1006, 13/8/1395H).

STANDALONE track (no base_law_key): this regulation predates and is not a
formal implementing regulation of general_education_law (Royal Decree M/36,
27/1/1448H, not yet in force) -- see that track's own official_source.json
(known_unresolved_discrepancies key
general_education_law_seven_com_resolutions_repealed_untracked), which
confirms Clause Fourth of Council of Ministers Resolution 103 repeals this
very regulation (by name, number, and date) once the new Law takes effect,
subject to a one-year phased transitional continuation. As of this pass the
new Law is NOT YET IN FORCE (effective ~mid-January 2027), so this
regulation remains fully السَريان (in force) today -- and will remain in
force transitionally for up to one further year even after the new Law
takes effect. Follows this corpus's press_regulation / civil_defense_regulation
single/standalone-track pattern.

24 articles, flat (no أبواب/فصول). 22 اصلية, 2 معدلة:
  - Article 5(e): amended by CoM Resolution 269, 3/5/1443H (disability-
    inclusion exception for girls' primary schools). NOTE: the Ministry of
    Education's own official source PDF itself shows an internal
    inconsistency -- its main article body still prints the PRE-amendment
    wording while a footnote gives the amended text verbatim; this track
    adopts the amended (footnote) text as legally current, with the
    original preserved in history[]. See known_unresolved_discrepancies.
  - Article 7(a): deleted (Saudi-nationality requirement for the school
    owner) by CoM Resolution 89, 7/2/1440H, with paragraphs renumbered;
    single-source (MOE PDF footnote) attestation, disclosed as such.

VERIFICATION TIER: TIER_1-candidate. Primary source is the Ministry of
Education's own official PDF (moe.gov.sa), fetched directly this pass and
vision-read in full across all 8 rendered pages against the pdftotext
extraction -- byte-for-byte match confirmed on every page checked, no OCR/
font defects found (unlike several other PDF sources in this corpus).
laws.boe.gov.sa was unreachable (connection reset, a pattern already
documented elsewhere in this corpus for this domain). Full account in
sources/private_schools_regulation/law/official_source/
private_schools_regulation_official_source.json's verification_methodology_note.

TASHKEEL and layout artifacts (double spaces, space-before-punctuation,
curly quotes, invisible RTL/LTR embedding marks from PDF extraction)
normalised in the display layer only by this generator; no legal text
altered. Arabic governs; no translation/paraphrase/interpretation performed.
Read-only over input; deterministic over outputs. Standalone track -- no
shared pipeline files modified.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "private_schools_regulation", "law", "official_source",
                   "private_schools_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "private_schools_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "private_schools_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "private_schools_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "private_schools_regulation_arabic_legal_llm",
                        "private_schools_regulation_legal_llm_001_024.json")

LAW_ID = "sa-private-schools-regulation-1006-1395h"
LAW_AR = "لائحة تنظيم المدارس الأهلية"
KEY_RE = r"private_schools_regulation_art_(\d{3})$"
AMENDED_KEYS = {"private_schools_regulation_art_005", "private_schools_regulation_art_007"}

STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم جهة الإشراف المدرسة الأهلية").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def _clean(text):
    """Display-layer normalisation only: strip invisible bidi marks left over
    from PDF extraction, collapse double spaces, remove space-before-
    punctuation, straighten curly quotes. No wording altered."""
    text = re.sub(r"[‎‏‪-‮]", "", text)
    text = text.replace(" ", " ")
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
        ver.append({"law_key": "private_schools_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "PRIVATE_SCHOOLS_REGULATION_ARABIC_VERIFIED_TEXT",
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
                        "Arabic governs; this track rests on the Ministry of "
                        "Education's own official PDF, direct-fetched this pass and "
                        "vision-read in full across all 8 pages (byte-identical to "
                        "the automated pdftotext extraction on every page checked). "
                        "This regulation is explicitly named for future repeal "
                        "(subject to a one-year phased transition) by "
                        "general_education_law (Royal Decree M/36, not yet in "
                        "force) -- see known_unresolved_discrepancies and this "
                        "law's own verification_methodology_note before relying on "
                        "its current-in-force status long-term."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": bool(a.get("is_mukarrar")), "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "private-schools-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "private_schools_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من لائحة تنظيم المدارس الأهلية"
                                          % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": (
                        "Ministry of Education official PDF (moe.gov.sa), direct "
                        "fetch, vision-verified in full against pdftotext across "
                        "all 8 pages -> TIER_1-candidate."),
                                     "source_authority_ar": (
                        "ملف وزارة التعليم الرسمي (moe.gov.sa)، جلب مباشر، تحقق "
                        "بصري كامل مقابل النص الآلي عبر الصفحات الثماني -> "
                        "TIER_1 مشروط."),
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "private_schools_regulation",
               "layer": "PRIVATE_SCHOOLS_REGULATION_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-private-schools-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (24 مادة)",
               "title_en": ("Private (National) Schools Regulation — Arabic "
                            "LLM-ready layer (24 records)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 24],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Private Schools Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
