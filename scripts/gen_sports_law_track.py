#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Sports Law track (نظام الرياضة, Royal Decree M/121,
10/6/1447H / ~1 December 2025G; published Umm al-Qura issue 5129, 21/6/1447H /
12 December 2025G; entry into force 180 days after publication, ~June 2026G).

VERIFICATION TIER -- see sources/sports/law/official_source/
sports_law_official_source.json's verification_methodology_note for the full
account. Summary:

BOTH PRIMARY GOVERNMENT PORTALS UNREACHABLE THIS PASS:
  * laws.boe.gov.sa: HTTP 503 (WebFetch) and TLS connection-reset (direct
    curl through the session's configured proxy, multiple attempts).
  * mos.gov.sa (Ministry of Sport, hosts an official "نظام الرياضة v2025.pdf"):
    TLS connection-reset via WebFetch AND direct curl (default UA and a full
    browser UA), three independent attempts -- consistent with a
    network/WAF-level block of non-browser traffic rather than a transient
    outage.
  web.archive.org was NOT attempted (organization egress-policy block on that
  host for this session, documented across this corpus and never bypassed).

WHAT WAS OBTAINED (TIER_3):
  * uqn.gov.sa (the Umm al-Qura OFFICIAL GAZETTE): its news page for the
    decree (details?p=28705) is a client-rendered Vue app; the underlying
    JSON API endpoint (https://www.uqn.gov.sa/api/article/21263/json) was
    fetched directly (HTTP 200) and returned OFFICIAL metadata -- hijri_date
    1447-6-21, gregorian_date 12-12-2025 -- confirming the gazette publication
    date directly from the government source, plus a verbatim (if truncated,
    ~640 char) excerpt of the royal decree's preamble that matches nezams.com
    word-for-word up to the truncation point. This is official but does NOT
    cover the substantive law articles themselves (only the decree
    announcement/preamble).
  * nezams.com (independent Saudi legal-text aggregator, NOT a BOE mirror):
    fetched directly (HTTP 200) via the site's standard URL-slug convention;
    parsed 97 "subject" elements (subject-1..subject-97) matching the law's
    full article count, with an explicit metadata table (decree M/121,
    10/6/1447H; CoM Resolution 414, 4/6/1447H; publication 21/6/1447H; status
    ساري) and the full preamble (decree text + all 7 numbered clauses of CoM
    Resolution 414) matching the uqn.gov.sa excerpt verbatim.
  * qanoonsa.com (a SEPARATE independent Saudi legal-text site, explicitly
    disclaiming its own non-official status and pointing users back to Umm
    al-Qura for verification): fetched directly (HTTP 200, raw HTML -- NOT
    the AI-paraphrased WebFetch summary, which under-delivers on this page);
    parsed into 97 article segments by their spelled-ordinal Arabic labels.
    Cross-checked programmatically, article-by-article, against the
    nezams.com text (after normalizing Arabic-Indic vs Western digits,
    alef/yaa/taa-marbuta variants, and diacritics): EVERY article's substantive
    body text matched VERBATIM between the two independent sources. The small
    number of raw character-diff mismatches surfaced by the automated
    comparison were manually inspected and are ALL attributable to the next
    chapter's باب/فصل heading being swept into the tail of the prior article
    by the (deliberately simple) qanoonsa parser -- not to any real textual
    discrepancy. qanoonsa's own page footer independently corroborates the
    Umm al-Qura issue number (5129) and Gregorian publication date (12 Dec
    2025) a third time.

Because no OFFICIAL government document could be retrieved as the governing
text for the 97 articles themselves (only the gazette's own preamble excerpt
and metadata could be confirmed officially and directly), this track is
honestly classified TIER_3 (full text from two independent non-derivative
sources, cross-verified verbatim; official corroboration of decree identity/
date/preamble only) -- NOT inflated to TIER_2 or TIER_1.

97 records, ALL 'اصلية' (0 معدلة, 0 ملغاة, 0 مضافة, 0 مكرر): this is a
BRAND-NEW founding statute with no amendments yet (in force only a few weeks
as of this track's preparation). 11 أبواب; 7 of them flat (no فصول: الأول,
الرابع, الخامس, السادس, السابع, الثامن, الحادي عشر) and 4 subdivided into
فصول (الثاني: 7 فصول؛ الثالث: 7 فصول؛ التاسع: فصلان؛ العاشر: 3 فصول).

NAMED PREDECESSOR REPEAL: Article 96 explicitly supersedes and repeals the
Basic Law of Sports Federations and the Saudi Arabian Olympic Committee
(النظام الأساسي للاتحادات الرياضية واللجنة الأولمبية العربية السعودية),
Royal Decree M/55 (19/10/1407H), issued following Council of Ministers
Resolution 226 (13/9/1407H) -- both numbers independently corroborated via a
web search that surfaced the exact laws.boe.gov.sa indexing of that
predecessor title/decree/date. Article 97 sets the 180-day effective-date
rule (separate from, and not conflated with, the decree's issuance date).

TASHKEEL stripped uniformly (corpus-majority convention); curly quotes
straightened; double/nbsp spaces removed; in-word decorative kashida removed
(هـ preserved) -- display-layer only, no legal text altered. Arabic governs;
no translation/paraphrase/interpretation. Read-only over input; deterministic
over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "sports", "law", "official_source",
                   "sports_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "sports", "law", "verified")
RECORDS = os.path.join(OUT_VER, "sports_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "sports_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "sports_arabic_legal_llm",
                        "sports_law_legal_llm_001_097.json")

LAW_ID = "sa-sports-law-m-121-1447"
LAW_AR = "نظام الرياضة"
STATUS_UNCHANGED = "UNCHANGED"
KEY_RE = r"sports_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللوائح أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم الوزارة الوزير الكيان الرياضي الرياضية").split())


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


GOV_NOTE = ("Arabic governs; laws.boe.gov.sa and mos.gov.sa (Ministry of Sport, hosting an "
            "official نظام الرياضة PDF) were BOTH unreachable this pass (HTTP 503 / TLS "
            "connection-reset across WebFetch and direct curl, multiple attempts each; "
            "web.archive.org egress-blocked and NOT bypassed). The gazette's own JSON API "
            "(uqn.gov.sa/api/article/21263/json) DID confirm officially and directly: "
            "publication hijri_date 1447-6-21 / gregorian_date 12-12-2025, and a verbatim "
            "preamble excerpt matching nezams.com word-for-word (but not the substantive "
            "articles). The full 97-article text comes from TWO independent non-derivative "
            "aggregators (nezams.com primary, qanoonsa.com cross-check) verified verbatim "
            "article-by-article after digit/diacritic normalization -> TIER_3 (not inflated to "
            "TIER_2/TIER_1). 97 articles, ALL اصلية (brand-new founding statute, no amendments "
            "yet); 11 أبواب (7 flat, 4 with فصول). Article 96 NAMES and REPEALS the predecessor "
            "Royal Decree M/55 (19/10/1407H, following CoM Resolution 226, 13/9/1407H) -- both "
            "numbers independently corroborated via web search of the laws.boe.gov.sa index for "
            "that exact predecessor title. Article 97 sets the 180-day effective-date rule, kept "
            "separate from the decree's own issuance date (10/6/1447H). See "
            "verification_methodology_note and known_unresolved_discrepancies in the source "
            "artifact before relying on this track's text or provenance.")

SRC_AUTH = ("Royal Decree M/121 (10/6/1447H), CoM Resolution 414 (4/6/1447H, itself following "
            "Shura Council Resolution 424/39 dated 19/1/1447H), published Umm al-Qura issue 5129 "
            "dated 21/6/1447H / 12/12/2025G. Full text from nezams.com (primary) cross-checked "
            "verbatim article-by-article against qanoonsa.com (independent secondary), both "
            "non-official aggregators; decree identity/date/preamble independently confirmed via "
            "the official Umm al-Qura gazette's own JSON API (uqn.gov.sa). laws.boe.gov.sa and "
            "mos.gov.sa unreachable this pass (503 / TLS reset, multiple attempts each; Wayback "
            "egress-blocked, not bypassed) -> TIER_3")

SRC_AUTH_AR = ("المرسوم الملكي رقم م/121 وتاريخ 10/6/1447هـ، وقرار مجلس الوزراء رقم 414 وتاريخ "
               "4/6/1447هـ (بناء على قرار مجلس الشورى 424/39، 19/1/1447هـ)، منشور في أم القرى "
               "العدد 5129 بتاريخ 21/6/1447هـ الموافق 12/12/2025م. النص الكامل من nezams.com "
               "(أساسي) متقاطع حرفيا مادة بمادة مع qanoonsa.com (ثانوي مستقل)، وكلاهما مصدر غير "
               "رسمي؛ هوية المرسوم وتاريخه وديباجته مؤكدة رسميا عبر نقطة API الرسمية لبوابة أم "
               "القرى (uqn.gov.sa). تعذر الوصول إلى laws.boe.gov.sa وmos.gov.sa هذه الجولة "
               "(503/TLS reset عبر محاولات متعددة لكل منهما؛ أرشيف Wayback محظور ولم يُتجاوَز) "
               "-- TIER_3")


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
        ver.append({"law_key": "sports", "law_component": "law",
                    "language": "ar",
                    "record_layer": "SPORTS_LAW_ARABIC_VERIFIED_TEXT",
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
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "sports-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "sports/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام الرياضة" % a["number_label_ar"]],
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
    json.dump({"law_key": "sports",
               "layer": "SPORTS_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-sports-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (97 مادة؛ كلها أصلية)",
               "title_en": ("Sports Law — Arabic LLM-ready layer "
                            "(97 records, all original; brand-new founding statute)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 97], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Sports Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
