#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Premium Residency Regulation track (اللائحة التنفيذية لنظام
الإقامة المميزة) -- the implementing regulation of this corpus's already-
ingested premium_residency track (نظام الإقامة المميزة, Royal Decree M/106,
10/9/1440H). Originally issued by the Premium Residency Center's own Decision
No. (4-1440) dated 20/9/1440H, comprehensively amended by the Center's Board
of Directors Decision No. (7-5-1444) dated 29/12/1444H.

VERIFICATION TIER -- see sources/premium_residency_regulation/law/
official_source/premium_residency_regulation_official_source.json's
verification_methodology_note and known_unresolved_discrepancies for the full
account. Summary: ncar.gov.sa, laws.boe.gov.sa, and pr.gov.sa (the Center's
own official portal) were all UNREACHABLE this pass despite independent
attempts (direct curl, WebFetch/proxy, r.jina.ai reader-proxy, Wayback CDX
lookups). This track instead rests entirely on two independent commercial/
private secondary sources: qanoniah.com (a Saudi legal database, verbatim
text for Articles 1-5 of both the current 1444H-amended and original 1440H
editions, subscription-gated beyond 10 free items) and aunklaw.com (a law
firm's public blog, verbatim text for all 13 current articles). Articles 1-5
carry genuine cross-verification (word-for-word match across both sources,
including section sub-headers); Articles 6-13 rest on aunklaw.com alone.
Because 8 of 13 articles (~62%) are single-secondary-sourced with zero
official corroboration, this track is classified TIER_4_SINGLE_SOURCE_OR_
MIXED_CONFIDENCE overall per this corpus's own methodology (reports/
verification_tiers/VERIFICATION_TIERS_METHODOLOGY_AR.md), which calls for
grading a mixed-confidence track by its WEAKEST part, not its strongest.

13 articles, no أبواب/فصول (flat structure per both sources' own rendering;
chapter_structure below is an informal thematic grouping for indexing only,
taken verbatim from the actual sub-headers appearing in both sources). Status:
1 اصلية (Article 7, confirmed byte-for-byte identical to the original 1440H
text), 12 معدلة (Articles 1-6 and 8-9 confirmed changed by direct text
comparison against the original 1440H edition also partially recovered this
pass; Articles 10-13 classified معدلة by reasonable inference -- the whole
document was reissued under a single Board Decision, and the one directly-
confirmed data point available for this range shows content relocation, not
mere renumbering -- NOT by direct original-text comparison, which the
qanoniah.com paywall prevented for this range; disclosed explicitly, not
silently assumed). 0 ملغاة, 0 مضافة.

GENUINE ANOMALIES carried forward, disclosed not silently resolved: (a)
Article 3's product-list wording differs between qanoniah.com ("دائمة", citing
TWO Council of Economic and Development Affairs decisions) and aunklaw.com
("غير محددة المدة", citing only ONE, older decision) -- qanoniah's more
complete/current version is adopted as governing text for this article; (b)
Article 6's fee table (sourced from aunklaw.com only, since qanoniah paywalled
this article) still uses the OLDER "غير محدد المدة" product name, a direct,
disclosed seam from combining two different platforms for different articles
of the very same document; (c) Article 8 of the regulation cross-references
"المادة (الثامنة) من النظام" for content that substantively matches the LAW's
Article 9 (revocation grounds), not its Article 8 (the tax-residency clause,
fully repealed by Royal Decree M/84, 1445H, per the premium_residency track) --
preserved verbatim as found, not corrected or interpreted.

No legal wording is altered beyond whitespace/typographic normalization
(stray ZWNJ characters, curly quotes to Arabic guillemets, en-dash to hyphen,
HTML-table flattening to plain text). Arabic governs; no translation/
paraphrase/interpretation performed on the Arabic text. Read-only over input;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "premium_residency_regulation", "law", "official_source",
                   "premium_residency_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "premium_residency_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "premium_residency_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "premium_residency_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "premium_residency_regulation_arabic_legal_llm",
                        "premium_residency_regulation_legal_llm_001_013.json")

LAW_ID = "sa-premium-residency-regulation-center-decision-7-5-1444"
LAW_AR = "اللائحة التنفيذية لنظام الإقامة المميزة"
KEY_RE = r"premium_residency_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
AMENDED_KEYS = {"premium_residency_regulation_art_%03d" % n
                for n in (1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13)}
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك الإقامة المميزة حامل غير السعودي "
            "الفقرة هذه المركز المتقدم").split())


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
        ver.append({"law_key": "premium_residency_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "PREMIUM_RESIDENCY_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": a["status"],
                    "governing_source_note": ("Arabic governs; ncar.gov.sa, laws.boe.gov.sa, and "
                                              "pr.gov.sa (the Center's own portal) were all "
                                              "unreachable this pass -- this track rests on two "
                                              "independent secondary sources (qanoniah.com, "
                                              "aunklaw.com), cross-verified word-for-word for "
                                              "Articles 1-5 only; Articles 6-13 rest on "
                                              "aunklaw.com alone. See verification_methodology_"
                                              "note and known_unresolved_discrepancies in the "
                                              "source artifact before relying on this track for "
                                              "any single article's definitively-current wording."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "premium-residency-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "premium_residency_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام الإقامة المميزة" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Premium Residency Center Board "
                                                          "Decision No. 7-5-1444 (29/12/1444H) "
                                                          "-- official ncar.gov.sa/BOE/pr.gov.sa "
                                                          "portals unreachable this pass; sourced "
                                                          "from qanoniah.com (Articles 1-5, cross-"
                                                          "verified) and aunklaw.com (Articles "
                                                          "1-13, sole source for Articles 6-13)"),
                                     "source_authority_ar": "قرار مجلس إدارة مركز الإقامة المميزة رقم (7-5-1444) وتاريخ 29/12/1444هـ — بوابات ncar.gov.sa وBOE وpr.gov.sa الرسمية غير متاحة هذه الجولة؛ اعتُمد على qanoniah.com (المواد 1-5، تحقق مزدوج) وaunklaw.com (المواد 1-13، المصدر الوحيد للمواد 6-13)",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "premium_residency_regulation",
               "layer": "PREMIUM_RESIDENCY_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "founding_decree": src.get("founding_decree"),
               "founding_decree_date_hijri": src.get("founding_decree_date_hijri"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-premium-residency-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (13 مادة؛ مادة أصلية واحدة و12 مادة معدلة)",
               "title_en": ("Implementing Regulation of the Premium Residency Law — Arabic "
                            "LLM-ready layer (13 ingested records: 1 original, 12 amended)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 13], "text_status": "TIER_4_SINGLE_SOURCE_OR_MIXED_CONFIDENCE",
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Premium Residency Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
