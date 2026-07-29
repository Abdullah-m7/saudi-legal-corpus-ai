#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Organizational Statute of the General Authority of Civil
Aviation (GACA) track (تنظيم الهيئة العامة للطيران المدني, Council of
Ministers Resolution No. 807, 14/11/1446H / 12 May 2025G).

VERIFICATION TIER -- see sources/gaca_organizational_statute/law/
official_source/gaca_organizational_statute_official_source.json's
verification_methodology_note for the full account. Summary:

PRIMARY SOURCE: uqn.gov.sa (جريدة أم القرى, the Kingdom's own official Umm
Al-Qura Gazette website) -- its own server-rendered article page (reached via
a 301 redirect from https://uqn.gov.sa/details?p=27192 to
https://www.uqn.gov.sa/details?p=27192) embeds the COMPLETE, untruncated
15-article statute text inside its own '<article id="article-content">'
element (present in the raw HTTP response body itself, not requiring
JavaScript execution) -- unlike the page's own <title>/meta/JSON-LD text and
its own underlying JSON API endpoint (api/article/20519/json), both of which
are truncated to a 694-character preview only.

laws.boe.gov.sa (retried at BOTH the BOE Law Id supplied in this track's own
task brief -- BOE's OLD record for the now-repealed Resolution-33 statute --
and a second, distinct BOE Law Id for the new Resolution-807 statute) and
web.archive.org (the Wayback Machine fallback) were BOTH confirmed
unreachable this pass: BOE returned HTTP 503 / a TLS connection reset on
every direct attempt (confirmed via curl -v), and web.archive.org returned
the tool-level error 'Claude Code is unable to fetch from web.archive.org'
via WebFetch and 'HTTP 503 Service Unavailable' via a direct curl against its
own CDX index.

SECONDARY CROSS-CHECK: qanoonsa.com's own reproduction of the statute's
15-article text (p/508802/) is a WORD-FOR-WORD MATCH with uqn.gov.sa's own
text after normalizing only cosmetic differences (Eastern- vs Western-Arabic
digit glyphs; a presentational U+200F RTL mark uqn.gov.sa's own markup embeds
around dashes; and qanoonsa's own page-furniture lines). qanoonsa.com's
separate decree-reproduction page (p/508801/) independently supplied the
exact decree number (807), the exact Hijri issuance date (14/11/1446H,
resolving this track's task brief's own open question), and the exact Umm
Al-Qura Gazette issue number/date (5088, 24 May 2025G).

TERTIARY CORROBORATION: argaam.com's own press coverage (published the same
date as the Gazette's own issue-5088 cover date) verbatim-quotes Articles 2
and 3 (matching after normalization) and independently confirms the
predecessor statute's exact citation (Resolution 33, 11 Safar 1426H) plus
several of the amending resolution's own transitional/operative provisions
(not ingested as new statute articles -- see known_unresolved_discrepancies).

WHOLESALE RE-ISSUE, NOT AN AMENDMENT LAYER: Resolution 807's own operative
item 'ثانياً' expressly REPLACES (not amends in place) the 2005 Resolution-33
predecessor statute in its entirety, with an entirely new, self-contained
15-article text. This track therefore models all 15 articles as ORIGINAL
(اصلية) under the new consolidated statute -- NOT as an amendment layer over
the predecessor -- and does not attempt to source Resolution 33's own text or
its two prior amendments (Resolutions 28/1433H and 120/1438H per this
track's own task brief), since none of that superseded text carries forward
into the current statute.

15 records: 15 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة. Flat structure, no
أبواب/فصول. No inline per-article titles in the source -- no title_ar field
is used.

No legal text is altered beyond stripping the source HTML's own
presentational markup and a presentational U+200F RTL control character.
Arabic governs; no translation/paraphrase/interpretation performed on the
Arabic text. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "gaca_organizational_statute", "law", "official_source",
                   "gaca_organizational_statute_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "gaca_organizational_statute", "law", "verified")
RECORDS = os.path.join(OUT_VER, "gaca_organizational_statute_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "gaca_organizational_statute_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "gaca_organizational_statute_arabic_legal_llm",
                        "gaca_organizational_statute_legal_llm_001_015.json")

LAW_ID = "sa-gaca-organizational-statute-807-1446"
LAW_AR = "تنظيم الهيئة العامة للطيران المدني"
TOP_STATUS = ("UQN_GOV_SA_OFFICIAL_GAZETTE_SSR_HTML_X_QANOONSA_COM_WORD_FOR_WORD_MATCH_X_"
              "ARGAAM_COM_TERTIARY_CORROBORATION_LIVE_BOE_AND_WAYBACK_BOTH_UNREACHABLE_"
              "THIS_PASS_WHOLESALE_REISSUE_ALL_ARTICLES_ORIGINAL")
KEY_RE = r"gaca_organizational_statute_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = set()
ADDED_KEYS = set()
REPEALED_KEYS = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام التنظيم اللائحة أحكام يجب يجوز "
            "عليه دون فيما منه منها وإذا حال وله ولها الهيئة المجلس الرئيس بوجه خاص").split())


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
        ver.append({"law_key": "gaca_organizational_statute", "law_component": "law",
                    "language": "ar",
                    "record_layer": "GACA_ORGANIZATIONAL_STATUTE_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; this track rests on uqn.gov.sa "
                                              "(the official Umm Al-Qura Gazette website)'s own "
                                              "server-rendered article HTML (cms_article_id "
                                              "20519, https://www.uqn.gov.sa/details?p=27192), "
                                              "cross-checked word-for-word against qanoonsa.com's "
                                              "reproduction (p/508802/ for the statute text, "
                                              "p/508801/ for the decree itself) and tertiarily "
                                              "corroborated by argaam.com's press coverage. "
                                              "laws.boe.gov.sa and web.archive.org were both "
                                              "confirmed unreachable this pass -- see "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact. Resolution 807 is a wholesale "
                                              "consolidated re-issue superseding Resolution 33 "
                                              "(11/2/1426H) in full; all 15 articles are "
                                              "ingested as original (اصلية), not as an amendment "
                                              "layer."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "gaca-organizational-statute-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "gaca_organizational_statute/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من تنظيم الهيئة العامة للطيران المدني" %
                                          a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Council of Ministers Resolution No. "
                                                          "(807), 14/11/1446H (12 May 2025G) -- "
                                                          "uqn.gov.sa (official Umm Al-Qura "
                                                          "Gazette website, article 20519) as "
                                                          "primary source; qanoonsa.com "
                                                          "(p/508802/, p/508801/) word-for-word "
                                                          "cross-check; argaam.com tertiary "
                                                          "press corroboration. laws.boe.gov.sa "
                                                          "and web.archive.org both confirmed "
                                                          "unreachable this pass. Wholesale "
                                                          "re-issue superseding Resolution 33 "
                                                          "(11/2/1426H) in full."),
                                     "source_authority_ar": "قرار مجلس الوزراء رقم (807) وتاريخ 14/11/1446هـ (الموافق 12 مايو 2025م) -- عبر جريدة أم القرى الرسمية (uqn.gov.sa، المقالة 20519) كمصدر أساسي؛ مطابقة حرفية مع qanoonsa.com (p/508802/ وp/508801/)؛ ومطابقة ثانوية إضافية مع تغطية argaam.com الصحفية. تعذّر الوصول إلى موقعي هيئة الخبراء بمجلس الوزراء وأرشيف الإنترنت (Wayback) هذه الجولة. إصدار جديد شامل يحل محل قرار مجلس الوزراء رقم (33) وتاريخ 11/2/1426هـ بالكامل.",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "gaca_organizational_statute",
               "layer": "GACA_ORGANIZATIONAL_STATUTE_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-gaca-organizational-statute-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (15 مادة؛ جميعها أصلية بموجب الإصدار الشامل الجديد)",
               "title_en": "Organizational Statute of the General Authority of Civil "
                          "Aviation (GACA) — Arabic LLM-ready layer (15 records, all "
                          "original under the 2025 wholesale re-issue)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 15], "text_status": TOP_STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready GACA Organizational Statute records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
