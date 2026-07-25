#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Real Estate Brokerage Law track
(اللائحة التنفيذية لنظام الوساطة العقارية، قرار مجلس إدارة الهيئة العامة للعقار
رقم (132/ق) وتاريخ 24/06/1444هـ، صادرة استنادًا إلى المادة (الثالثة والعشرين)
من نظام الوساطة العقارية -- المرسوم الملكي رقم م/130 وتاريخ 30/11/1443هـ، الذي
له مسار منفصل في هذه المدونة: sources/real_estate_brokerage/law، track_id
real_estate_brokerage).

Source: REGA's own hosted PDF (rega.gov.sa/media/1mjbk4f5/...الوساطة.pdf,
23 pages, fetched directly HTTP 200). The PDF carries a genuine digital text
layer (Word-exported PDF 1.7, not a scanned image), but automated extraction
of that layer (pdftotext, PyMuPDF) produces known Arabic lam-alef/RTL
reordering artifacts (e.g. "الالئحة" instead of "اللائحة"). The GOVERNING text
here is therefore a direct VISUAL transcription of every one of the 23 pages
rendered at 300dpi, cross-verified programmatically against the full raw text
extracted directly from the official Umm al-Qura Gazette portal's own page
(uqn.gov.sa/details?p=21268, fetched directly -- not summarized) -- word-for-
word identical across all 27 articles except one immaterial one-word
preposition variant in Article 14 item 10 (عن/على), disclosed in
known_unresolved_discrepancies. Decision number/date (132/ق, 24/06/1444H)
independently confirmed by two further secondary sources (lexismiddleeast.com
search-index, snadlaw.sa direct fetch). laws.boe.gov.sa was connection-reset
(consistent with this being a REGA Board decision, not separately indexed
there, a pattern also seen in standards_quality_regulation/traffic_regulation).

VERIFICATION TIER: TIER_1 -- see the source artifact's
verification_methodology_note for the full account, including an explicit
honesty flag: a claimed subsequent amending decision ("5-23-م-23 لسنة 1444هـ")
surfaced via one AI-summarized web fetch but could NOT be independently
verified (the underlying URL 404s on direct fetch; no other source mentions
it) and is therefore NOT applied to any article here -- all 27 articles are
اصلية (fresh, single issuance, 0 معدلة / 0 ملغاة / 0 مضافة).

27 records across 8 فصول (Article 1 is unsectioned definitions, before
"الفصل الأول" begins): licensing rules (2-6) -- license duration/renewal/
termination (7-11) -- brokers' registry (12-13) -- conduct rules (14-15) --
brokerage contracts (16-19) -- guarantee/earnest-money rules (20-22) --
supervision/inspection (23-25) -- violations committee (26-27). Two annex
tables (penalty-classification table; city/governorate/center classification
table) exist in the official document but are NOT extracted as separate
structured LLM records in this pass -- disclosed as an honest, documented
scope limitation in known_unresolved_discrepancies (this track's scope is the
27 numbered مواد, matching the base law's own convention and this corpus's
"article" atomic unit).

NO PREDECESSOR REGULATION: this is the FIRST Implementing Regulation issued
under the (itself freshly-issued, 1443H) base Real Estate Brokerage Law; no
supersession edge is required. (The base law's own Article 22 repealed an
older, different instrument -- لائحة تنظيم المكاتب العقارية, 1398H -- but that
repeal is documented in the separate real_estate_brokerage track, not here.)

law_component is "regulation" throughout (distinguishing every record here
from the separate base-law track, track_id: real_estate_brokerage,
law_component: "law"). Arabic governs; no translation, paraphrase or
interpretation performed. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "real_estate_brokerage_regulation", "law", "official_source",
                   "real_estate_brokerage_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "real_estate_brokerage_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "real_estate_brokerage_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "real_estate_brokerage_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "real_estate_brokerage_regulation_arabic_legal_llm",
                        "real_estate_brokerage_regulation_legal_llm_001_027.json")

LAW_ID = "sa-real-estate-brokerage-regulation-132-1444"
LAW_AR = "اللائحة التنفيذية لنظام الوساطة العقارية"
KEY_RE = r"real_estate_brokerage_regulation_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك التالية التالي").split())

STATUS_MAIN = "REGA_OFFICIAL_PDF_VISUALLY_VERIFIED_X_UQN_GAZETTE_FULLTEXT_CROSSCHECK_TIER1_BOE_UNREACHABLE"

GOV_NOTE = ("Arabic governs. Governing text is a direct VISUAL transcription of all 23 pages of "
            "REGA's own hosted official PDF (rega.gov.sa/media/1mjbk4f5/...), fetched directly "
            "(HTTP 200) -- automated text-layer extraction (pdftotext/PyMuPDF) produces known Arabic "
            "lam-alef/RTL reordering artifacts and was NOT used as the governing text. Cross-verified "
            "programmatically, word-for-word, against the full raw text of the official Umm al-Qura "
            "Gazette portal's own page (uqn.gov.sa/details?p=21268, fetched directly): identical "
            "across all 27 articles except one immaterial one-word preposition variant in Article 14 "
            "item 10 (عن/على, disclosed). Decision identity (132/ق, 24/06/1444H) independently "
            "confirmed by two further secondary sources (lexismiddleeast.com, snadlaw.sa). A claimed "
            "subsequent amendment surfaced via one AI-summarized web fetch could NOT be independently "
            "verified (the underlying URL 404s on direct fetch) and is explicitly NOT applied here -- "
            "see known_unresolved_discrepancies in the source artifact before relying on this track's "
            "provenance.")

SRC_AUTH = ("REGA Board of Directors Decision No. (132/ق), 24/06/1444H, issued pursuant to Article 23 "
            "of the Real Estate Brokerage Law (Royal Decree M/130, 30/11/1443H); published on the "
            "Umm al-Qura Gazette portal (available 25/06/1444H = 18 Jan 2023G per direct fetch of the "
            "gazette's own page). PRIMARY full text from REGA's own hosted PDF (visually verified); "
            "independently cross-checked word-for-word against the Umm al-Qura Gazette portal's own "
            "raw page text (fetched directly) -> TIER_1.")

SRC_AUTH_AR = ("قرار مجلس إدارة الهيئة العامة للعقار رقم (132/ق) وتاريخ 24/06/1444هـ، صادر استنادًا "
               "إلى المادة (الثالثة والعشرين) من نظام الوساطة العقارية (المرسوم الملكي رقم م/130 "
               "وتاريخ 30/11/1443هـ)؛ منشورة على بوابة جريدة أم القرى (تاريخ الإتاحة 25/06/1444هـ "
               "الموافق 18 يناير 2023م بحسب الجلب المباشر لصفحة الجريدة نفسها). النص الأساسي من ملف "
               "REGA الرسمي المستضاف مباشرة (مُتحقَّق منه بصريًا)؛ مطابق حرفيًا -بشكل مستقل- لنص بوابة "
               "جريدة أم القرى الخام المجلوب مباشرة -> TIER_1.")


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
        is_repealed = ls == "ملغاة"
        text = a["text"]
        ver.append({"law_key": "real_estate_brokerage_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "REAL_ESTATE_BROKERAGE_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": bool(a.get("is_mukarrar")),
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "secondary_cross_check": a.get("secondary_cross_check"),
                    "official_text_status": STATUS_MAIN,
                    "governing_source_note": GOV_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": bool(a.get("is_mukarrar")), "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "real-estate-brokerage-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "real_estate_brokerage_regulation/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d اللائحة التنفيذية لنظام الوساطة العقارية" % n],
                    "text_status": STATUS_MAIN,
                    "source_trust": {"source_authority": SRC_AUTH,
                                     "source_authority_ar": SRC_AUTH_AR,
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "real_estate_brokerage_regulation",
               "layer": "REAL_ESTATE_BROKERAGE_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS_MAIN,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "visually_adjudicated": src["stats"]["visually_adjudicated"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-real-estate-brokerage-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (27 مادة؛ إصدار تأسيسي كامل: 27 أصلية)",
               "title_en": ("Implementing Regulation of the Real Estate Brokerage Law — Arabic "
                            "LLM-ready layer (27 records, all original)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 27], "text_status": STATUS_MAIN,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Real Estate Brokerage Regulation records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
