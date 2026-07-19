#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Travel Documents Law track (نظام وثائق السفر,
Royal Decree M/24, 28/5/1421H / 2000G).

VERIFICATION TIER -- see sources/travel_documents/law/official_source/
travel_documents_law_official_source.json's verification_methodology_note for
the full account. Summary (be conservative -- this is an honest TIER_2 overall
assessment, NOT inflated to TIER_1):

PRIMARY SOURCE: laws.boe.gov.sa, fetched via THREE Wayback Machine snapshots
spanning 13 Nov 2019 - 12 Dec 2025 (live BOE portal unreachable this pass:
TLS connection failure via direct curl, HTTP 503 via WebFetch). All 15
numbered "article_item" divs are present and byte-identical across all three
snapshots; the one added article (10 مكرر) is absent in the 2019 snapshot and
present, byte-identical, in the 2022 and 2025 snapshots -- its appearance
timing exactly matches its real decree date (M/11, 1443H). This internally
consistent, temporally-progressive pattern (also observed for the M/11
changelog popups on Articles 10/11, and the second M/71 popup on Article 12)
gives high confidence in BOE's own text fidelity.

SECOND SOURCES (private aggregators, NOT official/primary): nezams.com
independently reproduces every article's full text and all amendment
notations verbatim, and additionally supplies a decree citation (Council of
Ministers Resolution 217, 29/4/1439H) that BOE's OWN changelog popup for
Article 6 omits entirely. qistas.com independently corroborates the M/134
decree's specific effect (Articles 2, 4 amended, Article 3 repealed).

GENUINELY OFFICIAL SECOND SOURCE (for the M/11 amendment only): the official
Umm Al-Qura Gazette (uqn.gov.sa) directly confirms, in detail, the Royal
Decree M/11 (18/1/1443H) amendments to Articles 10, 10-mukarrar, and 11 --
this is a real second official/primary source (a separate government organ
from BOE), not a BOE mirror.

HONEST TIER CALL: because a genuinely official second source was located
only for the M/11-derived provisions (Articles 10, 10 مكرر, 11), while the
base law and its other four amending instruments (M/134, CoM 217/1439H,
M/48, M/71) rest on BOE (primary, via Wayback) plus private-aggregator
cross-checks only, this track's overall self-assessed tier is TIER_2 ("1
official/primary source + secondary cross-check"), NOT TIER_1, even though
the Articles-10/10bis/11 provisions specifically reach TIER_1-caliber
confidence on their own. Do not inflate the whole-track tier past what the
weakest-verified provisions support.

16 records: 8 اصلية, 6 معدلة (Articles 2, 4, 6, 10, 11, 12), 1 ملغاة
(Article 3), 1 مضافة (Article 10 مكرر). Flat structure, no أبواب/فصول. No
inline per-article titles in the BOE source (bare spelled-ordinal "المادة
الأولى" style headings) -- no title_ar field is used.

PREDECESSOR: Article 13 states this law and its Implementing Regulation
supersede the travel-document-related provisions (a SCOPED/PARTIAL
supersession, not a blanket repeal of the whole prior instrument) of the
prior "نظام الجوازات السفرية" (Passports System, Supreme Order 17/3/2 dated
19/1/1358H) -- not present anywhere in this corpus; recorded as historical
context only, not ingested (one-law-per-pass rule).

COMPANION INSTRUMENTS NOT INGESTED: (1) اللائحة التنفيذية لنظام وثائق السفر
(this law's own Implementing Regulation, indexed by qanoonsa.com/qanoniah.com)
and (2) نظام جوازات السفر السياسية والخاصة (a wholly separate, differently
decreed law governing diplomatic/special passports, referenced but not
superseded by Article 1 of this law) -- neither ingested this pass.

Two genuine BOE-source anomalies preserved verbatim, not silently fixed: (a)
Article 6's own changelog popup cites no decree number/date at all (unlike
every other amended article here); (b) Article 10's changelog "before"-quote
text does not character-for-character match BOE's own main-body wording
("لا تزيد عن" vs "لا تزيد على"; "بهما معا" vs "بمها معاً") -- a minor
same-source internal mismatch that did not block clean incorporation because
the substitution's location is contextually unambiguous.

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
SRC = os.path.join(ROOT, "sources", "travel_documents", "law", "official_source",
                   "travel_documents_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "travel_documents", "law", "verified")
RECORDS = os.path.join(OUT_VER, "travel_documents_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "travel_documents_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "travel_documents_arabic_legal_llm",
                        "travel_documents_law_legal_llm_001_016.json")

LAW_ID = "sa-travel-documents-law-m24-1421"
LAW_AR = "نظام وثائق السفر"

STATUS_UNCHANGED = ("BOE_WAYBACK_THREE_TIMEPOINT_NOV2019_DEC2022_DEC2025_TEXT_STABLE_X_"
                    "NEZAMS_COM_QISTAS_COM_CROSSCHECK_LIVE_BOE_UNREACHABLE")
STATUS_M134_FULLTEXT = ("BOE_CHANGELOG_FULLTEXT_REPLACEMENT_M134_1440H_CLEAN_INCORPORATED_X_"
                        "NEZAMS_COM_QISTAS_COM_CROSSCHECK_LIVE_BOE_UNREACHABLE")
STATUS_M134_REPEALED = ("BOE_CHANGELOG_REPEALED_M134_1440H_TEXT_PRESERVED_X_"
                        "NEZAMS_COM_QISTAS_COM_CROSSCHECK_LIVE_BOE_UNREACHABLE")
STATUS_ART6_CM217 = ("BOE_CHANGELOG_PARA2_PHRASE_INSERTION_CLEAN_X_NEZAMS_COM_SUPPLIES_CM217_1439H_"
                    "DECREE_CITATION_BOE_CHANGELOG_ITSELF_OMITS_DECREE_NUMBER_LIVE_BOE_UNREACHABLE")
STATUS_ART10_M11 = ("BOE_CHANGELOG_PHRASE_SUBSTITUTION_M11_1443H_CLEAN_X_UQN_GOV_SA_OFFICIAL_"
                    "GAZETTE_CROSSCHECK_LIVE_BOE_UNREACHABLE")
STATUS_ART10BIS_M11 = ("BOE_CHANGELOG_NEW_ARTICLE_ADDED_M11_1443H_X_UQN_GOV_SA_OFFICIAL_GAZETTE_"
                       "CROSSCHECK_LIVE_BOE_UNREACHABLE")
STATUS_ART11_M11 = ("BOE_CHANGELOG_PARA3_FULLTEXT_REPLACEMENT_M11_1443H_CLEAN_X_UQN_GOV_SA_"
                    "OFFICIAL_GAZETTE_CROSSCHECK_LIVE_BOE_UNREACHABLE")
STATUS_ART12_TWOSTEP = ("BOE_CHANGELOG_TWO_STEP_M48_1437H_FULLTEXT_PLUS_M71_1444H_PARAGRAPH_"
                        "ADDITION_CLEAN_INCORPORATED_X_NEZAMS_COM_QISTAS_COM_CROSSCHECK_"
                        "LIVE_BOE_UNREACHABLE")

KEY_RE = r"travel_documents_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = {"travel_documents_art_%03d" % n for n in (2, 4, 6, 10, 11, 12)}
ADDED_KEYS = {"travel_documents_art_010_mukarrar"}
REPEALED_KEYS = {"travel_documents_art_003"}
MUKARRAR_KEYS = {"travel_documents_art_010_mukarrar"}

STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك النظام التنفيذية").split())


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
    if key == "travel_documents_art_010_mukarrar":
        return STATUS_ART10BIS_M11
    if key == "travel_documents_art_010":
        return STATUS_ART10_M11
    if key == "travel_documents_art_011":
        return STATUS_ART11_M11
    if key == "travel_documents_art_012":
        return STATUS_ART12_TWOSTEP
    if key == "travel_documents_art_006":
        return STATUS_ART6_CM217
    if key == "travel_documents_art_003":
        return STATUS_M134_REPEALED
    if key in ("travel_documents_art_002", "travel_documents_art_004"):
        return STATUS_M134_FULLTEXT
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
        ver.append({"law_key": "travel_documents", "law_component": "law",
                    "language": "ar",
                    "record_layer": "TRAVEL_DOCUMENTS_LAW_ARABIC_VERIFIED_TEXT",
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
                                              "archived snapshots spanning 13 Nov 2019 - 12 Dec "
                                              "2025 as the PRIMARY source (live BOE unreachable "
                                              "this pass, TLS connection failure/HTTP 503), "
                                              "cross-verified against nezams.com and qistas.com's "
                                              "independent reproductions, and, for the M/11 "
                                              "(1443H) amendment specifically, against the "
                                              "official Umm Al-Qura Gazette (uqn.gov.sa). 6 of 15 "
                                              "numbered articles are معدلة and 1 is ملغاة: BOE's "
                                              "own main body is stale for these, but each "
                                              "article's own changelog popup supplies a clean, "
                                              "contextually-unambiguous current-text "
                                              "reconstruction -- see verification_methodology_note "
                                              "and known_unresolved_discrepancies in the source "
                                              "artifact (including two genuine BOE-side changelog "
                                              "anomalies: Article 6's missing decree citation and "
                                              "Article 10's before-phrase mismatch) before relying "
                                              "on this track's amended-article text. Overall "
                                              "verification tier is honestly self-assessed as "
                                              "TIER_2 (not inflated to TIER_1), since a genuinely "
                                              "official second source was located only for the "
                                              "M/11-derived provisions."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "travel-documents-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "travel_documents/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام وثائق السفر" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree M/24 (28/5/1421H) — "
                                                          "laws.boe.gov.sa via three Wayback "
                                                          "Machine snapshots (2019-2025), "
                                                          "cross-verified against nezams.com, "
                                                          "qistas.com, and (for the M/11 "
                                                          "amendment) the official Umm Al-Qura "
                                                          "Gazette; live BOE unreachable this "
                                                          "pass"),
                                     "source_authority_ar": "المرسوم الملكي رقم (م/24) وتاريخ 28/5/1421هـ — ثلاث لقطات أرشيفية من بوابة هيئة الخبراء عبر Wayback Machine (2019-2025)، مطابقة مع nezams.com وqistas.com، ومع جريدة أم القرى الرسمية لتعديل م/11",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "travel_documents",
               "layer": "TRAVEL_DOCUMENTS_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-travel-documents-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (16 سجلا؛ 8 أصلية و6 معدلة ومادة ملغاة ومادة مضافة)",
               "title_en": ("Saudi Travel Documents Law — Arabic LLM-ready layer (16 records: "
                            "8 original, 6 amended, 1 repealed, 1 added)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 15], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Travel Documents Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
