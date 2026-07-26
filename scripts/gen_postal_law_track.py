#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Postal Law track (نظام البريد, Royal Decree M/22, 08/03/1443H).

*** THIS IS A DELIBERATE, DISCLOSED PARTIAL-COVERAGE TRACK. ***
See sources/postal_law/law/official_source/postal_law_official_source.json's
verification_methodology_note and known_unresolved_discrepancies for the
full account. Summary:

The Postal Law is reported (lexismiddleeast.com's independent structural
scrape of Council of Ministers Resolution 149's page, corroborated by
Arab News quoting Saudi Communications Minister Abdullah Al-Swaha directly)
to contain 37 articles across nine فصول. This track ingests ONLY Articles
1-20 (فصول 1-4 in full, plus Article 20 alone of فصل 5's three articles)
-- the only articles for which verbatim text could be retrieved this pass
with confidence.

PRIMARY SOURCE: laws.boe.gov.sa returned HTTP 503 on every attempt (both
WebFetch and direct curl -- curl failed at the TLS-handshake stage,
suggesting the destination is unreachable from this session's egress path).
web.archive.org is categorically blocked for this session's WebFetch tool.
tga.gov.sa and site.eastlaws.com likewise failed to connect via curl.
mot.gov.sa and the Umm Al-Qura Gazette (uqn.gov.sa) returned no substantive
content (404/redirect, or a pure client-rendered SPA shell with no
server-side text). qanoonsa.com/qanoniah.com are also pure client-rendered
SPAs.

SECONDARY SOURCE THAT DID YIELD CONTENT: nezams.com's page is server-side
rendered and embeds all 38 of its own listed articles' text directly in
the HTML. Its own page metadata independently confirms decree/resolution
numbers, dates, and states "لم يجرى عليه تعديل" (no amendment made) for
the Law itself. CRITICALLY, while articles 1-20's فصل headings exactly
match lexismiddleeast.com's independent chapter/range breakdown, the BODY
TEXT under every heading from article 21 onward is verbatim content from
an entirely unrelated law (the Solid Municipal Waste Management Law,
Royal Decree M/48, 17/9/1434H) -- confirmed reproducible across two
separate fetches. Consequence: nezams.com is treated as reliable for
Articles 1-20 only.

Articles 21-37 are NOT ingested: no reachable source could supply their
verbatim text this pass. A handful of un-sourced web-search fragments
(an Article 23-like liability clause, an Article 31-like penalty clause,
a 180-day enactment clause) are documented as LEADS ONLY in
known_unresolved_discrepancies -- explicitly not ingested as verified text.

Regulatory-transfer finding: Council of Ministers Resolution 705,
27/12/1443H, is reported (via WebSearch synthesis, not a direct primary
fetch) to transfer postal-sector oversight from CITC/Ministry of
Communications and IT to the General Authority for Transport (TGA) and
Ministry of Transport and Logistics Services, via terminology substitution
across the Law and related instruments -- corroborated circumstantially by
TGA's own Regulations portal hosting this Law's Executive Regulation, and
by a TGA-issued 2023 administrative decision approving the Law's
violations/penalties table. This is treated as a confirmed administrative
reassignment, NOT a confirmed textual amendment of any specific numbered
article (no source reachable this pass identified specific edited
articles; nezams.com's own amendment field for this Law reads "no
amendment made").

No legal text is altered beyond whitespace/line-break normalization
(<br> -> newline; collapsed whitespace/zero-width artifacts; the leading
فصل/title/bare-ordinal heading lines nezams.com repeats atop the first
article of each فصل are relocated into chapter_structure/section_ar
rather than left inline). Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "postal_law", "law", "official_source",
                   "postal_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "postal_law", "law", "verified")
RECORDS = os.path.join(OUT_VER, "postal_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "postal_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "postal_law_arabic_legal_llm",
                        "postal_law_legal_llm_001_020.json")

LAW_ID = "sa-postal-law-m22-1443"
LAW_AR = "نظام البريد"
TOP_STATUS = ("NEZAMS_SSR_HTML_LIVE_FETCH_X_LEXISMIDDLEEAST_STRUCTURAL_CROSSCHECK_"
              "ARTS_1_20_ONLY_BOE_LIVE_AND_WAYBACK_UNREACHABLE")
KEY_RE = r"postal_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = set()
ADDED_KEYS = set()
REPEALED_KEYS = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك الهيئة مقدم الخدمة").split())


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
        ver.append({"law_key": "postal_law", "law_component": "law",
                    "language": "ar",
                    "record_layer": "POSTAL_LAW_ARABIC_VERIFIED_TEXT",
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
                    "coverage_status": "PARTIAL_VERIFIED_SUBSET",
                    "governing_source_note": ("Arabic governs; this track rests on a live, "
                                              "server-side-rendered HTML fetch of nezams.com "
                                              "(laws.boe.gov.sa unreachable this pass, both "
                                              "live and via Wayback), cross-verified "
                                              "structurally against lexismiddleeast.com's "
                                              "independent chapter/article-range scrape "
                                              "through Article 20. ONLY Articles 1-20 of a "
                                              "reported 37-article law are ingested -- "
                                              "Articles 21-37 could not be verified this "
                                              "pass (nezams.com's own content for those "
                                              "articles is confirmed corrupted with an "
                                              "unrelated law's text). See "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track as "
                                              "complete."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "postal-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "postal_law/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام البريد" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree M/22 — nezams.com "
                                                          "(live server-rendered fetch), "
                                                          "cross-verified against "
                                                          "lexismiddleeast.com's structural "
                                                          "scrape; laws.boe.gov.sa "
                                                          "unreachable this pass. Covers "
                                                          "Articles 1-20 of a reported "
                                                          "37-article law only"),
                                     "source_authority_ar": "مرسوم ملكي رقم (م/22) — نزوم (نزوم.كوم)، تحقق بنيوي مقابل lexismiddleeast.com؛ تعذر الوصول إلى هيئة الخبراء بمجلس الوزراء هذه الجولة. يغطي المواد 1-20 فقط من أصل 37 مادة مُبلَّغ عنها",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"],
                                     "coverage_status": "PARTIAL_VERIFIED_SUBSET"},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "postal_law",
               "layer": "POSTAL_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": TOP_STATUS,
               "coverage_status": "PARTIAL_VERIFIED_SUBSET",
               "official_reported_article_count": src.get("official_reported_article_count"),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-postal-law-arabic-legal-llm-partial",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (20 مادة "
                           "موثقة من أصل 37 مادة مُبلَّغ عنها -- تغطية جزئية مُفصح عنها)",
               "title_en": "Postal Law — Arabic LLM-ready layer (20 verified records out "
                           "of a reported 37 total articles; DISCLOSED PARTIAL COVERAGE, "
                           "Articles 21-37 not yet verified/ingested)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 20], "text_status": TOP_STATUS,
               "coverage_status": "PARTIAL_VERIFIED_SUBSET",
               "official_reported_article_count": src.get("official_reported_article_count"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Postal Law records (PARTIAL: 20/37)" %
          (len(ver), len(llm)))


if __name__ == "__main__":
    main()
