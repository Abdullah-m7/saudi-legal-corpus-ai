#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Chambers of Commerce Law track
(اللائحة التنفيذية لنظام الغرف التجارية), the follow-up track for this corpus's
chambers_of_commerce (base law) track.

VERIFICATION TIER -- see sources/chambers_of_commerce_regulation/law/official_source/
chambers_of_commerce_regulation_official_source.json's verification_methodology_note
for the full account. Summary:

PRIMARY SOURCE: the Umm Al-Qura official gazette (uqn.gov.sa/?p=7074). The live site
redirects to a JavaScript-rendered (Vue SPA) page with no article text in raw HTML, so
a Wayback Machine archive snapshot (2022-08-18, a pre-relaunch WordPress version of the
site carrying the full 63-article text in raw HTML) was used instead.

INDEPENDENT CROSS-CHECK: an official PDF published by the Federation of Saudi Chambers
(fsc.org.sa) -- the chambers' own legal umbrella body, addressed directly in the
regulation's text -- was compared article-by-article and table-row-by-row against the
Umm Al-Qura text. All 63 articles match in numbering/order/headings; full-text spot
checks (including the Article 40 numeric fee table and Article 44) show zero content
differences, aside from one disclosed sub-clause numbering divergence in Article 15.

CONFIRMED AMENDMENT: Ministerial Decision No. 87 (12/5/1447H / 3 Nov 2025), amending
ONLY Article 10 (chamber board member-count tiers: 9/12/15/18 -> 6/9/12), published in
Umm Al-Qura Gazette issue 5122 (14/11/2025). Sourced via qanoonsa.com's full-text
republication (an independent legal-tracking site, not the government itself) and
corroborated by an independent news source (akhbaar24.com) matching the same figures
and publication date.

PENDING DRAFT (NOT ADOPTED): a proposed amendment to Article 44 (performance-evaluation
mechanism) was floated for public consultation via istitlaa.ncc.gov.sa and
eparticipation.my.gov.sa from 12-27 Jan 2025. This pass independently re-checked its
status: despite ~17 months elapsed and a comprehensive listing of Ministry of Commerce
ministerial decisions on qanoonsa.com covering through mid-May 2026 (which DOES include
the Article 10 amendment above), NO decision implementing this Article 44 draft was
found. Article 44 is therefore recorded here in its ORIGINAL (اصلية) form; the pending,
unadopted draft is recorded separately (not merged into the article text) under
pending_draft_amendments in the source artifact.

63 records: 62 اصلية, 1 معدلة (Article 10), 0 ملغاة, 0 مضافة. This regulation has its
OWN independent chapter/باب structure (not keyed to the base law's own 66-article
numbering) -- unlike this corpus's anti_smoking_regulation track (flat, base-law-keyed).

Arabic governs; no translation/paraphrase/interpretation. Read-only over input;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "chambers_of_commerce_regulation", "law", "official_source",
                   "chambers_of_commerce_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "chambers_of_commerce_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "chambers_of_commerce_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "chambers_of_commerce_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "chambers_of_commerce_regulation_arabic_legal_llm",
                        "chambers_of_commerce_regulation_legal_llm_001_063.json")

LAW_ID = "sa-chambers-of-commerce-regulation-2021-decision10"
LAW_AR = "اللائحة التنفيذية لنظام الغرف التجارية"
CORPUS = "chambers_of_commerce_regulation"
STATUS = "MATCHES_UQN_GAZETTE_X_FSC_INDEPENDENT_CROSS_CHECK"
KEY_RE = r"chambers_of_commerce_regulation_art_(\d{3})(_mukarrar)?$"
N_ARTICLES = 63
RECID_PREFIX = "chambers-of-commerce-regulation-llm-art"
SEARCH_TERM = "اللائحة التنفيذية لنظام الغرف التجارية"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك").split())


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
    return (int(m.group(1)), 1 if m.group(2) else 0)


GOV_NOTE = ("Arabic governs; laws.boe.gov.sa has NO dedicated lawId page for this "
            "Implementing Regulation (only for the base Chambers of Commerce Law). PRIMARY "
            "full-text source: the Umm Al-Qura official gazette (uqn.gov.sa/?p=7074), accessed "
            "via a Wayback Machine archive snapshot since the live site is a JavaScript-"
            "rendered SPA. CROSS-CHECK: an official Federation of Saudi Chambers (fsc.org.sa) "
            "PDF, matched article-by-article and table-row-by-row with zero content "
            "differences -> TIER_2. One confirmed amendment (Article 10, Ministerial Decision "
            "No. 87, 12/5/1447H) verified via an independent legal-tracking site (qanoonsa.com) "
            "and corroborated by an independent news source (akhbaar24.com). A separate "
            "proposed amendment to Article 44 was floated for public consultation in Jan 2025 "
            "but was NOT found to be adopted as of this pass -- Article 44 here reflects its "
            "original, unamended text; the pending draft is recorded separately under "
            "pending_draft_amendments. See verification_methodology_note and "
            "known_unresolved_discrepancies in the source artifact before relying on this "
            "track's text or provenance.")

SRC_AUTH = ("Implementing Regulation of the Chambers of Commerce Law, issued by the Minister "
            "of Commerce under Article 64 of Royal Decree M/37 (22/4/1442H), via Ministerial "
            "Decision No. 10 (11/1/1443H). Full text from the Umm Al-Qura gazette (Wayback "
            "archive of uqn.gov.sa/?p=7074), cross-checked against an official Federation of "
            "Saudi Chambers (fsc.org.sa) PDF. Confirmed amendment: Ministerial Decision No. 87 "
            "(12/5/1447H), Article 10 only -> TIER_2")

SRC_AUTH_AR = ("اللائحة التنفيذية لنظام الغرف التجارية، صادرة عن وزير التجارة عملا بالمادة "
               "(الرابعة والستين) من المرسوم الملكي رقم م/37 وتاريخ 22/4/1442هـ، بموجب القرار "
               "الوزاري رقم (10) وتاريخ 11/1/1443هـ. النص الكامل من جريدة أم القرى (عبر أرشيف "
               "Wayback لصفحة uqn.gov.sa/?p=7074)، متقاطع مع نسخة رسمية صادرة عن اتحاد الغرف "
               "التجارية السعودية (fsc.org.sa). تعديل مؤكد: القرار الوزاري رقم (87) وتاريخ "
               "12/5/1447هـ (المادة العاشرة فقط) -- TIER_2")


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for key in keys:
        a = arts[key]
        m = re.match(KEY_RE, key)
        n, is_muk = int(m.group(1)), bool(m.group(2))
        suffix = "-mukarrar" if is_muk else ""
        ls = a.get("legal_status_ar")
        is_repealed = ls == "ملغاة"
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        text = a["text"]
        ver.append({"law_key": CORPUS, "law_component": "regulation", "language": "ar",
                    "record_layer": "CHAMBERS_OF_COMMERCE_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_muk, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "article_title_ar": a.get("article_title_ar", ""),
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": GOV_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_muk, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "%s-%03d%s" % (RECID_PREFIX, n, suffix),
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s%s" % (LAW_AR, a["number_label_ar"],
                                                   " (معدلة)" if is_amended else ""),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "%s/law/articles/%03d%s" % (CORPUS, n, suffix),
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d %s" % (n, SEARCH_TERM)],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": SRC_AUTH,
                                     "source_authority_ar": SRC_AUTH_AR,
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": CORPUS,
               "layer": "CHAMBERS_OF_COMMERCE_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "founding_resolution_confirmed": src.get("founding_resolution_confirmed", False),
               "founding_resolution_confirmation_method":
                   src.get("founding_resolution_confirmation_method"),
               "latest_confirmed_amendment_resolution_ar":
                   src.get("latest_confirmed_amendment_resolution_ar"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "pending_draft_amendments": src.get("pending_draft_amendments", []),
               "chapter_structure": src.get("chapter_structure", []),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-chambers-of-commerce-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية "
                           "(63 مادة؛ 62 أصلية، 1 معدلة، 0 ملغاة، 0 مضافة)",
               "title_en": ("Implementing Regulation of the Chambers of Commerce Law — "
                            "Arabic LLM-ready layer (63 records: 62 original, 1 amended, "
                            "0 repealed, 0 added)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, N_ARTICLES], "text_status": STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "pending_draft_amendments_note": (
                   "A proposed amendment to Article 44 was under public consultation in "
                   "Jan 2025 but was NOT found adopted as of this pass; Article 44 here is "
                   "its original, unamended text. See pending_draft_amendments in the "
                   "verified_summary.json / source artifact."),
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Chambers of Commerce Regulation records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
