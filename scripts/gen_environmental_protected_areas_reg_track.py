#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Executive Regulation for Protected Areas track
(اللائحة التنفيذية للمناطق المحمية).

Companion regulation to the already-ingested base Environmental Law track
(corpus key `environmental`, Royal Decree M/165, 19/11/1441H) -- same family
as environmental_wildlife_hunting / environmental_noise / etc.

CITATION: no independent ministerial/CoM decision number was found for this
specific regulation; issued under the Environmental Law's own authority via
the National Center for Wildlife Development (NCW). Text extracted from an
official mewa.gov.sa RulesLibrary PDF, confirmed byte-identical (sha256/md5)
to the same file independently hosted on NCW's own site
(ncw.gov.sa/assets/files/regulations/regulations-for-protected-areas.pdf) --
i.e. the same file is served from two independent official .gov.sa domains.

VERIFICATION TIER -- TIER_2 (single primary text source, visually read;
independently re-hosted on a second official domain, but no independently-
transcribed second full-text source like the sibling environmental_noise
track had). See the official_source JSON's verification_methodology_note.

STRUCTURE: 10 numbered articles (المادة الأولى .. العاشرة, no chapter
division) + 1 appendix-type record: الجدول (١) المخالفات والعقوبات (32 rows).
article_count=10, appendix_count=1, record_count=11, all اصلية (fresh
issuance as ingested, no amendment history confirmed this pass).

TEXT HANDLING: verbatim Arabic from the visually-read PDF pages (the
automated pypdf/pdftotext text layer for this specific file is corrupted --
dropped letters). Arabic governs; no translation / paraphrase /
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "environmental_protected_areas",
                   "official_source",
                   "environmental_protected_areas_reg_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "environmental_protected_areas", "verified")
RECORDS = os.path.join(OUT_VER, "environmental_protected_areas_reg_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "environmental_protected_areas_reg_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "environmental_protected_areas_reg_arabic_legal_llm",
                        "environmental_protected_areas_reg_legal_llm_001_011.json")

LAW_ID = "sa-environmental-protected-areas-reg-m165-1441"
LAW_AR = "اللائحة التنفيذية للمناطق المحمية"
STATUS_UNCHANGED = "UNCHANGED"
ART_RE = r"environmental_protected_areas_reg_art_(\d{3})$"
APP_RE = r"environmental_protected_areas_reg_appendix_(\d{3})$"

STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم النظام اللوائح الجهة المختصة المركز الوزارة").split())


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

    gov_note = ("Arabic governs; PRIMARY full text is an official mewa.gov.sa-hosted PDF, "
                "READ VISUALLY page-by-page (150dpi) because the automated pypdf/pdftotext "
                "text layer for this specific file is corrupted (dropped letters). The file "
                "is confirmed byte-identical (sha256/md5) to the same PDF independently "
                "hosted on the National Center for Wildlife Development's own site "
                "(ncw.gov.sa) -- the same competent Center referenced throughout this "
                "regulation's own text -- served from two independent official .gov.sa "
                "domains. No independent ministerial/CoM decision number was found for this "
                "specific regulation this pass. TIER_2. See verification_methodology_note "
                "and known_unresolved_discrepancies in the source artifact before relying "
                "on this track.")

    ver, llm = [], []
    for idx, key in enumerate(keys, start=1):
        a = arts[key]
        is_app = bool(a.get("is_appendix"))
        n = a["article_number"]
        ls = a.get("legal_status_ar")
        text = a["text"]
        component = "appendix" if is_app else "regulation"
        ver.append({
            "law_key": "environmental_protected_areas",
            "law_component": component,
            "language": "ar",
            "record_layer": "ENVIRONMENTAL_PROTECTED_AREAS_REG_ARABIC_VERIFIED_TEXT",
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
            "record_id": "environmental-protected-areas-reg-llm-%03d" % idx,
            "record_type": "verified_arabic_article",
            "language": "ar",
            "governing_text_language": "ar",
            "article_text_ar": text,
            "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "llm_title_ar": "%s — %s" % (LAW_AR, unit_ar),
            "retrieval_title_ar": "%s - %s" % (LAW_AR, unit_ar),
            "article_path": "environmental_protected_areas/%s/%s" % (component, key),
            "keywords_ar": _kw(text),
            "search_queries_ar": [
                "%s %s" % (a["number_label_ar"], LAW_AR),
                "%s %s" % (LAW_AR, a["number_label_ar"]),
                "%s من اللائحة التنفيذية للمناطق المحمية" % a["number_label_ar"],
            ],
            "text_status": a["status"],
            "source_trust": {
                "source_authority": ("Executive Regulation for Protected Areas, issued under "
                                     "the Environmental Law (Royal Decree M/165, "
                                     "19/11/1441H); no independent decision number found "
                                     "this pass; full text from an official mewa.gov.sa-"
                                     "hosted PDF, read visually page-by-page; confirmed "
                                     "byte-identical to the same file independently hosted "
                                     "on ncw.gov.sa (the competent Center)"),
                "source_authority_ar": ("اللائحة التنفيذية للمناطق المحمية، صادرة تنفيذاً "
                                        "لنظام البيئة (م/165 وتاريخ 19/11/1441هـ)؛ لم يُعثر "
                                        "على رقم قرار مستقل هذه الجولة؛ النص الكامل من ملف "
                                        "PDF رسمي على mewa.gov.sa، قُرئ بصرياً صفحة بصفحة؛ "
                                        "مؤكد مطابقاً حرفياً لنفس الملف المستضاف بشكل مستقل "
                                        "على ncw.gov.sa (المركز المختص)"),
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
        "law_key": "environmental_protected_areas",
        "layer": "ENVIRONMENTAL_PROTECTED_AREAS_REG_ARABIC_VERIFIED_TEXT",
        "record_count": len(ver),
        "article_count": src["article_count"],
        "appendix_count": src["appendix_count"],
        "status_counts": src["status_counts"],
        "decree": src["decree"],
        "decree_date_hijri": src["decree_date_hijri"],
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
        "layer_id": "sa-environmental-protected-areas-reg-arabic-legal-llm-full",
        "law_id": LAW_ID,
        "law_component": "regulation",
        "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (11 سجلاً: 10 مواد "
                             "+ الجدول (١) المخالفات والعقوبات؛ جميعها أصلية)",
        "title_en": ("Executive Regulation for Protected Areas — Arabic LLM-ready layer "
                     "(11 records: 10 articles + Table 1 violations/penalties; all original)"),
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
    print("Wrote %d verified + %d LLM-ready Protected Areas Regulation records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
