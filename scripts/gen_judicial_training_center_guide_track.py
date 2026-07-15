#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Organizational Guide for the Judicial Training Center
(الدليل التنظيمي لمركز التدريب العدلي).

Source: the official MOJ legal-portal text (Council of Ministers Resolution
162, 24/04/1435H, consolidated through Resolution 621, 29/10/1440H).
BESPOKE TRACK (per explicit repo-owner decision after a scoping check-in):
this document is a hybrid of 11 numbered legal decree clauses (أولاً..حادي
عشر, establishing the Center) and 7 unnumbered organizational/descriptive
entries (an org chart, a goals/tasks overview, and 5 department
job-description blocks) that the MOJ portal itself does not treat as
change-trackable legal sections (get-Section-Changes returns 404 for all
7). Both classes are ingested — items 1-11 are the legal clauses; items
12-18 are the narrative/structural content, each flagged
is_narrative_structural_content=True with legal_status_ar/history left
None/empty (mirroring what the portal itself returns, never defaulted to
اصلية) and number_label_ar drawn honestly from the source's own heading
(never a fabricated أولاً/ثانياً-style ordinal). Item 12 (the org chart) is
converted from its source HTML <table> to a plain-text reporting-line
hierarchy and was verified exclusively by direct visual reading (not
text-similarity-scorable against a rendered table).

17 of 18 text-bearing items matched the >=0.90 floor outright (mean 0.9982,
min 0.9888, items 1-11 + 13-18); item 12 was visually adjudicated. Two
legal clauses are أمعدلة: item 2 (ثانياً, the Center's goal clause, 3
versions: 1435H original -> amended by Resolution 7/1437H -> amended again
by Resolution 621/1440H, current) and item 6 (سادساً, Scientific Committee
composition, similarly 3 versions). The other 9 legal clauses are اصلية.

DOCUMENTED SOURCE ANOMALY: item 13's prose "goals and tasks" overview
states the Center's objective using the ORIGINAL pre-1440H-amendment
wording of item 2 (omitting judges, the general/administrative judiciary
scope, lawyers, and Public Prosecution members that the 1440H amendment
added) — a genuine internal drift between this guide's own decree clauses
and its narrative summary, confirmed identical in both official sources,
preserved verbatim, not reconciled with item 2.

No decorative in-word tatweel was found anywhere in this document (0
characters, no normalization needed). No legal text is altered. Arabic
governs; no translation/paraphrase/interpretation. Read-only over input;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "judicial_training_center", "guide", "official_source",
                   "judicial_training_center_guide_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "judicial_training_center", "guide", "verified")
RECORDS = os.path.join(OUT_VER, "judicial_training_center_guide_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "judicial_training_center_guide_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "judicial_training_center_arabic_legal_llm",
                        "judicial_training_center_guide_legal_llm_001_018.json")

LAW_ID = "sa-judicial-training-center-guide-1435"
LAW_AR = "الدليل التنظيمي لمركز التدريب العدلي"
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
KEY_RE = r"judicial_training_center_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك").split())


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
        narrative = bool(a.get("is_narrative_structural_content"))
        ls = a.get("legal_status_ar")
        text = a["text"]
        rec = {"law_key": "judicial_training_center", "law_component": "guide", "language": "ar",
               "record_layer": "JUDICIAL_TRAINING_CENTER_GUIDE_ARABIC_VERIFIED_TEXT",
               "article_number": n, "is_mukarrar": False,
               "is_narrative_structural_content": narrative,
               "article_key": key,
               "number_label_ar": a["number_label_ar"],
               "section_ar": a.get("section_ar", ""),
               "article_text_verified": text,
               "verification_status": a["status"],
               "legal_status_ar": ls,
               "is_repealed": ls == "ملغاة", "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
               "amendment_history": a.get("history"),
               "pdf_similarity": a.get("pdf_similarity"),
               "official_text_status": STATUS,
               "governing_source_note": ("Arabic governs; official MOJ portal text cross-verified "
                                         "against the official MOJ PDF (5 pages, sha256 recorded). "
                                         "17 of 18 text-bearing items matched the >=0.90 floor "
                                         "outright (mean 0.9982, min 0.9888); item 12 (the org "
                                         "chart) was visually adjudicated, not text-similarity-"
                                         "scorable against a rendered table."),
               "translation_performed": False, "legal_interpretation_performed": False,
               "summarized_or_paraphrased": False, "english_used_for_correction": False}
        if narrative:
            rec["content_class_note"] = ("This record is organizational-structure/job-description "
                                         "content (org chart, goals/tasks overview, or a "
                                         "departmental job-description block), NOT a numbered legal "
                                         "مادة/بند article — the portal's own data model has no "
                                         "'sequence'/ordinal field and no change-tracking "
                                         "(get-Section-Changes returns 404) for this entry. "
                                         "number_label_ar is the entry's own source heading, not a "
                                         "fabricated ordinal.")
        ver.append(rec)
        llm.append({"law_id": LAW_ID, "law_component": "guide", "article_number": n,
                    "is_mukarrar": False, "is_narrative_structural_content": narrative,
                    "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "record_id": "judicial-training-center-guide-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "judicial_training_center/guide/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "مركز التدريب العدلي %s" % a["number_label_ar"]],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": "Ministry of Justice (MOJ) — official legal portal",
                                     "source_authority_ar": "وزارة العدل — المنصة القانونية الرسمية",
                                     "source_status": "moj_portal_api_cross_checked_official_pdf",
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "judicial_training_center", "layer": "JUDICIAL_TRAINING_CENTER_GUIDE_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "visually_adjudicated": src["stats"]["visually_adjudicated"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-judicial-training-center-guide-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "guide",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (18 سجلاً؛ 11 بنداً قانونياً + 7 سجلات تنظيمية وصفية)",
               "title_en": "Organizational Guide for the Judicial Training Center — Arabic LLM-ready layer (18 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 18], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Judicial Training Center Guide records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
