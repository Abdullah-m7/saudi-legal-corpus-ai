#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Executive Regulation for Noise track (اللائحة التنفيذية للضوضاء).

Companion regulation to the already-ingested base Environmental Law track
(corpus key `environmental`, Royal Decree M/165, 19/11/1441H) -- same
"companion regulation to an already-ingested base law" pattern as
environmental_wildlife_hunting / environmental_inspection_audit / etc.

CITATION: no independent ministerial/CoM decision number was found for this
specific regulation; it appears to be issued directly under the National
Center for Environmental Compliance's own authority per the Environmental
Law. Published in the Umm Al-Qura Gazette, dated 15/11/1442H (25/06/2021G).

VERIFICATION TIER -- genuine TIER_1_PRIMARY_MULTI_SOURCE: text cross-verified
from TWO independent official primary sources that match verbatim, including
a genuine drafting anomaly preserved without silent correction (Article 11
cites "الجدول (1)" for the penalties table, which is itself printed as
"الجدول (5)"). See the official_source JSON's verification_methodology_note.

STRUCTURE: 11 numbered articles (المادة الأولى .. الحادية عشرة, no chapter
division) + 2 appendix-type records: الجدول (٥) المخالفات والعقوبات and
الملحق (١) اشتراطات رصد مستويات الضوضاء. article_count=11, appendix_count=2,
record_count=13, all اصلية (fresh issuance, no amendment history).

TEXT HANDLING: verbatim Arabic, cross-checked between the official MEWA PDF
(visually confirmed) and the Umm Al-Qura Gazette's own HTML rendering.
Arabic governs; no translation / paraphrase / interpretation. Read-only over
input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "environmental_noise",
                   "official_source",
                   "environmental_noise_reg_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "environmental_noise", "verified")
RECORDS = os.path.join(OUT_VER, "environmental_noise_reg_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "environmental_noise_reg_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "environmental_noise_reg_arabic_legal_llm",
                        "environmental_noise_reg_legal_llm_001_013.json")

LAW_ID = "sa-environmental-noise-reg-m165-1441"
LAW_AR = "اللائحة التنفيذية للضوضاء"
STATUS_UNCHANGED = "UNCHANGED"
ART_RE = r"environmental_noise_reg_art_(\d{3})$"
APP_RE = r"environmental_noise_reg_appendix_(\d{3})$"

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

    gov_note = ("Arabic governs; text cross-verified from TWO independent official primary "
                "sources that match verbatim: (1) an official MEWA RulesLibrary PDF "
                "(mewa.gov.sa), native Word-generated text, visually confirmed page-by-page "
                "(150dpi); (2) the Umm Al-Qura Gazette's own HTML rendering of the regulation "
                "(uqn.gov.sa, published 15/11/1442H / 25/06/2021G). A genuine drafting anomaly "
                "in the official text itself (Article 11 cites 'Table (1)' for the penalties "
                "table, which is itself printed as 'Table (5)') is preserved verbatim, not "
                "silently corrected, since it appears identically in both independent sources. "
                "Genuine TIER_1_PRIMARY_MULTI_SOURCE. No independent ministerial/CoM decision "
                "number was found for this specific regulation this pass. See "
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
            "law_key": "environmental_noise",
            "law_component": component,
            "language": "ar",
            "record_layer": "ENVIRONMENTAL_NOISE_REG_ARABIC_VERIFIED_TEXT",
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
            "record_id": "environmental-noise-reg-llm-%03d" % idx,
            "record_type": "verified_arabic_article",
            "language": "ar",
            "governing_text_language": "ar",
            "article_text_ar": text,
            "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "llm_title_ar": "%s — %s" % (LAW_AR, unit_ar),
            "retrieval_title_ar": "%s - %s" % (LAW_AR, unit_ar),
            "article_path": "environmental_noise/%s/%s" % (component, key),
            "keywords_ar": _kw(text),
            "search_queries_ar": [
                "%s %s" % (a["number_label_ar"], LAW_AR),
                "%s %s" % (LAW_AR, a["number_label_ar"]),
                "%s من اللائحة التنفيذية للضوضاء" % a["number_label_ar"],
            ],
            "text_status": a["status"],
            "source_trust": {
                "source_authority": ("Executive Regulation for Noise, issued under the "
                                     "Environmental Law (Royal Decree M/165, 19/11/1441H); "
                                     "no independent decision number found this pass; "
                                     "published in the Umm Al-Qura Gazette, 15/11/1442H "
                                     "(25/06/2021G); text cross-verified verbatim between "
                                     "the official MEWA PDF and the Gazette's own HTML "
                                     "rendering, including a genuine drafting anomaly "
                                     "preserved from both sources"),
                "source_authority_ar": ("اللائحة التنفيذية للضوضاء، صادرة تنفيذاً لنظام "
                                        "البيئة (م/165 وتاريخ 19/11/1441هـ)؛ لم يُعثر على "
                                        "رقم قرار مستقل هذه الجولة؛ منشورة في جريدة أم القرى "
                                        "بتاريخ 15/11/1442هـ الموافق 25/06/2021م؛ النص مؤكد "
                                        "حرفياً بين ملف PDF وزارة البيئة الرسمي وعرض الجريدة "
                                        "الرسمية نفسه، بما في ذلك تناقض توصيف أصلي محفوظ من "
                                        "كلا المصدرين"),
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
        "law_key": "environmental_noise",
        "layer": "ENVIRONMENTAL_NOISE_REG_ARABIC_VERIFIED_TEXT",
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
        "layer_id": "sa-environmental-noise-reg-arabic-legal-llm-full",
        "law_id": LAW_ID,
        "law_component": "regulation",
        "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (13 سجلاً: 11 مادة "
                             "+ الجدول (٥) المخالفات والعقوبات + الملحق (١) اشتراطات رصد "
                             "مستويات الضوضاء؛ جميعها أصلية)",
        "title_en": ("Executive Regulation for Noise — Arabic LLM-ready layer (13 records: "
                     "11 articles + Table 5 violations/penalties + Annex 1 noise-monitoring "
                     "requirements; all original)"),
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
    print("Wrote %d verified + %d LLM-ready Noise Regulation records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
