#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Nationality Law track (نظام الجنسية العربية
السعودية, Royal Will 8/20/5604, 22/2/1374H / 1954G).

VERIFICATION TIER -- see sources/nationality/law/official_source/
nationality_law_official_source.json's verification_methodology_note for the
full account. Summary:

PRIMARY SOURCE: laws.boe.gov.sa, fetched via THREE Wayback Machine snapshots
spanning 19 Nov 2019 - 14 Jan 2026 (live BOE portal unreachable this pass,
connection reset via both direct curl and the WebFetch tool). All 30
"article_item" divs are present in every snapshot, in the same order, no
أبواب/فصول grouping. All 30 articles' main-body text is byte-identical across
all three time-points with exactly two exceptions: a confirmed clerical typo
fix in Article 30 ("المعول"->"المفعول", no decree cited), and Article 8
gaining a second changelog popup (its M/88, 1444H amendment) between the Dec
2022 and Jan 2026 snapshots -- consistent with that amendment's real-world
Jan-Mar 2023G announcement/publication date.

SECOND SOURCE: nezams.com, an independent Arabic legal-reference aggregator,
independently reproduces this law's decree identity/preamble and the SAME
amendment notations (decree numbers, hijri dates) for Articles 7, 8, and 9
found in BOE's own changelog popups. THIRD-SOURCE cross-check for the most
recent Article 8 amendment (M/88, 1444H / ~Jan 2023G): independently
corroborated by multiple English-language news outlets (Arab News, Amwaj
Media, Middle East Monitor, Investment Migration Council).

AMENDMENT INCORPORATION -- a CLEAN case unlike this corpus's
engineering_practice_law/awqaf_law precedent: BOE's own main body for 11 of
30 articles (7, 8, 9, 12, 14, 16, 17, 21, 22, 26, 27) is stale (pre-amendment)
text, but every one of these 11 articles' changelog popups supplies either a
complete, self-contained replacement text, or (Article 8's second popup only)
an unambiguous single-occurrence phrase substitution cleanly applied to its
own first popup's already-established text. Per this corpus's press_law/
accounting_auditing_law clean-incorporation precedent, this track ingests
each of these 11 articles' fully-reconstructed CURRENT text (legal_status_ar
= معدلة), not BOE's stale main body, and records the full amendment chain in
each article's history[].

30 records: 19 اصلية, 11 معدلة (Articles 7, 8, 9, 12, 14, 16, 17, 21, 22, 26,
27), 0 ملغاة, 0 مضافة. Flat structure, no أبواب/فصول. No inline per-article
titles in the BOE source (bare numeric "المادة رقم (N)" labels) -- no
title_ar field is used.

PREDECESSOR: Article 28 explicitly repeals a named predecessor (the prior
Saudi Arabian Nationality System, Royal Will 7/1/47 dated 13 Shawwal 1357H,
and the separate Hejazi/Hejazi-Najdi nationality regulations) -- none of
these exists anywhere in this corpus; recorded as historical context only,
not ingested (one-law-per-pass rule).

COMPANION INSTRUMENT NOT INGESTED: اللائحة التنفيذية لنظام الجنسية العربية
السعودية (this law's own Implementing Regulation, ~25 articles per this
corpus's prior coverage-gap-map pass, hosted on moi.gov.sa) was identified
but NOT ingested this pass (one-law-per-pass precedent) -- see
known_unresolved_discrepancies.

No legal text is altered beyond whitespace normalization and the clean
changelog-incorporation described above. Arabic governs; no translation/
paraphrase/interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "nationality", "law", "official_source",
                   "nationality_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "nationality", "law", "verified")
RECORDS = os.path.join(OUT_VER, "nationality_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "nationality_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "nationality_arabic_legal_llm",
                        "nationality_law_legal_llm_001_030.json")

LAW_ID = "sa-nationality-law-8-20-5604-1374"
LAW_AR = "نظام الجنسية العربية السعودية"
STATUS_UNCHANGED = ("BOE_WAYBACK_THREE_TIMEPOINT_NOV2019_DEC2022_JAN2026_TEXT_STABLE_X_"
                    "NEZAMS_COM_CROSSCHECK_LIVE_BOE_UNREACHABLE")
STATUS_AMENDED_CLEAN = ("BOE_CHANGELOG_FULLTEXT_REPLACEMENT_CLEAN_INCORPORATED_X_"
                        "NEZAMS_COM_CROSSCHECK_LIVE_BOE_UNREACHABLE")
STATUS_ART8 = ("BOE_CHANGELOG_TWO_STEP_M14_1405H_FULLTEXT_PLUS_M88_1444H_CLEAN_"
              "SUBSTITUTION_INCORPORATED_X_NEWS_CROSSCHECK_JAN2023_MOTHER_"
              "TRANSMISSION_AMENDMENT_LIVE_BOE_UNREACHABLE")
STATUS_ART30 = ("BOE_WAYBACK_THREE_TIMEPOINT_TEXT_STABLE_EXCEPT_2019_TYPO_VARIANT_"
               "CONFIRMED_CLERICAL_NOT_A_DECREE_AMENDMENT_LIVE_BOE_UNREACHABLE")
KEY_RE = r"nationality_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = {"nationality_art_%03d" % n for n in (7, 8, 9, 12, 14, 16, 17, 21, 22, 26, 27)}
ADDED_KEYS = set()
REPEALED_KEYS = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك الجنسية العربية السعودية سعودي "
            "سعودية الوزارة الوزير").split())


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


def _top_status(key):
    if key == "nationality_art_008":
        return STATUS_ART8
    if key in AMENDED_KEYS:
        return STATUS_AMENDED_CLEAN
    if key == "nationality_art_030":
        return STATUS_ART30
    return STATUS_UNCHANGED


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
        top_status = _top_status(key)
        ver.append({"law_key": "nationality", "law_component": "law",
                    "language": "ar",
                    "record_layer": "NATIONALITY_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": top_status,
                    "governing_source_note": ("Arabic governs; this track rests on THREE "
                                              "independently-fetched BOE-via-Wayback-Machine "
                                              "archived snapshots spanning 19 Nov 2019 - 14 Jan "
                                              "2026 as the PRIMARY source (live BOE unreachable "
                                              "this pass, connection reset), cross-verified "
                                              "against nezams.com's independent reproduction of "
                                              "the decree identity and amendment notations, and, "
                                              "for the most recent amendment (Article 8, M/88, "
                                              "1444H), against multiple independent English-"
                                              "language news outlets reporting the same change "
                                              "in Jan-Mar 2023G. 11 of 30 articles are معدلة: "
                                              "BOE's own main body is stale for these, but each "
                                              "article's own changelog popup supplies a clean, "
                                              "unambiguous current-text reconstruction (unlike "
                                              "this corpus's engineering_practice_law Article 1 "
                                              "precedent) -- see verification_methodology_note "
                                              "and known_unresolved_discrepancies in the source "
                                              "artifact for the full account before relying on "
                                              "this track's amended-article text."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "nationality-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "nationality/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام الجنسية العربية السعودية" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Will 8/20/5604 (22/2/1374H) — "
                                                          "laws.boe.gov.sa via three Wayback "
                                                          "Machine snapshots (2019-2026), "
                                                          "cross-verified against nezams.com "
                                                          "and, for the most recent amendment, "
                                                          "independent news coverage; live BOE "
                                                          "unreachable this pass"),
                                     "source_authority_ar": "الإرادة الملكية السنية رقم (8/20/5604) وتاريخ 22/2/1374هـ — ثلاث لقطات أرشيفية من بوابة هيئة الخبراء عبر Wayback Machine (2019-2026)، مطابقة مع nezams.com",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "nationality",
               "layer": "NATIONALITY_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-nationality-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (30 مادة؛ 19 أصلية و11 معدلة)",
               "title_en": "Saudi Arabian Nationality Law — Arabic LLM-ready layer (30 records: 19 original, 11 amended)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 30], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Nationality Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
