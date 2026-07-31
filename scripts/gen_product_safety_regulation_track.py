#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Executive Regulation of the Product Safety Law track
(اللائحة التنفيذية لنظام سلامة المنتجات).

Companion regulation to the already-ingested base Product Safety Law track
(corpus key `product_safety`, Royal Decree M/36, 29/1/1446H).

CITATION: approved by SASO Board of Directors Decision No. (203), dated
15/11/2024G (1446-5-20H), per Cabinet Resolution No. (93) dated 24/1/1446H.
Text fetched directly from the Umm Al-Qura Official Gazette's own HTML
rendering of the full regulation (uqn.gov.sa/details?p=26781), published
1446-5-20H (22 November 2024G). The Gazette IS the official publication of
record for Saudi laws/regulations -- a direct primary-source fetch, matching
this corpus's established UQN_GAZETTE_DIRECT_FETCH_TIER1 precedent. The
PDF download link on the gazette page itself is broken (publisher-side bug).

VERIFICATION TIER -- TIER_1 (direct fetch from the official Gazette itself).
See the official_source JSON's verification_methodology_note.

STRUCTURE: 75 numbered articles across 7 chapters (الباب الأول .. السابع),
no separate appendix records. Article 72 references "الجدول رقم (1)" and
"الجدول رقم (2)" (penalty tables) by name, but no table data is present in
this gazette page -- disclosed as a known gap, not fabricated.
article_count=75, appendix_count=0, record_count=75, all اصلية (fresh
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
SRC = os.path.join(ROOT, "sources", "product_safety", "regulation",
                   "official_source", "product_safety_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "product_safety", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "product_safety_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "product_safety_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "product_safety_regulation_arabic_legal_llm",
                        "product_safety_regulation_legal_llm_001_075.json")

LAW_ID = "sa-product-safety-regulation-m36-1446"
LAW_AR = "اللائحة التنفيذية لنظام سلامة المنتجات"
STATUS_UNCHANGED = "UNCHANGED"
ART_RE = r"product_safety_regulation_art_(\d{3})$"

STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم النظام اللوائح الجهة المختصة الهيئة المشغل").split())


def _sort_key(key):
    m = re.match(ART_RE, key)
    return int(m.group(1))


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
                "(uqn.gov.sa/details?p=26781), published 1446-5-20H (22 November 2024G). The "
                "Gazette is the official publication of record for Saudi laws/regulations -- "
                "a direct primary-source fetch, matching this corpus's established "
                "UQN_GAZETTE_DIRECT_FETCH_TIER1 precedent. Approved by SASO Board of "
                "Directors Decision No. (203), dated 15/11/2024G. TIER_1. See "
                "verification_methodology_note and known_unresolved_discrepancies in the "
                "source artifact before relying on this track.")

    ver, llm = [], []
    for idx, key in enumerate(keys, start=1):
        a = arts[key]
        n = a["article_number"]
        ls = a.get("legal_status_ar")
        text = a["text"]
        ver.append({
            "law_key": "product_safety",
            "law_component": "regulation",
            "language": "ar",
            "record_layer": "PRODUCT_SAFETY_REGULATION_ARABIC_VERIFIED_TEXT",
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
        unit_ar = a["number_label_ar"] + ((" - " + a["title_ar"]) if a.get("title_ar") else "")
        llm.append({
            "law_id": LAW_ID,
            "law_component": "regulation",
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
            "record_id": "product-safety-regulation-llm-%03d" % idx,
            "record_type": "verified_arabic_article",
            "language": "ar",
            "governing_text_language": "ar",
            "article_text_ar": text,
            "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "llm_title_ar": "%s — %s" % (LAW_AR, unit_ar),
            "retrieval_title_ar": "%s - %s" % (LAW_AR, unit_ar),
            "article_path": "product_safety/regulation/%s" % key,
            "keywords_ar": _kw(text),
            "search_queries_ar": [
                "%s %s" % (a["number_label_ar"], LAW_AR),
                "%s %s" % (LAW_AR, a["number_label_ar"]),
                "%s من اللائحة التنفيذية لنظام سلامة المنتجات" % a["number_label_ar"],
            ],
            "text_status": a["status"],
            "source_trust": {
                "source_authority": ("Executive Regulation of the Product Safety Law, "
                                     "issued by SASO under the Product Safety Law (Royal "
                                     "Decree M/36, 29/1/1446H); approved by SASO Board of "
                                     "Directors Decision No. (203) dated 15/11/2024G; full "
                                     "text fetched directly from the Umm Al-Qura Official "
                                     "Gazette's own HTML rendering (published 1446-5-20H / "
                                     "22/11/2024G)"),
                "source_authority_ar": ("اللائحة التنفيذية لنظام سلامة المنتجات، صادرة عن "
                                        "الهيئة السعودية للمواصفات والمقاييس والجودة تنفيذاً "
                                        "لنظام سلامة المنتجات (م/36 وتاريخ 29/1/1446هـ)؛ "
                                        "اعتُمدت بقرار مجلس إدارة الهيئة رقم (203) بتاريخ "
                                        "15/11/2024م؛ النص الكامل جُلب مباشرة من صفحة جريدة "
                                        "أم القرى الرسمية (تاريخ النشر 1446-5-20هـ الموافق "
                                        "22/11/2024م)"),
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
        "law_key": "product_safety",
        "layer": "PRODUCT_SAFETY_REGULATION_ARABIC_VERIFIED_TEXT",
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
        "layer_id": "sa-product-safety-regulation-arabic-legal-llm-full",
        "law_id": LAW_ID,
        "law_component": "regulation",
        "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (75 مادة، جميعها "
                             "أصلية)",
        "title_en": ("Executive Regulation of the Product Safety Law — Arabic LLM-ready "
                     "layer (75 articles; all original)"),
        "record_type": "verified_arabic_article",
        "language": "ar",
        "governing_text_language": "ar",
        "record_count": len(llm),
        "article_count": src["article_count"],
        "appendix_count": src["appendix_count"],
        "article_range": [1, 75],
        "text_status": STATUS_UNCHANGED,
        "consolidated_amended_law": src.get("consolidated_amended_law", False),
        "status_counts": src["status_counts"],
        "not_legal_advice": True,
        "records": llm,
    }, open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Product Safety Regulation records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
