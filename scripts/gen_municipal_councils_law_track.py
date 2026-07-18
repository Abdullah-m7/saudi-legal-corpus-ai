#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Municipal Councils Law track
(نظام المجالس البلدية, Royal Decree M/61, 4/10/1435H).

VERIFICATION TIER -- see sources/municipal_councils/law/official_source/
municipal_councils_law_official_source.json's verification_methodology_note
for the full account. Summary:

TIER_1: two genuinely separate official/primary sources agree --
  (1) laws.boe.gov.sa, fetched via SIX Wayback Machine snapshots spanning
      22 Nov 2019 - 12 Dec 2025 because the live BOE portal was unreachable
      this pass (HTTP 503). All 69 'article_item' divs are present in every
      snapshot, in the same order, all carrying ONLY the 'no_alternate' CSS
      class (never 'changed-article') -- i.e. BOE's own page records ZERO
      amendments to this law across the entire six-year window, confirmed
      by a full word-for-word diff (zero differences) between the earliest
      and latest snapshots.
  (2) momah.gov.sa -- the Ministry of Municipal, Rural Affairs and Housing's
      OWN official website, hosting two independently-dated official PDF
      copies of this exact law's full text (uploaded Feb 2022 and Oct 2025),
      both reproducing the identical 69-article/12-فصل structure and
      content, and both including an embedded scan of the original signed
      Royal Decree (read via direct visual inspection of the rendered page
      image, not OCR).
  Independently corroborated by nezams.com (decree number/dates, 69
  articles, explicit 'لم يجرِ عليه تعديل' -- no amendment made).

69 records, ALL 69 اصلية (original) -- this law has NEVER been amended per
all sources checked. 0 معدلة, 0 ملغاة, 0 مضافة. Structured into 12 فصول
(chapters), NO أبواب (parts) above them.

REPEAL / PREDECESSOR: this law's own Article 68 PARTIALLY repeals four
specifically-named provisions (Articles 2(b), 2(c), 7(b), and Chapter Two
of Part Two) of the Law of Municipalities and Villages (نظام البلديات
والقرى, Royal Decree M/5, 21/2/1397H) -- NOT a full supersession. That
predecessor law is not ingested in this corpus and its text is not
independently fetched here (historical/cross-reference context only).

No legal text is altered beyond whitespace/line-break normalization and
selective removal of decorative Arabic tatweel/kashida characters (U+0640)
that appeared mid-word in a handful of BOE's own rendered spans (e.g.
'ريـال', 'الصـادر') -- the legitimate ه+tatweel 'هـ' Hijri-era abbreviation
marker is always preserved. Arabic governs; no translation/paraphrase/
interpretation performed. Read-only over input; deterministic over
outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "municipal_councils", "law", "official_source",
                   "municipal_councils_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "municipal_councils", "law", "verified")
RECORDS = os.path.join(OUT_VER, "municipal_councils_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "municipal_councils_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "municipal_councils_arabic_legal_llm",
                        "municipal_councils_law_legal_llm_001_069.json")

LAW_ID = "sa-municipal-councils-law-m61-1435"
LAW_AR = "نظام المجالس البلدية"
TOP_STATUS = ("TIER_1_BOE_WAYBACK_SIX_TIMEPOINT_2019_2025_ZERO_AMENDMENTS_X_"
              "MOMAH_GOV_SA_OFFICIAL_TWO_DATED_PDFS_X_NEZAMS_CROSSCHECK_"
              "LIVE_BOE_UNREACHABLE")
KEY_RE = r"municipal_councils_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = set()
ADDED_KEYS = set()
REPEALED_KEYS = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك المجلس الوزير الوزارة البلدية").split())


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
        ver.append({"law_key": "municipal_councils", "law_component": "law",
                    "language": "ar",
                    "record_layer": "MUNICIPAL_COUNCILS_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": TOP_STATUS,
                    "governing_source_note": ("Arabic governs; this track rests on SIX "
                                              "independently-fetched BOE-via-Wayback-Machine "
                                              "archived snapshots spanning 22 Nov 2019 - 12 Dec "
                                              "2025 (all showing ZERO amendments to any of the "
                                              "69 articles), cross-verified against TWO "
                                              "independently-dated official PDF copies of this "
                                              "law hosted on momah.gov.sa (the Ministry of "
                                              "Municipal, Rural Affairs and Housing's own site, "
                                              "a genuinely separate primary source from BOE) "
                                              "and against nezams.com's independent statement "
                                              "that no amendment has been made to this law. "
                                              "Live BOE was unreachable this pass (HTTP 503). "
                                              "See known_unresolved_discrepancies in the source "
                                              "artifact for a documented, immaterial chapter-10 "
                                              "heading spelling anomaly carried verbatim from "
                                              "both primary sources, and for the confirmed, "
                                              "narrow partial-repeal relationship this law's own "
                                              "Article 68 states against the (not-ingested) Law "
                                              "of Municipalities and Villages (M/5, 1397H)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "municipal-councils-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "municipal_councils/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام المجالس البلدية" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree M/61 — laws.boe.gov.sa "
                                                          "via six Wayback Machine snapshots "
                                                          "(2019-2025, zero amendments found), "
                                                          "cross-verified against momah.gov.sa's "
                                                          "own two independently-dated official "
                                                          "PDFs and nezams.com; live BOE "
                                                          "unreachable this pass"),
                                     "source_authority_ar": "مرسوم ملكي رقم (م/61) — ست لقطات أرشيفية من بوابة هيئة الخبراء عبر Wayback Machine (2019-2025)، مطابقة مع نسختي وزارة الشؤون البلدية والقروية والإسكان الرسميتين (2022 و2025) ومع nezams.com",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "municipal_councils",
               "layer": "MUNICIPAL_COUNCILS_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": TOP_STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-municipal-councils-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (69 مادة، جميعها أصلية)",
               "title_en": "Municipal Councils Law — Arabic LLM-ready layer (69 records, all original)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 69], "text_status": TOP_STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Municipal Councils Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
