#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Statute (Organizational Regulation) of the Education and
Training Evaluation Commission track (تنظيم هيئة تقويم التعليم والتدريب,
Council of Ministers Resolution No. 108, 14/2/1440H, amended by Resolution
No. 693, 2/11/1441H (Art. 7) and Resolution No. 631, 3/8/1445H (Art. 4)).

VERIFICATION TIER -- see sources/etec/law/official_source/
etec_law_official_source.json's verification_methodology_note for the full
account. Summary:

PRIMARY SOURCE: laws.boe.gov.sa's own law-detail page for this exact statute
IS catalogued (lawId c7a054a8-6dbc-4323-9405-aa3f00bd5985), but the LIVE
portal was unreachable this pass (direct curl: "Connection reset by peer";
WebFetch: HTTP 503). This track instead rests on TWO INDEPENDENT Wayback
Machine snapshots of that SAME official BOE page, taken ~18 months apart
(19 June 2024 and 12 December 2025), fetched and parsed this pass. Both
snapshots produced a FULL LITERAL MATCH: identical 18-article count,
identical per-article text, identical amended/unamended classification (the
portal's own "changed-article" CSS class on exactly Article 4 and Article
7 in both snapshots), and identical text inside both embedded
"تعديلات المادة" amendment-note popups. Per this corpus's own documented
methodology (reports/verification_tiers/VERIFICATION_TIERS_METHODOLOGY_AR.md
section 5), this exact pattern -- the official BOE portal via two
independent temporal snapshots in full agreement, with no reliance on any
private/secondary source for the primary text -- is treated as
TIER_1_PRIMARY_MULTI_SOURCE. This track is assessed at that tier.

STRUCTURAL NOTE: this pass's task brief flagged a caveat that this
instrument might be فقرة/clause-structured rather than مادة-structured (by
analogy to cybersecurity_authority_law). This turned out NOT to be the
case -- the primary source confirms a standard flat sequence of 18
individually-numbered مواد, no أبواب/فصول, no inline per-article titles.

18 records: 16 اصلية, 2 معدلة (Articles 4 and 7), 0 ملغاة, 0 مضافة.
Article 4 paragraph (5) amended by Resolution 631 (3/8/1445H) -- confirmed
identical to the prior-pass lead. Article 7 paragraph (1) amended by
Resolution 693 (2/11/1441H) -- a SECOND amendment, not in the prior lead,
discovered independently this pass directly from the primary source.

CONFIRMED NEGATIVE FINDING: none of the 18 articles (including the final
Article 18, a bare publication/effective-date clause with no repeal
language at all) contains any explicit repeal/replacement clause naming a
prior instrument. The preamble recitals mention, as background only,
Council of Ministers Resolution No. 94 (7/2/1438H)'s prior organizational
arrangements. A textually separate, older, NOT-ingested instrument (Council
of Ministers Resolution No. 120, 22/4/1434H, "تنظيم هيئة تقويم التعليم
العام", a different BOE lawId) was found via independent WebSearch and was
still listed "ساري" (in force) on BOE's own portal as of a June 2025
Wayback snapshot -- an unresolved status ambiguity for that OTHER
instrument, flagged but not resolved here. See known_unresolved_discrepancies
for the full account of both findings.

No legal text is altered beyond whitespace/line-break normalization and
stripping of the source portal's own decorative HTML markup. Arabic
governs; no translation/paraphrase/interpretation performed. Read-only over
input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "etec", "law", "official_source",
                   "etec_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "etec", "law", "verified")
RECORDS = os.path.join(OUT_VER, "etec_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "etec_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "etec_arabic_legal_llm",
                        "etec_law_legal_llm_001_018.json")

LAW_ID = "sa-etec-law-108-1440"
LAW_AR = "تنظيم هيئة تقويم التعليم والتدريب"
TOP_STATUS = ("BOE_PORTAL_TWO_INDEPENDENT_WAYBACK_SNAPSHOTS_LITERAL_MATCH_TIER1_"
              "X_NEZAMS_PARTIAL_CROSSCHECK_LIVE_PORTAL_503")
KEY_RE = r"etec_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = {"etec_art_004", "etec_art_007"}
ADDED_KEYS = set()
REPEALED_KEYS = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك الهيئة المجلس الرئيس المراكز").split())


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
        ver.append({"law_key": "etec", "law_component": "law",
                    "language": "ar",
                    "record_layer": "ETEC_LAW_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; this track rests on the official "
                                              "laws.boe.gov.sa portal itself, accessed via TWO "
                                              "INDEPENDENT Wayback Machine snapshots (19 June 2024 "
                                              "and 12 December 2025) after the live portal returned "
                                              "HTTP 503/connection-reset this pass, with a full "
                                              "literal match across all 18 articles and both "
                                              "embedded amendment-note popups (Articles 4 and 7) -- "
                                              "TIER_1 per this corpus's own methodology for this "
                                              "exact double-snapshot pattern. Supplementary partial "
                                              "cross-check from nezams.com (Article 1 text and the "
                                              "Resolution 631/Article 4 amendment note). See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact for the full account, including a "
                                              "confirmed-negative predecessor-repeal finding and a "
                                              "second amendment (Resolution 693, Article 7) not in "
                                              "this pass's original lead."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "etec-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "etec/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من تنظيم هيئة تقويم التعليم والتدريب" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Council of Ministers Resolution 108 "
                                                          "(amended by Resolutions 693 and 631) — "
                                                          "official laws.boe.gov.sa portal, "
                                                          "accessed via two independent Wayback "
                                                          "Machine snapshots in full literal "
                                                          "agreement, TIER_1; supplementary partial "
                                                          "cross-check from nezams.com"),
                                     "source_authority_ar": "قرار مجلس الوزراء رقم (108) (المعدل بقراري مجلس الوزراء رقم 693 و631) — بوابة laws.boe.gov.sa الرسمية، تم الوصول إليها عبر لقطتين أرشيفيتين مستقلتين من Wayback Machine متطابقتين حرفياً، المستوى الأول؛ تدقيق ثانوي جزئي تكميلي من nezams.com",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "etec",
               "layer": "ETEC_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-etec-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (18 مادة، 16 أصلية و2 معدلة، بلا تقسيم إلى أبواب)",
               "title_en": "Statute (Organizational Regulation) of the Education and Training Evaluation Commission — Arabic LLM-ready layer (18 records, 16 original, 2 amended)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 18], "text_status": TOP_STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready ETEC Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
