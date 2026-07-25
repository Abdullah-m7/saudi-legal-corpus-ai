#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Electronic Transactions Law
track (اللائحة التنفيذية لنظام التعاملات الإلكترونية), Board of Directors
Decision of the Digital Government Authority (DGA) No. (M-8-6), dated
3 Ramadan 1445H (13 March 2024).

BASE LAW: نظام التعاملات الإلكترونية (Royal Decree M/18, 8/3/1428H) is
already tracked in this corpus at sources/electronic_transactions/. That law
was amended by Council of Ministers Resolution No. 293 (9 Rabi' al-Thani
1445H / 24 October 2023), which substituted the Digital Government Authority
(DGA) for the Communications and Information Technology Commission (CITC) as
the body administering the law AND its implementing regulation. THIS
regulation (M-8-6) is the implementing regulation DGA issued, under its own
Board, following that substitution -- it is a freshly-promulgated, whole
regulation (25 articles, all اصلية), not a partial in-place amendment of a
prior regulation's text. It supersedes in practice (though without an
explicit repeal clause found in its own text) an earlier 1429H (~2008)
implementing regulation issued under CITC/the Ministry -- see
known_unresolved_discrepancies.

PRIMARY SOURCE: the Official Umm al-Qura Gazette (uqn.gov.sa/details?p=25092),
fetched directly via curl (HTTP 200) -- this pass the page's server-rendered
HTML included the FULL article body inside <article id="article-content">
(unlike this corpus's prior einvoicing_regulation-track experience with the
same domain, where it appeared as an unrendered Vue.js/SPA shell). 25
articles across 8 chapters extracted cleanly (no ligature corruption, no
decorative tatweel, no stray Latin/HTML characters -- verified
programmatically). dga.gov.sa (the issuing authority's own site, both
language versions, and its node/1808 "amendments" project page) was blocked
by Cloudflare (HTTP 403) via direct curl, WebFetch, and r.jina.ai (which
additionally rate-limited this session's IP to HTTP 401 "bad IP reputation").
laws.boe.gov.sa was unreachable (connection reset). The Wayback Machine's
CDX/availability API confirmed a historical snapshot of the DGA English page
exists, but the content-serving path (web.archive.org/web/...) was blocked by
this environment's egress policy for both curl and WebFetch.

CROSS-CHECK: argaam.com (an independent financial-news outlet, unaffiliated
with government) published an article the same week as the Gazette,
verbatim-quoting several full paragraphs -- spot-checked word-for-word
against Article 5 and Article 22 as extracted from uqn.gov.sa: exact match,
including the decision date spelled out in words ("03 رمضان 1445هـ").

DATE RESOLUTION (disclosed, not silently picked): several secondary
paraphrase sources (including outside research prior to this pass) render
the Board Decision's date as "9/3/1445H" (9 Rabi' al-Awwal, 24 September
2023). Two independent sources that spell the month out in words -- the
Official Gazette itself and argaam.com -- both instead give "3 Ramadan
1445H" (13 March 2024), which is also the only reading chronologically
consistent with this regulation being issued "based on"/pursuant to Council
of Ministers Resolution 293 (9 Rabi' al-Thani 1445H / 24 October 2023,
already verified in the base law's own track) -- Ramadan (month 9) follows
Rabi' al-Thani (month 4) within 1445H, whereas Rabi' al-Awwal (month 3) would
precede it. This track adopts 3 Ramadan 1445H and flags the "9/3" figure as
an unresolved discrepancy in secondary paraphrase sources.

TIER: TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED (one official/primary source
reached and adopted as governing text -- the Official Gazette -- with no
second independent GOVERNMENT source confirming wording, since both DGA's
own site and BOE were unreachable; cross-verified word-for-word against an
independent press source for two full articles).

See sources/electronic_transactions_regulation/law/official_source/
electronic_transactions_regulation_official_source.json for the full
methodology note and all documented unresolved discrepancies (predecessor
1429H regulation not ingested, decision-vs-publication date distinction,
Gazette issue number inferred, irregular paragraph-numbering spacing
preserved verbatim, diacritics preserved verbatim per the base law's own
convention, etc.).

25 articles, ALL اصلية (0 معدلة, 0 مضافة, 0 ملغاة), organized under 8
chapters, no مكرر. No legal text is altered. Arabic governs; no translation/
paraphrase/interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "electronic_transactions_regulation", "law", "official_source",
                   "electronic_transactions_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "electronic_transactions_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "electronic_transactions_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "electronic_transactions_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "electronic_transactions_regulation_arabic_legal_llm",
                        "electronic_transactions_regulation_legal_llm_001_025.json")

LAW_ID = "sa-electronic-transactions-regulation-m8-6-1445h"
LAW_AR = "اللائحة التنفيذية لنظام التعاملات الإلكترونية"
STATUS = "UQN_GAZETTE_OFFICIAL_PRIMARY_X_ARGAAM_PRESS_CROSSCHECK_DGA_BOE_UNREACHABLE"
TIER = "TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED"
KEY_RE = r"electronic_transactions_regulation_art_(\d{3})$"
AMENDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك الهيئة المرخص").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def _sort_key(key):
    return int(re.match(KEY_RE, key).group(1))


GOV_NOTE = ("Arabic governs; primary source is the Official Umm al-Qura Gazette "
            "(uqn.gov.sa/details?p=25092), fetched directly (HTTP 200), server-rendered full "
            "text, 25 articles across 8 chapters. dga.gov.sa (issuing authority) and "
            "laws.boe.gov.sa were both unreachable this pass -> TIER_2. Cross-checked "
            "word-for-word for two full articles against an independent press source "
            "(argaam.com). See verification_methodology_note and known_unresolved_discrepancies "
            "in the source artifact (including a resolved Board-Decision-date transposition, "
            "the un-ingested 1429H predecessor regulation, and the decision-vs-publication date "
            "distinction) before relying on this track's text or provenance.")

SRC_AUTH = ("Implementing Regulation of the Electronic Transactions Law, issued by the Digital "
            "Government Authority (DGA) Board of Directors Decision No. (M-8-6), dated 3 Ramadan "
            "1445H (13 March 2024). Full text from the Official Umm al-Qura Gazette "
            "(uqn.gov.sa), cross-checked word-for-word against an independent press source "
            "(argaam.com) -> TIER_2. 25 articles, all اصلية.")

SRC_AUTH_AR = ("اللائحة التنفيذية لنظام التعاملات الإلكترونية، الصادرة بقرار مجلس إدارة هيئة "
               "الحكومة الرقمية رقم (م-8-6) وتاريخ 3 رمضان 1445هـ. النص الكامل من جريدة أم "
               "القرى الرسمية (uqn.gov.sa)، مطابق حرفياً لمصدر صحفي مستقل (argaam.com) -- "
               "TIER_2. 25 مادة، جميعها أصلية.")


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for key in keys:
        a = arts[key]
        n = int(re.match(KEY_RE, key).group(1))
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        is_repealed = ls == "ملغاة"
        is_added = ls == "مضافة"
        text = a["text"]
        ver.append({"law_key": "electronic_transactions_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "ELECTRONIC_TRANSACTIONS_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "verification_tier": a.get("verification_tier"),
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": GOV_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "electronic-transactions-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "electronic_transactions_regulation/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d من اللائحة التنفيذية لنظام التعاملات الإلكترونية"
                                          % n],
                    "text_status": STATUS, "verification_tier": a.get("verification_tier"),
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
    json.dump({"law_key": "electronic_transactions_regulation",
               "layer": "ELECTRONIC_TRANSACTIONS_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "verification_tier": TIER,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "base_law": src.get("base_law"),
               "gazette_publication_hijri": src.get("gazette_publication_hijri"),
               "gazette_publication_gregorian": src.get("gazette_publication_gregorian"),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-electronic-transactions-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (25 مادة، جميعها أصلية)",
               "title_en": ("Implementing Regulation of the Electronic Transactions Law — "
                            "Arabic LLM-ready layer (25 records, all اصلية)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 25], "text_status": STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Electronic Transactions Regulation records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
