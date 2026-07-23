#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation for Air Quality track
(اللائحة التنفيذية لجودة الهواء لنظام البيئة, Ministerial Decision No. (512258/1/1442),
24/9/1442H, issued under Article 48 of the Environmental Law, Royal Decree M/165,
19/11/1441H).

This is one of the ~15 genuinely distinct topical Implementing Regulations of the
General Environmental Law (see reports/coverage_gap_map/coverage_gap_map.json, the
"Implementing Regulations of the General Environmental Law -- CORRECTED SCOPE" gap,
sub_candidate environmental_air_quality_reg). A prior pass flagged it build-ready
but had NOT captured the exact decision number; this track confirms it.

VERIFICATION TIER -- see environmental_air_quality_reg_official_source.json's
verification_methodology_note for the full account. Summary:

DECISION NUMBER (the prior pass's main open item) is now confirmed from a PRIMARY
source: the preamble of the later Table-3-amendment decision, published on the
Umm Al-Qura official gazette portal (uqn.gov.sa/details?p=25436), states verbatim:
"اللائحة التنفيذية لجودة الهواء لنظام البيئة، الصادرة بالقرار الوزاري رقم
(512258/1/1442) بتاريخ 24/9/1442هـ". The date (24 Ramadan 1442H = 6 May 2021) is
independently corroborated by Saudipedia (saudipedia.com); the number is consistent
with MEWA's 1442H executive-regulation numbering series (######/1/1442).

laws.boe.gov.sa was checked FIRST per this corpus's methodology but is unreachable
this pass (connection failure, HTTP 000 -- matching sibling tracks food_regulation
and environmental_law) and has no dedicated lawId page for this Board/Ministerial-
level regulation. Wayback (web.archive.org) is blocked in this environment.

TEXT SOURCE + DUAL VERIFICATION: the authoritative PRIMARY document is MEWA's own
born-digital PDF (mewa.gov.sa/.../اللائحة التنفيذية لجودة الهواء.pdf, HTTP 200, 102
pages, Creator: Word, macOS Quartz PDFContext, internal CreationDate 24 May 2021 --
one day before the 25 May 2021 application date). Its embedded text layer uses
presentation/Farsi letter forms (ھ U+06BE, ی U+06CC) and RTL word-gluing that make
verbatim extraction error-prone, so the ingested article text is taken from an
independent legal aggregator's cleanly-ordered rendering (qanoniah.com, retrieved
via the r.jina.ai reader) and then DUAL-VERIFIED word-for-word (4+ char words)
against the MEWA authoritative PDF after letter-form folding -- ~100% match (the sole
outlier being a trivial ملايين/مليون grammatical-number variant on an identical
barrel threshold in Article 6). Both sources are fully independent (issuing
ministry's own site + independent aggregator).

STRUCTURE: 8 numbered, titled articles (المواد 1-8) -- confirmed via the MEWA PDF
table of contents, the qanoniah independent copy, and argaam.com ("8 articles").
All 8 are اصلية (0 معدلة, 0 ملغاة, 0 مضافة). The regulation additionally contains a
violations/penalties TABLE (الجدول 3, 37 rows) and EIGHT technical APPENDICES
(الملاحق 1-8, pages 33-102, pure numeric pollutant-standard/emission-limit
schedules). These tabular annexes are NOT ingested verbatim here -- consistent with
the food_regulation precedent (which excluded its penalty table as a distinct
tabular annex) and because verbatim extraction of dense RTL numeric tables to a
"fully trusted" standard is out of scope this pass. They are documented as a
follow-up candidate (excluded_tabular_annexes / known_unresolved_discrepancies).
Table 3 alone was later amended (Ministerial Decision 15029057, 04/02/1446H); that
amendment does NOT touch any of the 8 ingested articles.

No repeal/supersession clause is present in the regulation text (confirmed negative,
searched both independent sources). Articles 5 and 6 contain genuine Latin technical
acronyms/method names (CEMS, RATA, USEPA Method, etc.) that are part of the source
text and are preserved. Diacritics (tashkeel) and tatweel are stripped uniformly for
consistency with this corpus's other tracks. Arabic governs; no translation/
paraphrase/interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "environmental_air_quality", "official_source",
                   "environmental_air_quality_reg_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "environmental_air_quality", "verified")
RECORDS = os.path.join(OUT_VER, "environmental_air_quality_reg_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "environmental_air_quality_reg_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "environmental_air_quality_arabic_legal_llm",
                        "environmental_air_quality_reg_legal_llm_001_008.json")

LAW_ID = "sa-environmental-air-quality-reg-512258-1-1442"
LAW_AR = "اللائحة التنفيذية لجودة الهواء لنظام البيئة"
STATUS_UNCHANGED = "UNCHANGED"
KEY_RE = r"environmental_air_quality_reg_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()

STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم المركز").split())


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
    n = int(m.group(1))
    suf = m.group(2)
    if suf is None:
        return (n, 0)
    if suf == "":
        return (n, 1)
    return (n, 1 + int(suf))


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    gov_note = ("Arabic governs. DECISION NUMBER confirmed from a PRIMARY source (the "
                "Umm Al-Qura gazette's own Table-3-amendment-decision preamble, "
                "uqn.gov.sa) citing 'القرار الوزاري رقم (512258/1/1442) بتاريخ "
                "24/9/1442هـ'; date corroborated by saudipedia.com. Article TEXT is "
                "dual-verified: taken from qanoniah.com's independent rendering and "
                "matched word-for-word (~100%) against MEWA's own born-digital PDF "
                "(the issuing ministry's site). laws.boe.gov.sa was checked first but "
                "is unreachable this pass and has no dedicated lawId page for this "
                "regulation. SCOPE: only the 8 numbered articles are ingested; the "
                "violations/penalties TABLE (الجدول 3) and the 8 technical APPENDICES "
                "(الملاحق 1-8) are excluded as tabular annexes (documented follow-up), "
                "per the food_regulation precedent. Table 3 was separately amended by "
                "Ministerial Decision 15029057 (04/02/1446H); that does not touch any "
                "of these 8 articles. No repeal/supersession clause exists (confirmed "
                "negative). See verification_methodology_note and "
                "known_unresolved_discrepancies in the source artifact before relying "
                "on this track.")

    ver, llm = [], []
    for idx, key in enumerate(keys, start=1):
        a = arts[key]
        m = re.match(KEY_RE, key)
        n = int(m.group(1))
        is_mukarrar = bool(a.get("is_mukarrar"))
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        is_repealed = ls == "ملغاة"
        text = a["text"]
        text_complete = a.get("text_complete", True)
        title = a.get("title_ar") or ""
        num_label = a["number_label_ar"]
        full_label = ("%s: %s" % (num_label, title)) if title else num_label
        ver.append({"law_key": "environmental_air_quality", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "ENVIRONMENTAL_AIR_QUALITY_REG_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": num_label,
                    "title_ar": title,
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "text_complete": text_complete,
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS_UNCHANGED,
                    "governing_source_note": gov_note,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": full_label,
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "environmental-air-quality-reg-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, full_label),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, full_label),
                    "article_path": "environmental_air_quality/regulation/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (num_label, LAW_AR),
                                          "%s %s" % (title, LAW_AR) if title else "%s %s" % (num_label, LAW_AR),
                                          "%s من اللائحة التنفيذية لجودة الهواء" % num_label],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Ministerial Decision No. (512258/1/1442) "
                                                          "(24/9/1442H) of the Minister of Environment, "
                                                          "Water and Agriculture, under Article 48 of "
                                                          "the Environmental Law (Royal Decree M/165) — "
                                                          "decision number confirmed via the Umm Al-Qura "
                                                          "gazette (uqn.gov.sa); article text dual-verified "
                                                          "between mewa.gov.sa (born-digital PDF) and "
                                                          "qanoniah.com; laws.boe.gov.sa unreachable this "
                                                          "pass and has no dedicated lawId page"),
                                     "source_authority_ar": "قرار وزير البيئة والمياه والزراعة رقم (512258/1/1442) وتاريخ 24/9/1442هـ، استنادا إلى المادة (48) من نظام البيئة (المرسوم الملكي رقم م/165) — رقم القرار مؤكد من الجريدة الرسمية أم القرى (uqn.gov.sa)؛ نص المادة مؤكد مزدوجا بين mewa.gov.sa (PDF رقمي أصلي) وqanoniah.com؛ بوابة هيئة الخبراء غير قابلة للوصول هذه الجولة ولا تملك صفحة مخصصة لهذه اللائحة",
                                     "source_status": STATUS_UNCHANGED.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "environmental_air_quality",
               "layer": "ENVIRONMENTAL_AIR_QUALITY_REG_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "legal_basis_ar": src.get("legal_basis_ar", ""),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "structure_note_ar": src.get("structure_note_ar", ""),
               "excluded_tabular_annexes": src.get("excluded_tabular_annexes", []),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-environmental-air-quality-reg-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (8 مواد؛ 8 أصلية، 0 معدلة، 0 مضافة، 0 ملغاة؛ الجدول 3 والملاحق الفنية الثمانية خارج النطاق)",
               "title_en": ("Implementing Regulation for Air Quality under the Environmental Law — "
                            "Arabic LLM-ready layer (8 records: 8 original, 0 amended, 0 added, "
                            "0 repealed; the penalties Table 3 and the 8 technical appendices are "
                            "out of scope)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 8], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Air Quality Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
