#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the تنظيم الهيئة السعودية للسياحة track.

CITATION: no issuing decision number is stated in the official gazette source; the confirmed anchor is the gazette publication date.
Text fetched directly from the Umm Al-Qura Official Gazette's own
server-rendered HTML page (uqn.gov.sa/details?p=24561),
published 13/8/1445H (2024-02-23). The Gazette IS the official publication of record
for Saudi laws/regulations -- a direct primary-source fetch, matching this
corpus's established UQN_GAZETTE_DIRECT_FETCH_TIER1 precedent.

VERIFICATION TIER -- TIER_1. See the official_source JSON's
verification_methodology_note and known_unresolved_discrepancies.

STRUCTURE: 15 numbered articles, no appendix records. All اصلية.

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
SRC = os.path.join(ROOT, "sources", "saudi_tourism_authority_statute", "official_source",
                   "saudi_tourism_authority_statute_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "saudi_tourism_authority_statute", "verified")
RECORDS = os.path.join(OUT_VER, "saudi_tourism_authority_statute_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "saudi_tourism_authority_statute_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "saudi_tourism_authority_statute_arabic_legal_llm",
                        "saudi_tourism_authority_statute_legal_llm_001_015.json")

LAW_ID = "sa-saudi-tourism-authority-statute"
LAW_AR = "تنظيم الهيئة السعودية للسياحة"
STATUS_UNCHANGED = "UNCHANGED"
ART_RE = r"saudi_tourism_authority_statute_art_(\d{3})$"

STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم النظام اللوائح الجهة المختصة الوزارة الهيئة").split())


def _sort_key(key):
    return int(re.match(ART_RE, key).group(1))


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
                "Official Gazette's own server-rendered HTML page "
                "(uqn.gov.sa/details?p=24561), published 13/8/1445H (2024-02-23). "
                "The Gazette is the official publication of record for Saudi laws/"
                "regulations -- a direct primary-source fetch, matching this corpus's "
                "established UQN_GAZETTE_DIRECT_FETCH_TIER1 precedent. TIER_1. See "
                "verification_methodology_note and known_unresolved_discrepancies in the "
                "source artifact before relying on this track.")

    ver, llm = [], []
    for idx, key in enumerate(keys, start=1):
        a = arts[key]
        n = a["article_number"]
        ls = a.get("legal_status_ar")
        text = a["text"]
        ver.append({
            "law_key": "saudi_tourism_authority_statute",
            "law_component": "statute",
            "language": "ar",
            "record_layer": "SAUDI_TOURISM_AUTHORITY_STATUTE_ARABIC_VERIFIED_TEXT",
            "article_number": n,
            "is_appendix": False,
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
        unit_ar = a["number_label_ar"]
        llm.append({
            "law_id": LAW_ID,
            "law_component": "statute",
            "article_number": n,
            "is_appendix": False,
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
            "record_id": "saudi-tourism-authority-statute-llm-%03d" % idx,
            "record_type": "verified_arabic_article",
            "language": "ar",
            "governing_text_language": "ar",
            "article_text_ar": text,
            "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "llm_title_ar": "%s — %s" % (LAW_AR, unit_ar),
            "retrieval_title_ar": "%s - %s" % (LAW_AR, unit_ar),
            "article_path": "saudi_tourism_authority_statute/statute/%s" % key,
            "keywords_ar": _kw(text),
            "search_queries_ar": [
                "%s %s" % (a["number_label_ar"], LAW_AR),
                "%s %s" % (LAW_AR, a["number_label_ar"]),
            ],
            "text_status": a["status"],
            "source_trust": {
                "source_authority": ("Statute of the Saudi Tourism Authority -- full text fetched directly from the Umm "
                                     "Al-Qura Official Gazette's own HTML rendering "
                                     "(published 13/8/1445H / 2024-02-23)"),
                "source_authority_ar": ("تنظيم الهيئة السعودية للسياحة — النص الكامل جُلب مباشرة من صفحة جريدة أم "
                                        "القرى الرسمية (تاريخ النشر 13/8/1445هـ الموافق 2024-02-23م)"),
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
        "law_key": "saudi_tourism_authority_statute",
        "layer": "SAUDI_TOURISM_AUTHORITY_STATUTE_ARABIC_VERIFIED_TEXT",
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
        "layer_id": "saudi-tourism-authority-statute-arabic-legal-llm-full",
        "law_id": LAW_ID,
        "law_component": "statute",
        "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (15 مادة، جميعها أصلية)",
        "title_en": "Statute of the Saudi Tourism Authority — Arabic LLM-ready layer (15 articles; all original)",
        "record_type": "verified_arabic_article",
        "language": "ar",
        "governing_text_language": "ar",
        "record_count": len(llm),
        "article_count": src["article_count"],
        "appendix_count": src["appendix_count"],
        "article_range": [1, 15],
        "text_status": STATUS_UNCHANGED,
        "consolidated_amended_law": src.get("consolidated_amended_law", False),
        "status_counts": src["status_counts"],
        "not_legal_advice": True,
        "records": llm,
    }, open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Statute of the Saudi Tourism Authority records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
