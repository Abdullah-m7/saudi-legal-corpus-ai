#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Finance Lease Law track (نظام الإيجار التمويلي, Royal Decree
M/48, 13/8/1433H).

VERIFICATION TIER -- STATUS constant
BOE_WAYBACK_ARCHIVE_X_SAMA_RULEBOOK_PDF_X_NEZAMS_TRIPLE_VERIFIED_LIVE_BOE_UNREACHABLE
reflects that laws.boe.gov.sa's LIVE portal was unreachable this pass (direct
HTTPS/HTTP curl attempts returned exit code 28 / connection timeout on both
schemes) -- BUT a Wayback Machine snapshot of this exact BOE law page
(timestamped 20251212220818) WAS reachable via https:// (http:// returned
403 for the same snapshot; both schemes were tried per this corpus's
established practice and whichever worked was used). It was parsed with
BeautifulSoup (locating each 'article_item' div and its 'HTMLContainer'
child) to recover the full text of all 28 articles, the decree number/date,
and BOE's own per-article HTML class attributes -- all 28 articles carry
ONLY the default 'no_alternate' class, with zero amended/repealed markers
anywhere on the page.

This was cross-verified against nezams.com's independent HTML transcription
of all 28 articles (fetched live, directly, with a browser User-Agent
header) -- full text agreement on all 28 articles (the only variation was a
cosmetic hyphen/en-dash style difference in enumerated sub-items, with no
effect on legal meaning). nezams.com's own 'التعديلات' field independently
states 'لم يجرى عليه تعديل' (no amendment has been made), matching BOE's
lack of any per-article amendment marker.

A THIRD independent source -- rulebook.sama.gov.sa (Saudi Central Bank's
own official Rulebook, since SAMA administers this Law) -- hosts both an
official Arabic PDF and an official English-translation PDF of this exact
Law; both were downloaded and read in full. These PDFs are the ONLY source
that renders the Law's chapter/فصل headings inline with the article text,
establishing (with unambiguous heading placement) a 5-part structure:
فصل تمهيدي (Article 1 only); الفصل الأول (Articles 2-17); الفصل الثاني
(Articles 18-23 -- NOT 18-20 as an initial webpage-summary artifact had
suggested, see known_unresolved_discrepancies); الفصل الثالث (Articles
24-26); الفصل الرابع (Articles 27-28). No فرع subdivisions exist in this
Law.

28 records, ALL اصلية (original, unamended) -- this Royal Decree has never
been amended since 1433H (only its companion Implementing Regulation has
been separately amended -- not ingested this pass). No repeal/supersession
clause naming a predecessor statute was found. See
sources/finance_lease/law/official_source/finance_lease_law_official_source.json
for the full methodology note and every documented discrepancy, including
the un-ingested companion Implementing Regulation (Administrative/Governor's
Decision 1/م ش ت, 14/4/1434H).

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "finance_lease", "law", "official_source",
                   "finance_lease_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "finance_lease", "law", "verified")
RECORDS = os.path.join(OUT_VER, "finance_lease_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "finance_lease_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "finance_lease_arabic_legal_llm",
                        "finance_lease_law_legal_llm_001_028.json")

LAW_ID = "sa-finance-lease-law-m48-1433"
LAW_AR = "نظام الإيجار التمويلي"
STATUS = "BOE_WAYBACK_ARCHIVE_X_SAMA_RULEBOOK_PDF_X_NEZAMS_TRIPLE_VERIFIED_LIVE_BOE_UNREACHABLE"
KEY_RE = r"finance_lease_art_(\d{3})(?:_mukarrar(\d*))?$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك المؤجر المستأجر العقد الأصل").split())


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
    for k in ("original_1433h_text",):
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
        ver.append({"law_key": "finance_lease", "law_component": "law",
                    "language": "ar",
                    "record_layer": "FINANCE_LEASE_LAW_ARABIC_VERIFIED_TEXT",
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
                                              "(agreement on all 28 articles) and against "
                                              "rulebook.sama.gov.sa's official Arabic and "
                                              "English PDFs (which also independently establish "
                                              "the chapter structure). This Royal Decree has "
                                              "never been amended since 1433H -- all 28 "
                                              "articles are اصلية. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact for full caveats, including the "
                                              "un-ingested companion Implementing Regulation."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "finance-lease-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "finance_lease/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام الإيجار التمويلي" % a["number_label_ar"]],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Decree M/48 — laws.boe.gov.sa "
                                                          "via Wayback Machine archive (primary), "
                                                          "cross-verified against nezams.com and "
                                                          "rulebook.sama.gov.sa's official PDFs; "
                                                          "live BOE unreachable this pass"),
                                     "source_authority_ar": "مرسوم ملكي رقم (م/48) — نسخة أرشيفية من بوابة هيئة الخبراء عبر Wayback Machine، مطابقة مع نزامز.كوم وبوابة ساما الرسمية",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "finance_lease",
               "layer": "FINANCE_LEASE_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-finance-lease-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (28 مادة؛ جميعها أصلية)",
               "title_en": "Saudi Finance Lease Law — Arabic LLM-ready layer (28 records, unamended)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 28], "text_status": STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Finance Lease Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
