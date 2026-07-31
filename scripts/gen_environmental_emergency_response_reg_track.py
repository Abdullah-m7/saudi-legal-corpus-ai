#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Executive Regulation on Controls for Preparing and
Implementing Environmental Emergency and Disaster Preparedness and
Response Plans track (اللائحة التنفيذية لضوابط إعداد وتنفيذ خطط التأهب
والاستجابة لحالات الطوارئ والكوارث البيئية).

Companion regulation to the already-ingested base Environmental Law track
(corpus key `environmental`, Royal Decree M/165, 19/11/1441H) -- same
family as environmental_wildlife_hunting / environmental_noise /
environmental_protected_areas / etc.

CITATION: no independent ministerial/CoM decision number was found for this
specific regulation. Text fetched directly from the Umm Al-Qura Official
Gazette's own HTML rendering of the full regulation (uqn.gov.sa/details?
p=24377), published 7/7/1445H (19/01/2024G). The Gazette IS the official
publication of record for Saudi laws/regulations -- a direct primary-source
fetch, matching this corpus's established UQN_GAZETTE_DIRECT_FETCH_TIER1
precedent. No matching PDF was found in MEWA's RulesLibrary this pass.

VERIFICATION TIER -- TIER_1 (direct fetch from the official Gazette itself).
See the official_source JSON's verification_methodology_note.

STRUCTURE: 11 numbered articles (المادة الأولى .. الحادية عشرة, no chapter
division) + 1 appendix-type record: الجدول (١) المخالفات والعقوبات (14 rows).
article_count=11, appendix_count=1, record_count=12, all اصلية (fresh
issuance, no amendment history).

TEXT HANDLING: verbatim Arabic as rendered by the official Gazette's own
HTML. Arabic governs; no translation / paraphrase / interpretation.
Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "environmental_emergency_response",
                   "official_source",
                   "environmental_emergency_response_reg_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "environmental_emergency_response", "verified")
RECORDS = os.path.join(OUT_VER, "environmental_emergency_response_reg_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "environmental_emergency_response_reg_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "environmental_emergency_response_reg_arabic_legal_llm",
                        "environmental_emergency_response_reg_legal_llm_001_012.json")

LAW_ID = "sa-environmental-emergency-response-reg-m165-1441"
LAW_AR = "اللائحة التنفيذية لضوابط إعداد وتنفيذ خطط التأهب والاستجابة لحالات الطوارئ والكوارث البيئية"
STATUS_UNCHANGED = "UNCHANGED"
ART_RE = r"environmental_emergency_response_reg_art_(\d{3})$"
APP_RE = r"environmental_emergency_response_reg_appendix_(\d{3})$"

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

    gov_note = ("Arabic governs; PRIMARY full text fetched directly from the Umm Al-Qura "
                "Official Gazette's own HTML rendering of the regulation "
                "(uqn.gov.sa/details?p=24377), published 7/7/1445H (19/01/2024G). The "
                "Gazette is the official publication of record for Saudi laws/regulations -- "
                "a direct primary-source fetch, matching this corpus's established "
                "UQN_GAZETTE_DIRECT_FETCH_TIER1 precedent. No matching PDF was found in "
                "MEWA's RulesLibrary this pass. No independent ministerial/CoM decision "
                "number was found for this specific regulation this pass. TIER_1. See "
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
            "law_key": "environmental_emergency_response",
            "law_component": component,
            "language": "ar",
            "record_layer": "ENVIRONMENTAL_EMERGENCY_RESPONSE_REG_ARABIC_VERIFIED_TEXT",
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
            "record_id": "environmental-emergency-response-reg-llm-%03d" % idx,
            "record_type": "verified_arabic_article",
            "language": "ar",
            "governing_text_language": "ar",
            "article_text_ar": text,
            "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "llm_title_ar": "%s — %s" % (LAW_AR, unit_ar),
            "retrieval_title_ar": "%s - %s" % (LAW_AR, unit_ar),
            "article_path": "environmental_emergency_response/%s/%s" % (component, key),
            "keywords_ar": _kw(text),
            "search_queries_ar": [
                "%s %s" % (a["number_label_ar"], LAW_AR),
                "%s %s" % (LAW_AR, a["number_label_ar"]),
                "%s من اللائحة التنفيذية للطوارئ والكوارث البيئية" % a["number_label_ar"],
            ],
            "text_status": a["status"],
            "source_trust": {
                "source_authority": ("Executive Regulation on environmental emergency/"
                                     "disaster preparedness and response plans, issued "
                                     "under the Environmental Law (Royal Decree M/165, "
                                     "19/11/1441H); no independent decision number found "
                                     "this pass; full text fetched directly from the Umm "
                                     "Al-Qura Official Gazette's own HTML rendering "
                                     "(published 7/7/1445H / 19/01/2024G)"),
                "source_authority_ar": ("اللائحة التنفيذية لضوابط إعداد وتنفيذ خطط التأهب "
                                        "والاستجابة لحالات الطوارئ والكوارث البيئية، صادرة "
                                        "تنفيذاً لنظام البيئة (م/165 وتاريخ 19/11/1441هـ)؛ لم "
                                        "يُعثر على رقم قرار مستقل هذه الجولة؛ النص الكامل جُلب "
                                        "مباشرة من صفحة جريدة أم القرى الرسمية (تاريخ النشر "
                                        "7/7/1445هـ الموافق 19/01/2024م)"),
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
        "law_key": "environmental_emergency_response",
        "layer": "ENVIRONMENTAL_EMERGENCY_RESPONSE_REG_ARABIC_VERIFIED_TEXT",
        "record_count": len(ver),
        "article_count": src["article_count"],
        "appendix_count": src["appendix_count"],
        "status_counts": src["status_counts"],
        "decree": src["decree"],
        "decree_date_hijri": src["decree_date_hijri"],
        "gazette_publication_date_hijri": src["gazette_publication_date_hijri"],
        "gazette_publication_date_gregorian": src["gazette_publication_date_gregorian"],
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
        "layer_id": "sa-environmental-emergency-response-reg-arabic-legal-llm-full",
        "law_id": LAW_ID,
        "law_component": "regulation",
        "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (12 سجلاً: 11 مادة "
                             "+ الجدول (١) المخالفات والعقوبات؛ جميعها أصلية)",
        "title_en": ("Executive Regulation on Environmental Emergency/Disaster Preparedness "
                     "and Response Plans — Arabic LLM-ready layer (12 records: 11 articles + "
                     "Table 1 violations/penalties; all original)"),
        "record_type": "verified_arabic_article",
        "language": "ar",
        "governing_text_language": "ar",
        "record_count": len(llm),
        "article_count": src["article_count"],
        "appendix_count": src["appendix_count"],
        "article_range": [1, 11],
        "text_status": STATUS_UNCHANGED,
        "consolidated_amended_law": src.get("consolidated_amended_law", False),
        "status_counts": src["status_counts"],
        "not_legal_advice": True,
        "records": llm,
    }, open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Emergency Response Regulation records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
