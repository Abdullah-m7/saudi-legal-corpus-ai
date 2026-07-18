#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Law of Practicing Healthcare Professions track (نظام مزاولة
المهن الصحية, Royal Decree M/59, 4/11/1426H).

VERIFICATION TIER -- STATUS constant
BOE_WAYBACK_ARCHIVE_X_NEZAMS_CROSS_VERIFIED_LIVE_BOE_UNREACHABLE
reflects that laws.boe.gov.sa's LIVE portal was unreachable this pass (direct
HTTPS connection attempts returned curl exit code 35 / no response, on both
the law-detail URL and the bare BOE domain) -- BUT a Wayback Machine snapshot
of this exact BOE law page (timestamped 20251116121007, re-confirmed as the
closest available snapshot when re-queried at timestamp 2026-07-17) WAS
reachable via direct curl over https://web.archive.org/ (https:// succeeded,
HTTP 200, ~94KB; the plain http:// scheme returned HTTP 403 for this
snapshot -- the opposite of what worked for this corpus's
cooperative_health_insurance_law track, so both schemes were tried per this
corpus's established practice and whichever worked was used). It was parsed
with BeautifulSoup (locating each 'article_item' div and its 'HTMLContainer'
child) to recover the full text of all 44 articles, the decree number/date,
and BOE's own per-article HTML class attributes -- all 44 articles carry
ONLY the default 'no_alternate' class, with zero amended/repealed markers
anywhere on the page (the only two occurrences of 'معدلة'/'ملغية' are the
page's own generic filter-checkbox UI labels, unrelated to any article).

This was cross-verified against nezams.com's independent HTML transcription
of all 44 articles (fetched live, directly, with a browser User-Agent
header) -- a full normalized-text comparison found agreement on 42 of 44
articles with ZERO differences, and two trivial, fully-documented,
non-substantive artifacts confined to nezams.com's own page (an isolated
single-character typo in Article 36, and a page-boundary scrape artifact
after Article 44 -- see known_unresolved_discrepancies). nezams.com's own
'التعديلات' (amendments) field independently states 'لم يجرِ عليه تعديل'
(no amendment has been made), matching BOE's lack of any per-article
amendment marker.

44 records, ALL اصلية (original, unamended) -- this Royal Decree has never
been amended since 1426H. The chapter/فصل/فرع structure (absent from BOE's
own per-article HTML but described in BOE's own prose summary field) was
independently confirmed, with exact article boundaries, against moh.gov.sa's
official consolidated Arabic AND English PDFs of the Law + Implementing
Regulation. A PROPOSED (Shura Council, December 2023) but NOT YET ENACTED
new Article 4 bis is documented in known_unresolved_discrepancies rather
than fabricated into this track. See
sources/healthcare_professions/law/official_source/
healthcare_professions_law_official_source.json for the full methodology
note and every documented discrepancy, including the un-ingested companion
Implementing Regulation (Ministerial Resolution No. 4080489, 2/1/1439H).

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "healthcare_professions", "law", "official_source",
                   "healthcare_professions_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "healthcare_professions", "law", "verified")
RECORDS = os.path.join(OUT_VER, "healthcare_professions_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "healthcare_professions_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "healthcare_professions_arabic_legal_llm",
                        "healthcare_professions_law_legal_llm_001_044.json")

LAW_ID = "sa-healthcare-professions-law-m59-1426"
LAW_AR = "نظام مزاولة المهن الصحية"
STATUS = "BOE_WAYBACK_ARCHIVE_X_NEZAMS_CROSS_VERIFIED_LIVE_BOE_UNREACHABLE"
KEY_RE = r"healthcare_professions_art_(\d{3})(?:_mukarrar(\d*))?$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك الصحي الصحية المهن").split())


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


def _original_text(a):
    for k in ("original_1409h_text", "original_1426h_text"):
        if a.get(k):
            return a[k]
    return None


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
        text = a["text"]
        original_text = _original_text(a)
        ver.append({"law_key": "healthcare_professions", "law_component": "law",
                    "language": "ar",
                    "record_layer": "HEALTHCARE_PROFESSIONS_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "original_text": original_text,
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track rests on a BOE-via-"
                                              "Wayback-Machine archived snapshot as the PRIMARY "
                                              "source (live BOE unreachable), cross-verified "
                                              "against nezams.com's live HTML transcription "
                                              "(agreement on 42 of 44 articles with zero "
                                              "differences; 2 trivial nezams.com-side artifacts "
                                              "documented, neither adopted). This Royal Decree "
                                              "has never been amended since 1426H -- all 44 "
                                              "articles are اصلية. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact for full caveats, including the "
                                              "un-ingested companion Implementing Regulation and "
                                              "a pending, NOT-yet-enacted proposed Article 4 "
                                              "bis."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "healthcare-professions-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "healthcare_professions/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام مزاولة المهن الصحية" % a["number_label_ar"]],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Decree M/59 — laws.boe.gov.sa "
                                                          "via Wayback Machine archive (primary), "
                                                          "cross-verified against nezams.com; "
                                                          "live BOE unreachable this pass"),
                                     "source_authority_ar": "مرسوم ملكي رقم (م/59) — نسخة أرشيفية من بوابة هيئة الخبراء عبر Wayback Machine، مطابقة مع نزامز.كوم",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "healthcare_professions",
               "layer": "HEALTHCARE_PROFESSIONS_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-healthcare-professions-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (44 مادة؛ جميعها أصلية)",
               "title_en": "Saudi Law of Practicing Healthcare Professions — Arabic LLM-ready layer (44 records, unamended)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 44], "text_status": STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Healthcare Professions Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
