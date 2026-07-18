#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Law of the General Authority for Awqaf track
(نظام الهيئة العامة للأوقاف, Royal Decree M/11, 26/2/1437H).

VERIFICATION TIER -- see sources/awqaf/law/official_source/
awqaf_law_official_source.json's verification_methodology_note for the full
account. Summary:

PRIMARY SOURCE: laws.boe.gov.sa, fetched via SIX Wayback Machine snapshots
spanning 21 Nov 2019 - 12 Dec 2025 because the live BOE portal was
unreachable this pass (HTTP 503). All 25 'article_item' divs are present
in every snapshot, in the same order, no أبواب/فصول grouping. Only two
articles (6 and 21) ever carry BOE's own 'changed-article' class plus a
'تعديلات المادة' changelog popup; the other 23 are textually identical
across all six time-points.

TWO ARTICLES WITH CONFIRMED AMENDMENTS, TREATED DIFFERENTLY:
  - Article 21 (fees): a SINGLE, clean, fully-quoted amendment (Royal
    Decree M/72, 1/6/1444H, adding paragraph 2 exempting charitable waqf
    from judicial-costs law) -- BOE's own main body is stale (still shows
    1 paragraph even in snapshots years after the amendment), so this
    track ingests the changelog-popup's quoted amended text, following
    this corpus's accounting_auditing_law precedent for exactly this
    stale-main-body-vs-changelog-popup pattern.
  - Article 6 (board composition): FOUR layered, partial amendments
    (Council of Ministers Resolutions 262/1438H, 618/1442H, 638/1442H,
    651/1443H) whose own quoted "before" phrasing does not match the
    article's actual historically-observed wording at any of the six
    snapshots -- an internal inconsistency implying an unlogged
    intermediate step. This track does NOT hand-reconstruct a guessed
    merged text; it ingests BOE's own stable six-year main-body text,
    marks the article معدلة, records all four amendments in history[],
    and flags the unresolved inconsistency explicitly (see
    known_unresolved_discrepancies, key
    awqaf_article6_boe_main_body_not_reflecting_own_changelog).

25 records: 23 اصلية, 2 معدلة (Articles 6, 21), 0 ملغاة, 0 مضافة. Flat
structure, no أبواب/فصول. No inline per-article titles in the BOE source
-- no title_ar field is used.

PREDECESSOR: this law's own Article 25(1) replaces نظام مجلس الأوقاف
الأعلى (Royal Decree M/35, 18/7/1386H) -- confirmed via this law's own
primary text; the predecessor's own text is not independently fetched or
ingested (historical context only).

No legal text is altered beyond whitespace/line-break normalization (<br>
-> newline; Article 6's HTML <table> of board seats rendered one row per
line, "letter. role — membership-count") and, for Article 21 only,
substituting BOE's own quoted changelog replacement text for its stale
main body. Arabic governs; no translation/paraphrase/interpretation.
Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "awqaf", "law", "official_source",
                   "awqaf_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "awqaf", "law", "verified")
RECORDS = os.path.join(OUT_VER, "awqaf_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "awqaf_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "awqaf_arabic_legal_llm",
                        "awqaf_law_legal_llm_001_025.json")

LAW_ID = "sa-awqaf-law-m11-1437"
LAW_AR = "نظام الهيئة العامة للأوقاف"
TOP_STATUS = ("MIXED_TIER_SEE_PER_ARTICLE_STATUS_BOE_WAYBACK_SIX_TIMEPOINT_PRIMARY_X_"
              "AWQAF_GOV_SA_OFFICIAL_SCAN_X_NEZAMS_X_WEBSEARCH_PRESS_CROSSCHECK_"
              "LIVE_BOE_UNREACHABLE")
KEY_RE = r"awqaf_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = {"awqaf_art_006", "awqaf_art_021"}
ADDED_KEYS = set()
REPEALED_KEYS = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك الهيئة المجلس الرئيس المحافظ").split())


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
        ver.append({"law_key": "awqaf", "law_component": "law",
                    "language": "ar",
                    "record_layer": "AWQAF_LAW_ARABIC_VERIFIED_TEXT",
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
                                              "archived snapshots spanning 21 Nov 2019 - 12 Dec "
                                              "2025 as the PRIMARY source (live BOE unreachable "
                                              "this pass, HTTP 503), cross-verified against a "
                                              "scanned copy of the original Royal Decree hosted "
                                              "on the Authority's own official website "
                                              "(web.awqaf.gov.sa) and against nezams.com. Article "
                                              "21 is معدلة: BOE's own main body text is STALE "
                                              "(pre-M/72); this record instead carries BOE's own "
                                              "changelog-popup wording (quoting Royal Decree M/72, "
                                              "1/6/1444H), independently corroborated by a "
                                              "WebSearch aggregation citing Council of Ministers "
                                              "Resolution 363 and Saudi press coverage. Article 6 "
                                              "is also معدلة (four confirmed amendments per BOE's "
                                              "own changelog) but this record carries BOE's own "
                                              "STABLE six-year main-body text, NOT a "
                                              "hand-reconstructed merge, because the changelog's "
                                              "own four layered amendments are internally "
                                              "inconsistent with the article's observed history -- "
                                              "see verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact (keys "
                                              "awqaf_article6_boe_main_body_not_reflecting_own_changelog "
                                              "and "
                                              "awqaf_article21_changelog_amendment_incorporated_main_body_stale) "
                                              "before relying on this track's text as necessarily "
                                              "reflecting BOE's own live rendering."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "awqaf-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "awqaf/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام الهيئة العامة للأوقاف" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree M/11 — laws.boe.gov.sa "
                                                          "via six Wayback Machine snapshots "
                                                          "(2019-2025), cross-verified against "
                                                          "web.awqaf.gov.sa's own scanned original "
                                                          "decree and nezams.com; live BOE "
                                                          "unreachable this pass"),
                                     "source_authority_ar": "مرسوم ملكي رقم (م/11) — ست لقطات أرشيفية من بوابة هيئة الخبراء عبر Wayback Machine (2019-2025)، مطابقة مع نسخة الهيئة العامة للأوقاف الرسمية الممسوحة ضوئياً ومع nezams.com",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "awqaf",
               "layer": "AWQAF_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-awqaf-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (25 مادة؛ 23 أصلية و2 معدلة)",
               "title_en": "Law of the General Authority for Awqaf — Arabic LLM-ready layer (25 records: 23 original, 2 amended)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 25], "text_status": TOP_STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Awqaf Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
