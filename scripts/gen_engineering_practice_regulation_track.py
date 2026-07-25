#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Law of Practicing Engineering
Professions track (اللائحة التنفيذية لنظام مزاولة المهن الهندسية).

This is a companion-regulation track, entirely separate from this corpus's
already-ingested engineering_practice_law track (sources/engineering_practice,
the base Law itself, Royal Decree M/36, 19/4/1438H, 17 articles). This new
track (engineering_practice_regulation) documents ONLY the Implementing
Regulation issued under that Law's own Article 16.

CURRENT REGULATION INGESTED (18 articles, ALL اصلية): issued by Decision No.
(4/4400942200) of the Minister of Municipal, Rural Affairs and Housing, dated
26/5/1445H, published in the Official Gazette (Umm al-Qura), issue No. 5013,
dated 16/6/1445H / 29 December 2023G. This Decision is explicitly a full
UPDATE/reissuance (per its own preamble: "بشأن تحديث اللائحة التنفيذية"),
grounded in Supreme Royal Order No. (17103) dated 26/3/1442H (which
transferred supervision of the Saudi Council of Engineers from the Ministry
of Commerce to the Ministry of Municipal, Rural Affairs and Housing), and its
own clause 3 repeals "all prior decisions conflicting with it" (a general,
not specifically-named, repeal reaching the former Implementing Regulation).

FORMER REGULATION NOT INGESTED: Ministerial Decision No. (38315) dated
12/7/1439H (announced 1 April 2018G per an mc.gov.sa press release located by
this task's prior research) was the ORIGINAL Implementing Regulation, issued
by the then Ministry of Commerce and Investment. Its full text/article count
could NOT be independently verified this pass: saudieng.sa and
laws.boe.gov.sa were both unreachable live (connection reset); the Wayback
Machine's CDX/availability API confirmed two 2025 snapshots of
saudieng.sa/Admin/NPSCERules/67.pdf exist (byte-identical digest), but its
content-serving path returned "Blocked by egress policy" for every attempt;
and mc.gov.sa's own press release returned HTTP 503. This is an honest
could-not-confirm for the SUPERSEDED text specifically, not a gap in the
CURRENT text ingested here. See known_unresolved_discrepancies.

VERIFICATION TIER -- see sources/engineering_practice_regulation/law/
official_source/engineering_practice_regulation_official_source.json's
verification_methodology_note for the full account. Summary:

PRIMARY SOURCE: the official Umm al-Qura Gazette portal itself (uqn.gov.sa)
-- two pages fetched directly via curl this pass (HTTP 200 for both, direct
HTML text, not scanned images): uqn.gov.sa/details?p=24293 (the Minister's
issuing Decision, full text including its 4 operative clauses and signature)
and uqn.gov.sa/details?p=24294 (the Regulation's full 18-article text).

SECONDARY SOURCE (cross-verified programmatically, article-by-article):
qanoonsa.com -- two matching pages (/p/501308 for the Decision, /p/501309 for
the Regulation), both fetched directly (HTTP 200). All 18 articles matched
uqn.gov.sa WORD-FOR-WORD after normalizing diacritics/digit-style/whitespace
-- including two genuine source-level anomalies preserved faithfully (see
below), confirming they originate in the official text itself, not in either
fetch/parse pipeline.

NOT TIER_1: both laws.boe.gov.sa and saudieng.sa (the Saudi Council of
Engineers' own site) were unreachable live this pass (connection reset on
direct curl for both; saudieng.sa's PDF also timed out via the r.jina.ai
reader-proxy). The Wayback Machine's CDX/availability API (reachable over
https) confirmed two 2025 snapshots of saudieng.sa's PDF exist with an
identical digest, but its content-serving path was blocked by this session's
egress policy on every attempt (both plain and id_ raw forms) -- exactly the
failure mode this task's own instructions anticipated. IS TIER_2 (one
directly-reachable PRIMARY government source + one independent secondary
source, cross-verified verbatim article-by-article, 18/18 exact matches).

TWO GENUINE SOURCE-LEVEL ANOMALIES PRESERVED, NOT FABRICATED: (1) Article 4
lists three accreditation categories with alphabetic labels "أ-" and "ب-",
then lists the third category ("الفني") with NO "ج-" label at all -- an
omission byte-identical across both independently-fetched sources. (2)
Article 7 enumerates six permitted engineering-work domains but its item
numbering jumps directly from "2-" to "4-", with no item "3-" anywhere in
either source. Neither gap is patched or renumbered; both are preserved
exactly as published and flagged explicitly.

18 records: ALL اصلية (0 معدلة, 0 ملغاة, 0 مضافة) -- a fresh full
reissuance, not a partial amendment of specific articles. Flat structure, NO
أبواب/فصول (matching the base Law's own flat structure). No inline
per-article titles in either source -- no title_ar key is used.

Diacritics (tashkeel) are stripped uniformly (harakat range U+064B-U+0652),
consistent with this corpus's disability_rights_regulation precedent for the
same uqn.gov.sa source portal. The one incidental double-space artifact in
Article 1 ("مأمور  الضبط") is collapsed to a single space (a pure HTML-
formatting artifact, no semantic content). Single spaces around date slashes
(e.g. "19 /4/ 1438هـ") are an authentic, consistent source-typography
convention and are NOT altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "engineering_practice_regulation", "law", "official_source",
                   "engineering_practice_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "engineering_practice_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "engineering_practice_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "engineering_practice_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "engineering_practice_regulation_arabic_legal_llm",
                        "engineering_practice_regulation_legal_llm_001_018.json")

LAW_ID = "sa-engineering-practice-regulation-4400942200-1445"
LAW_AR = "اللائحة التنفيذية لنظام مزاولة المهن الهندسية"
STATUS_UNCHANGED = ("UQN_GOV_SA_OFFICIAL_GAZETTE_DIRECT_HTML_HTTP200_X_QANOONSA_COM_"
                    "INDEPENDENT_SECONDARY_WORDFORWORD_MATCH_ALL_18_ARTICLES_X_"
                    "LAWS_BOE_GOV_SA_AND_SAUDIENG_SA_LIVE_UNREACHABLE_WAYBACK_"
                    "CONTENT_PATH_BLOCKED_CDX_ONLY")
KEY_RE = r"engineering_practice_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك الهيئة المجلس الوزارة الوزير").split())


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
    return STATUS_UNCHANGED


GOV_NOTE = ("Arabic governs; PRIMARY source is the official Umm al-Qura Gazette portal "
            "(uqn.gov.sa) itself -- both the Regulation's own page (details?p=24294) and its "
            "issuing Decision's page (details?p=24293) carry full text as direct HTML, not "
            "scanned images, fetched directly (HTTP 200). Cross-checked verbatim "
            "article-by-article against qanoonsa.com (an independent secondary aggregator) -> "
            "18/18 exact matches -> TIER_2. 18 articles, no أبواب/فصول; ALL اصلية (fresh full "
            "reissuance, 26/5/1445H / 16/6/1445H publication). laws.boe.gov.sa and saudieng.sa "
            "(the Saudi Council of Engineers' own site) were both unreachable live this pass "
            "(connection reset); the Wayback Machine's CDX/availability API confirmed a stable "
            "saudieng.sa PDF snapshot exists but its content-serving path was blocked by this "
            "session's egress policy. See verification_methodology_note and "
            "known_unresolved_discrepancies in the source artifact before relying on this "
            "track's text or provenance -- including for the SUPERSEDED former Regulation "
            "(Decision 38315, 1439H), which is NOT ingested here.")

SRC_AUTH = ("Decision No. (4/4400942200) of the Minister of Municipal, Rural Affairs and "
            "Housing (26/5/1445H), issued under Article 16 of the base Law (Royal Decree M/36, "
            "19/4/1438H) and Supreme Royal Order No. (17103, 26/3/1442H). Full text from "
            "uqn.gov.sa (official Umm al-Qura Gazette portal, primary) cross-checked verbatim "
            "against qanoonsa.com (independent secondary source) -> TIER_2. Published Umm "
            "al-Qura issue 5013, 16/6/1445H / 29 Dec 2023G.")

SRC_AUTH_AR = ("قرار وزير الشؤون البلدية والقروية والإسكان رقم (4/4400942200) وتاريخ 26/5/1445هـ، "
               "صادر استنادا إلى المادة (16) من النظام الأم (المرسوم الملكي م/36، 19/4/1438هـ) "
               "والأمر السامي الكريم رقم (17103) وتاريخ 26/3/1442هـ. النص الكامل من uqn.gov.sa "
               "(بوابة جريدة أم القرى الرسمية، مصدر أساسي) متقاطع حرفيا مع qanoonsa.com (مصدر "
               "ثانوي مستقل) -- TIER_2. منشورة في عدد جريدة أم القرى رقم (5013) بتاريخ 16/6/1445هـ "
               "الموافق 29 ديسمبر 2023م.")


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
        ver.append({"law_key": "engineering_practice_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "ENGINEERING_PRACTICE_REGULATION_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": GOV_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "engineering-practice-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "engineering_practice_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام مزاولة المهن الهندسية"
                                          % a["number_label_ar"]],
                    "text_status": a["status"],
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
    json.dump({"law_key": "engineering_practice_regulation",
               "layer": "ENGINEERING_PRACTICE_REGULATION_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-engineering-practice-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (18 مادة، كلها أصلية)",
               "title_en": ("Implementing Regulation of the Law of Practicing Engineering "
                            "Professions — Arabic LLM-ready layer (18 records, all original)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 18], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Engineering Practice Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
