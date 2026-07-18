#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Maritime Commercial Law track (النظام البحري التجاري, Royal
Decree M/33, 5/4/1440H).

VERIFICATION TIER -- STATUS constant
BOE_WAYBACK_ARCHIVE_X_NEZAMS_X_BOE_OFFICIAL_ENGLISH_TRANSLATION_TRIPLE_VERIFIED_LIVE_BOE_UNREACHABLE
reflects that laws.boe.gov.sa's LIVE portal was unreachable this pass (direct
HTTPS curl attempts returned 'Recv failure: Connection reset by peer' on both
the Arabic law page and the BOE-hosted official English-translation PDF
download link) -- BUT Wayback Machine snapshots of BOTH the exact BOE Arabic
law-detail page and the BOE-hosted official English-translation PDF WERE
reachable via https:// this pass (http:// returned 403 for both). The Arabic
page was parsed with BeautifulSoup (locating each of 391 'article_item' divs
and its 'HTMLContainer' child, plus the interleaved باب/فصل heading
structure) to recover the full text of all 391 articles, the decree
number/date, and BOE's own per-article HTML class attributes -- all 391
articles carry ONLY the default 'no_alternate' class, with zero amended/
repealed markers anywhere on the page.

This was cross-verified against nezams.com's independent HTML transcription
of all 391 articles (fetched live, directly, with a browser User-Agent
header) -- full text agreement (after NFC normalization and normalizing a
handful of purely-cosmetic NBSP/quote-glyph differences) on 381 of 391
articles. The remaining 10 (Articles 316-325) reflect a nezams.com site-side
content-duplication bug (it repeats Articles 306-315's content under those
labels) -- resolved via BOE's own official English-translation PDF (a wholly
separate BOE-hosted document, 98 pages, downloaded and read in full via
pdftotext), which independently confirms BOE's Arabic sequence and content
for that range. See sources/maritime_commercial/law/official_source/
maritime_commercial_law_official_source.json for the full methodology note
and every documented discrepancy, including the un-ingested companion
implementing regulations (plural -- this Law spawned several, not one
consolidated Regulation) and a transparent terminology note on 'الرئيس' vs
the Article-1-defined term 'الوزير'.

391 records, ALL اصلية (original, unamended) -- this Royal Decree has never
been amended since 1440H. Repeals Book Two of the Commercial Court
Regulation (Royal Decree No. 32, 15/1/1350H) and the Ports, Harbours and
Lighthouses Law (Royal Decree M/27, 24/6/1394H) per its own Article 391.

No legal text is altered beyond the documented cosmetic whitespace/quote-
glyph/diacritic-order normalizations. Arabic governs; no translation/
paraphrase/interpretation. Read-only over input; deterministic over
outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "maritime_commercial", "law", "official_source",
                   "maritime_commercial_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "maritime_commercial", "law", "verified")
RECORDS = os.path.join(OUT_VER, "maritime_commercial_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "maritime_commercial_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "maritime_commercial_arabic_legal_llm",
                        "maritime_commercial_law_legal_llm_001_391.json")

LAW_ID = "sa-maritime-commercial-law-m33-1440"
LAW_AR = "النظام البحري التجاري"
STATUS = "BOE_WAYBACK_ARCHIVE_X_NEZAMS_X_BOE_OFFICIAL_ENGLISH_TRANSLATION_TRIPLE_VERIFIED_LIVE_BOE_UNREACHABLE"
KEY_RE = r"maritime_commercial_art_(\d{3})(?:_mukarrar(\d*))?$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللوائح أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك السفينة").split())


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
        text = a["text"]
        ver.append({"law_key": "maritime_commercial", "law_component": "law",
                    "language": "ar",
                    "record_layer": "MARITIME_COMMERCIAL_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "original_text": a.get("original_1440h_text"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track rests on a BOE-via-"
                                              "Wayback-Machine archived snapshot as the PRIMARY "
                                              "source (live BOE unreachable), cross-verified "
                                              "against nezams.com's live HTML transcription "
                                              "(exact agreement on 381/391 articles; the "
                                              "remaining 10 -- Articles 316-325 -- reflect a "
                                              "documented nezams.com duplication bug resolved "
                                              "via BOE's own official English-translation PDF, "
                                              "a third independent BOE-hosted document). This "
                                              "Royal Decree has never been amended since "
                                              "1440H -- all 391 articles are اصلية. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact for full caveats, including the "
                                              "un-ingested companion implementing regulations "
                                              "(plural) and the الرئيس/الوزير terminology "
                                              "note."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "maritime-commercial-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "maritime_commercial/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من النظام البحري التجاري" % a["number_label_ar"]],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Decree M/33 — laws.boe.gov.sa "
                                                          "via Wayback Machine archive (primary), "
                                                          "cross-verified against nezams.com and "
                                                          "BOE's own official English-translation "
                                                          "PDF; live BOE unreachable this pass"),
                                     "source_authority_ar": "مرسوم ملكي رقم (م/33) — نسخة أرشيفية من بوابة هيئة الخبراء عبر Wayback Machine، مطابقة مع نزامز.كوم وترجمة هيئة الخبراء الإنجليزية الرسمية",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "maritime_commercial",
               "layer": "MARITIME_COMMERCIAL_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-maritime-commercial-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (391 مادة؛ جميعها أصلية)",
               "title_en": "Saudi Commercial Maritime Law — Arabic LLM-ready layer (391 records, unamended)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 391], "text_status": STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Maritime Commercial Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
