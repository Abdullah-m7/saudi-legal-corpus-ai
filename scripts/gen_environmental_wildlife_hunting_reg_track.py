#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation for Hunting of Wild Terrestrial Animals
track (اللائحة التنفيذية لصيد الكائنات الفطرية البرية).

This is a companion-regulation candidate flagged by this corpus's own
coverage-gap map (reports/coverage_gap_map/coverage_gap_map.json, gap entry
"Implementing Regulations of the General Environmental Law -- CORRECTED
SCOPE", sub_candidate environmental_wildlife_hunting_reg, previously marked
"needs full discovery from scratch"). It is a companion to the already-
ingested base Environmental Law track (corpus key `environmental`, Royal
Decree M/165, 19/11/1441H) -- the same "companion regulation to an already-
ingested base law" pattern as environmental_violations_penalties.

CITATION: Decision of the Minister of Environment, Water and Agriculture No.
(312179/1/1442), dated 4/6/1442H, issued under the Environmental Law and the
Statute of the National Center for Wildlife Development. Table 1 (violation
classification/penalties) was later amended by Ministerial Decision No.
(15029615), dated 5/2/1446H, WITHOUT altering the regulation's 10 articles,
Table 2, or Appendix 1.

VERIFICATION TIER -- TIER_2. See the official_source JSON's
verification_methodology_note for the full account. Summary: the full text
(18 pages: 10 articles + 2 fine tables + 1 species appendix) was extracted
from an official mewa.gov.sa-hosted PDF (downloaded directly over HTTPS,
sha256 recorded) and READ VISUALLY page-by-page at 200dpi, because the
automated pypdf text layer has known corruption (dropped letters, decorative
tatweel rendered as repeated characters) matching the same defect documented
elsewhere in this corpus for other Arabic PDF sources. The founding decree
number/date is not printed on the PDF's own cover; it was independently
confirmed via the Umm Al-Qura Gazette page publishing the Table-1 amendment,
which quotes the founding citation verbatim. laws.boe.gov.sa returned HTTP
503 this pass (unreachable, not confirmed absent).

STRUCTURE: 10 numbered articles (المادة الأولى .. العاشرة) + 3 appendix-type
records: الجدول (١) تصنيف المخالفات والعقوبات (23 rows), الجدول (٢) غرامات
صيد الكائنات الحية (59 species rows across mammals/birds/reptiles), الملحق
(١) قائمة بالطيور المتوطنة (19 species). The 3 are official, integral parts
referenced by Articles 4 and 10; ingested as 3 distinct records flagged
is_appendix=true (article_count=10, appendix_count=3, record_count=13).
Each table/appendix is stored as ONE record with its full content rendered
as clean, verbatim, line-per-row plain text (numbers/names/amounts exactly
as printed) -- not split into per-row records, consistent with how this
corpus's other form/table appendices (e.g. environmental_violations_penalties)
are modeled.

LEGAL STATUS: all 13 records اصلية. The 1446H amendment to Table 1 is
disclosed at track level (amendment_history) and inside Table 1's own text,
without claiming to know its precise before/after diff (disclosed in
known_unresolved_discrepancies) -- the Table 1 text ingested here is
whatever the official mewa.gov.sa PDF fetched this pass actually shows.

TEXT HANDLING: verbatim Arabic from the visually-read PDF pages. One
genuine source-level discrepancy preserved without silent correction: the
scientific name for «دخلة عربية» is truncated to the genus only (Curruca)
in Table 2 but given in full (Curruca leucomelaena) in Appendix 1 -- both
kept exactly as printed. Arabic governs; no translation / paraphrase /
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "environmental_wildlife_hunting",
                   "official_source",
                   "environmental_wildlife_hunting_reg_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "environmental_wildlife_hunting", "verified")
RECORDS = os.path.join(OUT_VER, "environmental_wildlife_hunting_reg_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "environmental_wildlife_hunting_reg_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "environmental_wildlife_hunting_reg_arabic_legal_llm",
                        "environmental_wildlife_hunting_reg_legal_llm_001_013.json")

LAW_ID = "sa-environmental-wildlife-hunting-reg-312179-1-1442"
LAW_AR = "اللائحة التنفيذية لصيد الكائنات الفطرية البرية"
STATUS_UNCHANGED = "UNCHANGED"
ART_RE = r"environmental_wildlife_hunting_reg_art_(\d{3})$"
APP_RE = r"environmental_wildlife_hunting_reg_appendix_(\d{3})$"

STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم النظام اللوائح الجهة المختصة المركز الصيد").split())


def _sort_key(key):
    m = re.match(ART_RE, key)
    if m:
        return (0, int(m.group(1)))
    m = re.match(APP_RE, key)
    return (1, int(m.group(1)))


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    gov_note = ("Arabic governs; PRIMARY full text is an official mewa.gov.sa-hosted PDF "
                "(downloaded directly over HTTPS, sha256 recorded), READ VISUALLY page-by-"
                "page at 200dpi because the automated pypdf text layer has known corruption "
                "(dropped letters, decorative tatweel rendered as repeated characters). The "
                "founding decree number (312179/1/1442, 4/6/1442H) is not printed on the "
                "PDF's own cover; independently confirmed via the Umm Al-Qura Gazette page "
                "publishing the later Table-1 amendment (Decision 15029615, 5/2/1446H), "
                "which quotes the founding citation verbatim. laws.boe.gov.sa returned HTTP "
                "503 this pass (unreachable, not confirmed absent). TIER_2. See "
                "verification_methodology_note and known_unresolved_discrepancies in the "
                "source artifact before relying on this track.")

    ver, llm = [], []
    for idx, key in enumerate(keys, start=1):
        a = arts[key]
        is_app = bool(a.get("is_appendix"))
        n = a["article_number"]
        ls = a.get("legal_status_ar")
        text = a["text"]
        component = "appendix" if is_app else "regulation"
        ver.append({
            "law_key": "environmental_wildlife_hunting",
            "law_component": component,
            "language": "ar",
            "record_layer": "ENVIRONMENTAL_WILDLIFE_HUNTING_REG_ARABIC_VERIFIED_TEXT",
            "article_number": n,
            "is_appendix": is_app,
            "is_mukarrar": bool(a.get("is_mukarrar")),
            "article_key": key,
            "number_label_ar": a["number_label_ar"],
            "title_ar": a.get("title_ar") or "",
            "section_ar": a.get("section_ar") or "",
            "article_text_verified": text,
            "verification_status": a["status"],
            "legal_status_ar": ls,
            "is_repealed": ls == "ملغاة",
            "is_amended": ls == "معدلة",
            "is_added": ls == "مضافة",
            "text_complete": a.get("text_complete", True),
            "amendment_history": a.get("history"),
            "official_text_status": STATUS_UNCHANGED,
            "governing_source_note": gov_note,
            "translation_performed": False,
            "legal_interpretation_performed": False,
            "summarized_or_paraphrased": False,
            "english_used_for_correction": False,
        })
        unit_ar = a["number_label_ar"] + ((" - " + a["title_ar"]) if a.get("title_ar") else "")
        llm.append({
            "law_id": LAW_ID,
            "law_component": component,
            "article_number": n,
            "is_appendix": is_app,
            "is_mukarrar": bool(a.get("is_mukarrar")),
            "article_key": key,
            "article_title_ar": unit_ar,
            "title_ar": a.get("title_ar") or "",
            "section_ar": a.get("section_ar") or "",
            "legal_status_ar": ls,
            "is_repealed": ls == "ملغاة",
            "is_added": ls == "مضافة",
            "is_amended": ls == "معدلة",
            "text_complete": a.get("text_complete", True),
            "record_id": "environmental-wildlife-hunting-reg-llm-%03d" % idx,
            "record_type": "verified_arabic_article",
            "language": "ar",
            "governing_text_language": "ar",
            "article_text_ar": text,
            "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "llm_title_ar": "%s — %s" % (LAW_AR, unit_ar),
            "retrieval_title_ar": "%s - %s" % (LAW_AR, unit_ar),
            "article_path": "environmental_wildlife_hunting/%s/%s" % (component, key),
            "keywords_ar": _kw(text),
            "search_queries_ar": [
                "%s %s" % (a["number_label_ar"], LAW_AR),
                "%s %s" % (LAW_AR, a["number_label_ar"]),
                "%s من اللائحة التنفيذية لصيد الكائنات الفطرية البرية" % a["number_label_ar"],
            ],
            "text_status": a["status"],
            "source_trust": {
                "source_authority": ("Ministerial Decision (Minister of Environment, Water "
                                     "and Agriculture) No. (312179/1/1442) (4/6/1442H) -- "
                                     "full text from an official mewa.gov.sa-hosted PDF, "
                                     "read visually page-by-page; founding decree citation "
                                     "cross-confirmed via the Umm Al-Qura Gazette page "
                                     "publishing the later Table-1 amendment (Decision "
                                     "15029615, 5/2/1446H); laws.boe.gov.sa unreachable "
                                     "(HTTP 503) this pass"),
                "source_authority_ar": ("قرار وزير البيئة والمياه والزراعة رقم "
                                        "(312179/1/1442) وتاريخ 4/6/1442هـ — النص الكامل من "
                                        "ملف PDF رسمي مستضاف على mewa.gov.sa، قُرئ بصرياً "
                                        "صفحة بصفحة؛ رقم القرار المؤسس مؤكد بشكل مستقل عبر "
                                        "صفحة جريدة أم القرى الناشرة لتعديل الجدول (١) لاحقاً "
                                        "(القرار رقم 15029615 وتاريخ 5/2/1446هـ)؛ بوابة هيئة "
                                        "الخبراء (laws.boe.gov.sa) غير قابلة للوصول (HTTP "
                                        "503) هذه الجولة"),
                "source_status": a["status"].lower(),
                "source_document_ar": LAW_AR,
                "legal_status_ar": ls,
                "verification_status": a["status"],
            },
            "translation_performed": False,
            "legal_interpretation_performed": False,
            "english_used_for_correction": False,
            "text_summarized_or_paraphrased": False,
        })

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({
        "law_key": "environmental_wildlife_hunting",
        "layer": "ENVIRONMENTAL_WILDLIFE_HUNTING_REG_ARABIC_VERIFIED_TEXT",
        "record_count": len(ver),
        "article_count": src["article_count"],
        "appendix_count": src["appendix_count"],
        "status_counts": src["status_counts"],
        "decree": src["decree"],
        "decree_date_hijri": src["decree_date_hijri"],
        "amending_decree": src["amending_decree"],
        "amending_decree_date_hijri": src["amending_decree_date_hijri"],
        "amending_decree_scope": src["amending_decree_scope"],
        "gazette_ar": src["gazette_ar"],
        "legal_basis_ar": src["legal_basis_ar"],
        "base_law_track": src["base_law_track"],
        "legal_status_ar": src["legal_status_ar"],
        "consolidated_amended_law": src.get("consolidated_amended_law", False),
        "amendment_history": src.get("amendment_history", []),
        "chapter_structure": src["chapter_structure"],
        "verification_methodology_note": src["verification_methodology_note"],
        "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
        "source_artifact": os.path.relpath(SRC, ROOT),
    }, open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({
        "layer_id": "sa-environmental-wildlife-hunting-reg-arabic-legal-llm-full",
        "law_id": LAW_ID,
        "law_component": "regulation",
        "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (13 سجلاً: 10 مواد "
                             "+ الجدول (١) تصنيف المخالفات والعقوبات + الجدول (٢) غرامات صيد "
                             "الكائنات الحية + الملحق (١) قائمة الطيور المتوطنة؛ جميعها أصلية)",
        "title_en": ("Implementing Regulation for Hunting of Wild Terrestrial Animals — "
                     "Arabic LLM-ready layer (13 records: 10 articles + Table 1 violation/"
                     "penalty classification + Table 2 live-animal hunting fines + Appendix 1 "
                     "endemic bird list; all original)"),
        "record_type": "verified_arabic_article",
        "language": "ar",
        "governing_text_language": "ar",
        "record_count": len(llm),
        "article_count": src["article_count"],
        "appendix_count": src["appendix_count"],
        "article_range": [1, 10],
        "text_status": STATUS_UNCHANGED,
        "consolidated_amended_law": src.get("consolidated_amended_law", False),
        "status_counts": src["status_counts"],
        "not_legal_advice": True,
        "records": llm,
    }, open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Wildlife Hunting Regulation records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
