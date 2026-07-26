#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Law of Enforcement before the Board of Grievances track
(نظام التنفيذ أمام ديوان المظالم, Royal Decree M/15, 27/1/1443H).

VERIFICATION TIER -- see sources/bog_enforcement_law/law/official_source/
bog_enforcement_law_official_source.json's verification_methodology_note for
the full account. Summary:

PRIMARY SOURCE ACCESS: laws.boe.gov.sa's LIVE portal was unreachable this
pass (HTTP 503 on two separate attempts to the LawDetails/Viewer/
SearchDetails variants of this exact law ID). archive.org/wayback/available
confirmed exactly ONE Wayback Machine snapshot exists (20260215011202), but
this sandbox's egress policy blocks fetching actual web.archive.org page
CONTENT this pass (only the metadata-only availability lookup succeeded).

PRIMARY FULL-TEXT SOURCE USED: nezams.com (a Saudi legal-database
aggregator), fetched by direct curl and parsed programmatically from its 37
<li class="subject"> blocks. This is a SINGLE-AGGREGATOR tier, materially
lower than this corpus's BOE-Wayback-based tracks (e.g. nazaha) -- see
known_unresolved_discrepancies key bog_enforcement_single_aggregator_tier.

Partial cross-verification obtained: Article 37 confirmed fully verbatim via
an independent WebSearch snippet; the overall chapter/topic structure
confirmed independently via BOE's own SearchDetails summary; official
decree/gazette metadata (م/15, 27/1/1443هـ; CoM Resolution 73, 23/1/1443هـ;
gazette date 3/2/1443هـ) confirmed via the Umm Al-Qura gazette detail page;
~20 of 37 articles' substance spot-checked without contradiction via
muhamapp.com (a legal-explainer blog).

37 records: all اصلية (0 معدلة, 0 ملغاة, 0 مضافة). Five أبواب: أحكام عامة
(1-5), إجراءات التنفيذ (6-24, split into four فصول: 6-9, 10-15, 16-19,
20-24), منازعات التنفيذ والدعاوى الناشئة عنه (25-29), الجرائم والعقوبات
(30-33), أحكام ختامية (34-37).

SOURCE-TYPO CORRECTION (disclosed): nezams.com's own heading for Article 35
read "المادة الخامسة الثلاثون" (missing و), inconsistent with every other
similarly-formed ordinal in this law and contradicted by an independent
WebSearch snippet; corrected to "المادة الخامسة والثلاثون" here -- a
heading-typo fix only, not a legal-text change. See
known_unresolved_discrepancies key bog_enforcement_art035_label_typo_corrected.

CRITICAL DISTINCTNESS FINDING (confirmed, not a duplicate): this law is
genuinely distinct from this corpus's already-ingested enforcement_law track
(نظام التنفيذ, M/53, 13/8/1433هـ, 98 articles, ordinary judiciary). M/15's own
enacting decree clause ثالثاً explicitly carves out an exception from clause
ثانياً of M/53's enacting decree; M/15 Arts. 18/36 cross-reference M/53 as a
residual fallback. Two genuinely different, complementary statutes. See
known_unresolved_discrepancies key
bog_enforcement_distinctness_confirmed_not_duplicate.

UNRELATED SIDE-FINDING (out of scope, flagged for awareness only): a brand
new ordinary نظام التنفيذ (65 articles, CoM Resolution 746, published Umm
Al-Qura 1 May 2026, effective ~28 Oct 2026 -- not yet in force) will
eventually replace M/53 (this corpus's existing enforcement_law track). Not
investigated further here. See known_unresolved_discrepancies key
bog_enforcement_crossref_new_ordinary_enforcement_law_2026.

No legal text is altered beyond whitespace/line-break normalization and the
single disclosed Article-35 heading-typo correction above. Arabic governs;
no translation/paraphrase/interpretation. Read-only over input; deterministic
over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "bog_enforcement_law", "law", "official_source",
                   "bog_enforcement_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "bog_enforcement_law", "law", "verified")
RECORDS = os.path.join(OUT_VER, "bog_enforcement_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "bog_enforcement_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "bog_enforcement_law_arabic_legal_llm",
                        "bog_enforcement_law_legal_llm_001_037.json")

LAW_ID = "sa-bog-enforcement-law-m15-1443"
LAW_AR = "نظام التنفيذ أمام ديوان المظالم"
TOP_STATUS = ("NEZAMS_FULLTEXT_SINGLE_AGGREGATOR_X_UQN_GAZETTE_DECREE_METADATA_X_"
              "WEBSEARCH_PARTIAL_VERBATIM_CROSSCHECK_X_MUHAMAPP_STRUCTURAL_PARTIAL_"
              "LIVE_BOE_UNREACHABLE_WAYBACK_CONTENT_BLOCKED_BY_SANDBOX_EGRESS")
KEY_RE = r"bog_tnf_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = set()
ADDED_KEYS = set()
REPEALED_KEYS = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك المجلس الدائرة المحكمة").split())


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
        ver.append({"law_key": "bog_enforcement_law", "law_component": "law",
                    "language": "ar",
                    "record_layer": "BOG_ENFORCEMENT_LAW_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; this track rests on nezams.com "
                                              "(a single secondary legal-database aggregator) as "
                                              "PRIMARY full text -- laws.boe.gov.sa's live portal "
                                              "returned HTTP 503 twice this pass, and this "
                                              "sandbox's egress policy blocked fetching actual "
                                              "Wayback Machine snapshot content (only the "
                                              "metadata-only availability lookup succeeded, "
                                              "confirming one snapshot exists at timestamp "
                                              "20260215011202). Partial cross-verification: "
                                              "Article 37 confirmed fully verbatim via an "
                                              "independent WebSearch snippet; chapter/topic "
                                              "structure confirmed via BOE's own SearchDetails "
                                              "summary; decree/gazette metadata confirmed via "
                                              "the Umm Al-Qura gazette detail page; ~20 of 37 "
                                              "articles spot-checked without contradiction via "
                                              "muhamapp.com. See verification_methodology_note "
                                              "and known_unresolved_discrepancies in the source "
                                              "artifact -- in particular the single-aggregator "
                                              "tier flag -- before relying on this track's text."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "bog-enforcement-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "bog_enforcement_law/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام التنفيذ أمام ديوان المظالم" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree M/15 — nezams.com "
                                                          "(single secondary legal-database "
                                                          "aggregator) as primary full text; "
                                                          "live BOE unreachable (HTTP 503) and "
                                                          "Wayback content blocked by sandbox "
                                                          "egress policy this pass; partial "
                                                          "cross-verification via Umm Al-Qura "
                                                          "gazette metadata, one article "
                                                          "(No. 37) confirmed verbatim via "
                                                          "independent WebSearch, and "
                                                          "muhamapp.com spot-checks"),
                                     "source_authority_ar": "مرسوم ملكي رقم (م/15) — nezams.com (مصدر ثانوي واحد)، مع تحقق جزئي عبر بوابة أم القرى وWebSearch وmuhamapp.com؛ بوابة هيئة الخبراء وأرشيف Wayback غير متاحين هذه الجولة",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "bog_enforcement_law",
               "layer": "BOG_ENFORCEMENT_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-bog-enforcement-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (37 مادة أصلية، خمسة أبواب)",
               "title_en": "Law of Enforcement before the Board of Grievances — Arabic LLM-ready layer (37 records, all original, unamended)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 37], "text_status": TOP_STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready BOG Enforcement Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
