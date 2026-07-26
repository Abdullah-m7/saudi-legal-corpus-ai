#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Statute of the Technical and Vocational Training Corporation
track (تنظيم المؤسسة العامة للتدريب التقني والمهني, Council of Ministers
Resolution No. 268, 14/8/1428H, amended -- among others -- by Council of
Ministers Resolution No. 632, 26/8/1446H).

VERIFICATION TIER -- see sources/tvtc_organizational_statute/law/
official_source/tvtc_organizational_statute_official_source.json's
verification_methodology_note for the full account. Summary:

PRIMARY SOURCE: laws.boe.gov.sa, fetched via THREE Wayback Machine snapshots
spanning 16 Jan 2020 - 7 May 2025 (live BOE unreachable this pass). All 13
'article_item' divs are present in every snapshot, in the same order. Only
Article 4 ever carries BOE's own 'changed-article' class with a 'تعديلات
المادة' changelog popup; the other 12 articles are byte-for-byte identical
(SHA-256 verified) across all three time-points. Cross-checked against
nezams.com (an independent legal aggregator whose own structured summary
matches BOE's decree number/date, 13-article count, and Article 4's three
amendments exactly) and against TVTC's own official website
(tvtc.gov.sa/ar/About/Pages/TVTCRegulation.aspx, via a Wayback snapshot),
which corroborates the decree number/date but hosts only a summary, not full
article text.

TWO ARTICLES WITH CONFIRMED AMENDMENTS, DIFFERENT TREATMENT:
  - Article 4 (board composition): THREE layered, chronologically ordered
    amendments (Council of Ministers Resolutions 469/1438H, 693/1441H,
    745/1442H) -- but unlike this corpus's saudi_engineers_law Article 6
    precedent, entries 2 and 3 are bare 'add a seat' instructions with no
    stated lettered position, not complete replacement texts, and cannot
    safely be merged into one reconstructed 'current' text without this
    track inventing letter assignments. Following this corpus's awqaf_law
    precedent for exactly this not-safely-mergeable pattern, this track
    ingests BOE's own STALE main-body text (the original 1428H wording) and
    records all three amendments verbatim in history WITHOUT merging them.
  - Article 7 (Governor): a SINGLE amendment (Council of Ministers
    Resolution 632, 26/8/1446H / 25 Feb 2025G, Umm Al-Qura issue 5074)
    touching ONLY the صدر (opening clause) -- confirmed via a clean, complete
    quoted replacement independently reproduced by qanoonsa.com (direct
    fetch) and a separate WebSearch aggregation, but NOT YET reflected in any
    of the three independently-checked BOE snapshots (neither main body nor
    changelog), a materially thinner verification tier than a BOE-changelog-
    confirmed amendment -- honestly flagged in known_unresolved_discrepancies.

13 records: 11 اصلية, 2 معدلة (Articles 4, 7), 0 ملغاة, 0 مضافة. Flat
structure, no أبواب/فصول. No inline per-article titles in the BOE source --
no title_ar field is used. Article 12 names a CONFIRMED predecessor (نظام
المؤسسة العامة للتعليم الفني والتدريب المهني, Royal Decree M/30, 10/8/1400H),
a positive finding not ingested this pass (one-instrument-per-pass
precedent).

No legal text is altered beyond whitespace normalization (fixing one
incidental missing space in Article 4's original sub-paragraph 1/و, a BOE
table-rendering artifact) and, for Article 7 only, splicing Resolution 632's
own quoted صدر substitution onto the article's otherwise-unchanged,
independently-verified-stable remainder. Arabic governs; no translation/
paraphrase/interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "tvtc_organizational_statute", "law", "official_source",
                   "tvtc_organizational_statute_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "tvtc_organizational_statute", "law", "verified")
RECORDS = os.path.join(OUT_VER, "tvtc_organizational_statute_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "tvtc_organizational_statute_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "tvtc_organizational_statute_arabic_legal_llm",
                        "tvtc_organizational_statute_legal_llm_001_013.json")

LAW_ID = "sa-tvtc-organizational-statute-268-1428"
LAW_AR = "تنظيم المؤسسة العامة للتدريب التقني والمهني"
TOP_STATUS = ("MIXED_TIER_SEE_PER_ARTICLE_STATUS_BOE_WAYBACK_THREE_TIMEPOINT_JAN2020_DEC2022_"
              "MAY2025_PRIMARY_X_TVTC_OFFICIAL_SITE_CITATION_ONLY_X_NEZAMS_QANOONSA_WEBSEARCH_"
              "CROSSCHECK_LIVE_BOE_AND_LIVE_TVTC_UNREACHABLE")
KEY_RE = r"tvtc_organizational_statute_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = {"tvtc_organizational_statute_art_004", "tvtc_organizational_statute_art_007"}
ADDED_KEYS = set()
REPEALED_KEYS = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام التنظيم اللائحة أحكام يجب يجوز "
            "عليه دون فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك المؤسسة المجلس الرئيس "
            "بوجه خاص").split())


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
        ver.append({"law_key": "tvtc_organizational_statute", "law_component": "law",
                    "language": "ar",
                    "record_layer": "TVTC_ORGANIZATIONAL_STATUTE_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; this track rests on THREE "
                                              "independently-fetched BOE-via-Wayback-Machine "
                                              "archived snapshots spanning 16 Jan 2020 - 7 May "
                                              "2025 as the PRIMARY source (live BOE unreachable "
                                              "this pass), cross-verified against nezams.com (an "
                                              "independent legal aggregator matching BOE's decree "
                                              "number/date, article count, and Article 4's three "
                                              "amendments exactly) and TVTC's own official website "
                                              "(tvtc.gov.sa, decree citation only, no full text). "
                                              "Article 4 is معدلة: THREE layered amendments "
                                              "(Resolutions 469, 693, 745) exist per BOE's own "
                                              "changelog, but entries 2-3 are bare 'add a seat' "
                                              "instructions with no stated lettered position and "
                                              "cannot safely be merged -- this record carries "
                                              "BOE's own STALE main-body text (pre-469) with all "
                                              "three amendments recorded but NOT merged, per this "
                                              "corpus's awqaf_law precedent for not-safely-"
                                              "mergeable layered amendments. Article 7 is also "
                                              "معدلة: a single clean substitution of its صدر "
                                              "(opening clause) only, per Council of Ministers "
                                              "Resolution 632 (26/8/1446H) -- confirmed via "
                                              "qanoonsa.com's direct fetch and an independent "
                                              "WebSearch aggregation, but NOT YET reflected in any "
                                              "of the three checked BOE snapshots (a materially "
                                              "thinner verification tier than a BOE-changelog-"
                                              "confirmed amendment). See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track's text as "
                                              "necessarily reflecting BOE's own live rendering, "
                                              "especially for Articles 4 and 7."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "tvtc-organizational-statute-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "tvtc_organizational_statute/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من تنظيم المؤسسة العامة للتدريب التقني والمهني" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Council of Ministers Resolution No. "
                                                          "(268), 14/8/1428H — laws.boe.gov.sa via "
                                                          "three Wayback Machine snapshots "
                                                          "(2020-2025), cross-verified against "
                                                          "nezams.com and TVTC's own official "
                                                          "website (tvtc.gov.sa); live BOE "
                                                          "unreachable this pass"),
                                     "source_authority_ar": "قرار مجلس الوزراء رقم (268) وتاريخ 14/8/1428هـ — ثلاث لقطات أرشيفية من بوابة هيئة الخبراء عبر Wayback Machine (2020-2025)، مطابقة مع nezams.com والموقع الرسمي للمؤسسة (tvtc.gov.sa)",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "tvtc_organizational_statute",
               "layer": "TVTC_ORGANIZATIONAL_STATUTE_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-tvtc-organizational-statute-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (13 مادة؛ 11 أصلية و2 معدلة)",
               "title_en": "Statute of the Technical and Vocational Training Corporation — Arabic LLM-ready layer (13 records: 11 original, 2 amended)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 13], "text_status": TOP_STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready TVTC Organizational Statute records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
