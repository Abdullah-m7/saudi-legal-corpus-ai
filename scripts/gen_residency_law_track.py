#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Foreigners' Residency Law track (نظام الإقامة, also known as
the Iqama/Kafala law -- Royal (Supreme) Order No. 17/2/25/1337, 11/9/1371H).

VERIFICATION TIER -- see sources/residency/law/official_source/
residency_law_official_source.json's verification_methodology_note for the
full account. Summary:

laws.boe.gov.sa does NOT index this base 1371H law at all -- BOE's portal
only carries نظام الإقامة المميزة (the unrelated, much newer "Premium
Residency Law", Royal Decree M/106, 1440H, a separate investor/talent
long-term-residency instrument). BOE's live portal was also unreachable this
pass (connection reset). The Ministry of Interior's own hosted PDF of this
law could not be reached live (connection reset) nor recovered via the
Wayback Machine (only a dead 404 and a live-site error page were archived,
not the PDF itself).

This track is therefore built from the best-available, cross-verified
secondary reproduction of a widely-circulated compiled document titled
"نظام الإقامة والتعديلات الصادرة عليه", independently located in FOUR
separately-hosted forms: an NSHR-hosted PDF (font-corrupted, used only to
structurally confirm title/pagination/article count), two independent clean
HTML transcriptions (mohamah.net, rakadvocate.blogspot.com) agreeing
word-for-word with each other and with the PDF's own internal pagination,
and a fourth (islamport.com) independently reproducing at least part of the
identical text. Classified TIER_3 ("official source unreachable, 2+
independent secondaries agree").

65 base articles across 4 فصول (chapters, no أبواب): الفصل الأول
(1-31), الفصل الثاني (32-42), الفصل الثالث (43-49), الفصل الرابع
(50-65) -- plus 4 recoverable مكرر insertions (5, 44, 49, 62) = 69 records:
48 اصلية, 16 معدلة, 1 ملغاة (Article 37, preserved not deleted), 4 مضافة.
A confirmed-but-textually-unrecovered 5th مكرر article (61 مكرر, added by
Royal Decree M/56, 4/9/1427H) is NOT ingested -- its text could not be found
in any source checked; this is disclosed in known_unresolved_discrepancies
rather than fabricated.

REPEAL/PREDECESSOR: Article 64 states only a GENERAL repeal of all prior
orders/instructions on the subject, without naming a specific predecessor
law -- a confirmed negative finding, not a research gap.

COMPANION INSTRUMENTS NOT INGESTED THIS PASS: نظام الإقامة المميزة (Premium
Residency Law, M/106, 1440H) and its Implementing Regulation; نظام الجوازات
السفرية (Passports Law, already a separate coverage-gap candidate); Muqeem
system / exit-re-entry visa rules.

No legal text is altered beyond whitespace normalization and removing two
inconsistently-applied, spurious diacritic renderings of the single
recurring word "نظام" (confirmed via a full diacritic-frequency scan to be
the only anomalous marks in the document); see the official_source.json's
verification_methodology_note for the complete, itemized list of every
other minor cleanup applied. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "residency", "law", "official_source",
                   "residency_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "residency", "law", "verified")
RECORDS = os.path.join(OUT_VER, "residency_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "residency_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "residency_arabic_legal_llm",
                        "residency_law_legal_llm_001_069.json")

LAW_ID = "sa-residency-law-order-17-2-25-1337-1371"
LAW_AR = "نظام الإقامة"
TOP_STATUS = ("RESIDENCY_LAW_SECONDARY_CROSS_VERIFIED_MOHAMAH_RAKADVOCATE_ISLAMPORT_"
              "NSHR_PDF_STRUCTURAL_MATCH_BOE_NOT_INDEXED_MOI_LIVE_AND_WAYBACK_UNREACHABLE")
KEY_RE = r"residency_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = {"residency_art_%03d" % n for n in
                (14, 16, 25, 31, 35, 38, 43, 44, 45, 46, 47, 52, 53, 56, 60, 61)}
REPEALED_KEYS = {"residency_art_037"}
ADDED_KEYS = {"residency_art_005_mukarrar", "residency_art_044_mukarrar",
              "residency_art_049_mukarrar", "residency_art_062_mukarrar"}
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك الأجنبي البلاد الإقامة").split())


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
        ver.append({"law_key": "residency", "law_component": "law",
                    "language": "ar",
                    "record_layer": "RESIDENCY_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": TOP_STATUS,
                    "governing_source_note": ("Arabic governs; this track rests on a "
                                              "cross-verified secondary reproduction of the "
                                              "officially-circulated compiled document "
                                              "'نظام الإقامة والتعديلات الصادرة عليه' -- "
                                              "laws.boe.gov.sa does not index this 1371H base "
                                              "law at all (only the unrelated نظام الإقامة "
                                              "المميزة, M/106, 1440H, is BOE-indexed), and the "
                                              "Ministry of Interior's own hosted PDF could not "
                                              "be reached live or via Wayback this pass. TIER_3: "
                                              "official source unreachable, independent "
                                              "secondaries agree. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track for any "
                                              "single article's definitively-current wording."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "residency-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "residency/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام الإقامة" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal (Supreme) Order 17/2/25/1337 "
                                                          "(11/9/1371H) — laws.boe.gov.sa does "
                                                          "not index this law; MOI's own hosted "
                                                          "PDF unreachable live/via Wayback; "
                                                          "sourced from a cross-verified "
                                                          "secondary reproduction of the "
                                                          "officially-circulated compiled text "
                                                          "(mohamah.net, rakadvocate.blogspot.com, "
                                                          "islamport.com, NSHR PDF structural "
                                                          "cross-check)"),
                                     "source_authority_ar": "الأمر الملكي (السامي) رقم 17/2/25/1337 وتاريخ 11/9/1371هـ — هيئة الخبراء لا تُدرج هذا النظام، وموقع وزارة الداخلية غير متاح مباشرة أو عبر Wayback Machine؛ اعتُمد على نسخة ثانوية مُدقَّقة تقاطعياً من الوثيقة المُجمَّعة الرسمية المتداولة",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "residency",
               "layer": "RESIDENCY_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-residency-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (69 مادة مُدرَجة؛ 48 أصلية و16 معدلة ومادة واحدة ملغاة و4 مواد مضافة)",
               "title_en": "Foreigners' Residency Law — Arabic LLM-ready layer (69 ingested records: 48 original, 16 amended, 1 repealed, 4 added)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 65], "text_status": TOP_STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Residency Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
