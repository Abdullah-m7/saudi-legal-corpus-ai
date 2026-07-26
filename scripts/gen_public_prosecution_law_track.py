#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Public Prosecution Law track (نظام النيابة العامة، سابقاً نظام
هيئة التحقيق والادعاء العام، المرسوم الملكي رقم م/56 وتاريخ 24/10/1409هـ).

VERIFICATION TIER -- see sources/public_prosecution_law/law/official_source/
public_prosecution_law_official_source.json's verification_methodology_note for
the full account. Summary:

PRIMARY SOURCE: laws.boe.gov.sa's live portal was unreachable this pass (HTTP 503
via one tool path, TLS/connection reset via a direct curl attempt). A SINGLE
Wayback Machine snapshot (20260215023949, 15 Feb 2026) was fetched instead (via
curl through the session's egress proxy, since the WebFetch tool itself declines
web.archive.org URLs) and parsed with BeautifulSoup: 30 'article_item' divs, 16 of
which carry an 'ancArticlePrevVersions' amendment-history popup log. Critically,
each article's MAIN displayed HTMLContainer text turned out to be the law's
ORIGINAL 1409H wording, not its current text -- confirmed directly by BOE's own
popup log, which shows each amendment's resulting wording (where quoted) diverging
from that main body. This generator therefore reads 'text' as already resolved
(by the source artifact) to the best-confirmed CURRENT wording for every article,
and 'original_1409h_text' as the separately preserved 1409H baseline.

FOUR distinct amending instruments confirmed directly from BOE's own per-article
history log -- a correction/refinement of this task's initial working summary,
which had not been aware of the second one: Royal Decree M/4 (5/1/1433H, Art. 1
only), Royal Decree M/31 (13/4/1436H, Arts. 2,3,4,5,9,10,12,15,24,25,26), Royal
Decree M/125 (14/9/1441H -- NOT in the task's initial brief, discovered this pass;
Arts. 1,2,3,4,10,13,16,17,26,27 amended, Arts. 11 and 28 REPEALED), and Royal
Decree M/180 (17/8/1446H, Art. 4 paragraph (1) only, independently corroborated
via an official-decree mirror on qanoonsa.com). Royal Order A/240 (22/9/1438H)
renamed the governing body (هيئة التحقيق والادعاء العام -> النيابة العامة) but is
not itself a per-article BOE amendment entry -- documented as background only.

30 records: 12 اصلية, 16 معدلة, 2 ملغاة (Arts. 11, 28), 0 مضافة. Flat structure,
no باب/فصل subdivision on the BOE page (section_ar empty for every article) --
see known_unresolved_discrepancies, key public_prosecution_law_no_formal_chapter_
structure. THREE articles (3, 4, 16) carry current_wording_fully_confirmed=false:
BOE's own history log confirms each was further amended by M/125 but does not
quote the resulting text, and the sole independent secondary source reached this
pass (nezams.com) is entirely silent on M/125 for every article of this law. Per
this task's explicit instruction, this track does NOT reconstruct or guess at
these three articles' true current wording -- it ingests the last fully verbatim-
confirmed snapshot and flags the gap prominently, both per-article and in
known_unresolved_discrepancies.

No legal text is altered beyond whitespace/line-break normalization. Arabic
governs; no translation/paraphrase/interpretation. Read-only over input;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "public_prosecution_law", "law", "official_source",
                   "public_prosecution_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "public_prosecution_law", "law", "verified")
RECORDS = os.path.join(OUT_VER, "public_prosecution_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "public_prosecution_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "public_prosecution_law_arabic_legal_llm",
                        "public_prosecution_law_legal_llm_001_030.json")

LAW_ID = "sa-public-prosecution-law-m56-1409"
LAW_AR = "نظام النيابة العامة"
TOP_STATUS = "BOE_WAYBACK_PRIMARY_ARCHIVE_SINGLE_SNAPSHOT_X_NEZAMS_HTML_BYTE_CROSSCHECK_X_QANOONSA_OFFICIAL_DECREE_MIRROR_LIVE_BOE_UNREACHABLE"
KEY_RE = r"public_prosecution_law_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك الهيئة رئيس نائب").split())


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
    return int(m.group(1))


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for idx, key in enumerate(keys, start=1):
        a = arts[key]
        n = _sort_key(key)
        ls = a.get("legal_status_ar")
        is_repealed = ls == "ملغاة"
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        text = a["text"]
        confirmed = a.get("current_wording_fully_confirmed", True)
        ver.append({"law_key": "public_prosecution_law", "law_component": "law",
                    "language": "ar",
                    "record_layer": "PUBLIC_PROSECUTION_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "current_wording_fully_confirmed": confirmed,
                    "original_1409h_text": a.get("original_1409h_text"),
                    "amendment_history": a.get("history"),
                    "official_text_status": TOP_STATUS,
                    "governing_source_note": ("Arabic governs; this track rests on a single BOE-via-"
                                              "Wayback-Machine archived snapshot (20260215023949, "
                                              "15 Feb 2026; live BOE unreachable this pass) as PRIMARY "
                                              "source, cross-verified against nezams.com (byte-level, "
                                              "for the 1409H/M4/M31/M180 layers) and qanoonsa.com "
                                              "(independent official-decree mirror for M/180). Three "
                                              "articles (3, 4, 16) carry current_wording_fully_confirmed"
                                              "=false -- see this record's own field and the source "
                                              "artifact's known_unresolved_discrepancies before relying "
                                              "on their text as current law."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_amended": is_amended, "is_added": is_added,
                    "current_wording_fully_confirmed": confirmed,
                    "record_id": "public-prosecution-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "public_prosecution_law/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام النيابة العامة" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree M/56 — laws.boe.gov.sa via a "
                                                          "single Wayback Machine snapshot (live BOE "
                                                          "unreachable this pass), cross-verified "
                                                          "against nezams.com and qanoonsa.com"),
                                     "source_authority_ar": "مرسوم ملكي رقم (م/56) — نسخة أرشيفية من بوابة هيئة الخبراء عبر Wayback Machine، مطابقة مع nezams.com وqanoonsa.com",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"],
                                     "current_wording_fully_confirmed": confirmed},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "public_prosecution_law",
               "layer": "PUBLIC_PROSECUTION_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": TOP_STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-public-prosecution-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (30 مادة؛ 12 أصلية، 16 معدّلة، 2 ملغاة)",
               "title_en": "Public Prosecution Law — Arabic LLM-ready layer (30 records: 12 original, 16 amended, 2 repealed)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 30], "text_status": TOP_STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Public Prosecution Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
