#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Law of the Saudi Council of Engineers track
(نظام الهيئة السعودية للمهندسين, Royal Decree M/36, 26/9/1423H).

VERIFICATION TIER -- see sources/saudi_engineers/law/official_source/
saudi_engineers_law_official_source.json's verification_methodology_note for
the full account. Summary:

PRIMARY SOURCE: laws.boe.gov.sa, fetched via THREE Wayback Machine snapshots
spanning 15 Nov 2019 - 15 Sep 2025 because the live BOE portal was
unreachable this pass (HTTP 503). All 9 'article_item' divs are present in
every snapshot, in the same order, no أبواب/فصول grouping. Only two articles
(1 and 6) ever carry BOE's own 'changed-article' class plus a 'تعديلات
المادة' changelog popup; the other 7 are textually identical across all
three time-points. Independently cross-checked against the Saudi Council of
Engineers' own official website (saudieng.sa), fetched via THREE of its own
Wayback snapshots spanning 3 Nov 2017 - 30 Nov 2022.

TWO ARTICLES WITH CONFIRMED AMENDMENTS, BOTH CLEAN:
  - Article 1 (supervising government entity): a single, clean phrase-
    substitution instruction (Council of Ministers Resolution 57, 20/1/1442H,
    replacing "تعمل تحت إشراف وزارة التجارة" with a TBD-by-future-PM-order
    supervising-entity clause) -- BOE's own main body AND saudieng.sa's own
    site are both stale (still show the pre-amendment wording even years
    later), so this track ingests the changelog-instructed substitution,
    following this corpus's accounting_auditing_law/awqaf_law precedent for
    stale-main-body-vs-changelog-popup patterns.
  - Article 6 (board composition): TWO layered but EACH fully self-
    contained, complete quoted replacement texts (Royal Decree M/60,
    28/12/1425H, then Council of Ministers Resolution 388, 14/7/1443H,
    which fully supersedes M/60's own text) -- unlike awqaf_law's Article 6
    problem, no internal inconsistency was found between the layers. This
    track ingests Resolution 388's complete quoted text as Article 6's
    current wording, independently corroborated by saudieng.sa's own site
    (which shows this exact text from its 17 May 2022 snapshot onward).

9 records: 7 اصلية, 2 معدلة (Articles 1, 6), 0 ملغاة, 0 مضافة. Flat
structure, no أبواب/فصول. No inline per-article titles in the BOE source --
no title_ar field is used.

PREDECESSOR: no pre-2002 predecessor engineering-council law was found; this
law's own Article 9 contains only a general conflict-only repeal clause,
naming no specific prior instrument -- a confirmed negative finding.

COMPANION LAW NOT INGESTED: a separate, currently-in-force law, نظام
مزاولة المهن الهندسية (Law of the Practice of Engineering Professions,
Royal Decree M/36, 19/4/1438H -- a DIFFERENT decree despite the identical
number) governs licensing/accreditation and disciplinary penalties for
individual engineers; it presupposes this Authority as an existing body
rather than repealing/replacing it. Not ingested this pass (one-law-per-
pass precedent) -- see known_unresolved_discrepancies.

No legal text is altered beyond whitespace normalization (collapsing
incidental double-spaces; normalizing immaterial tashkeel/diacritic-
ordering artifacts) and, for Articles 1 and 6 only, substituting BOE's own
quoted/instructed changelog replacement text for their stale main bodies.
Arabic governs; no translation/paraphrase/interpretation. Read-only over
input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "saudi_engineers", "law", "official_source",
                   "saudi_engineers_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "saudi_engineers", "law", "verified")
RECORDS = os.path.join(OUT_VER, "saudi_engineers_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "saudi_engineers_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "saudi_engineers_arabic_legal_llm",
                        "saudi_engineers_law_legal_llm_001_009.json")

LAW_ID = "sa-saudi-engineers-law-m36-1423"
LAW_AR = "نظام الهيئة السعودية للمهندسين"
TOP_STATUS = ("MIXED_TIER_SEE_PER_ARTICLE_STATUS_BOE_WAYBACK_THREE_TIMEPOINT_PRIMARY_X_"
              "SAUDIENG_SA_OFFICIAL_SITE_WAYBACK_THREE_TIMEPOINT_X_AAWSAT_PRESS_CROSSCHECK_"
              "LIVE_BOE_UNREACHABLE")
KEY_RE = r"saudi_engineers_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = {"saudi_engineers_art_001", "saudi_engineers_art_006"}
ADDED_KEYS = set()
REPEALED_KEYS = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك الهيئة المجلس الرئيس").split())


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
        ver.append({"law_key": "saudi_engineers", "law_component": "law",
                    "language": "ar",
                    "record_layer": "SAUDI_ENGINEERS_LAW_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; this track rests on THREE "
                                              "independently-fetched BOE-via-Wayback-Machine "
                                              "archived snapshots spanning 15 Nov 2019 - 15 Sep "
                                              "2025 as the PRIMARY source (live BOE unreachable "
                                              "this pass, HTTP 503), cross-verified against THREE "
                                              "of the Saudi Council of Engineers' own official "
                                              "website (saudieng.sa) Wayback snapshots spanning "
                                              "3 Nov 2017 - 30 Nov 2022, and against a WebSearch/"
                                              "press aggregation (Asharq Al-Awsat) for Article 1's "
                                              "supervising-authority transfer. Article 1 is "
                                              "معدلة: BOE's own main body text is STALE (still "
                                              "shows Ministry-of-Commerce supervision); this "
                                              "record instead carries BOE's own changelog-"
                                              "instructed substitution (Council of Ministers "
                                              "Resolution 57, 20/1/1442H). Article 6 is also "
                                              "معدلة (two confirmed, layered, but individually "
                                              "clean and complete amendments); this record carries "
                                              "the MOST RECENT complete quoted text (Council of "
                                              "Ministers Resolution 388, 14/7/1443H), independently "
                                              "confirmed by saudieng.sa's own site. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track's text as "
                                              "necessarily reflecting BOE's own live rendering."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "saudi-engineers-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "saudi_engineers/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام الهيئة السعودية للمهندسين" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree M/36 (26/9/1423H) — "
                                                          "laws.boe.gov.sa via three Wayback "
                                                          "Machine snapshots (2019-2025), "
                                                          "cross-verified against the Saudi "
                                                          "Council of Engineers' own official "
                                                          "website (saudieng.sa); live BOE "
                                                          "unreachable this pass"),
                                     "source_authority_ar": "المرسوم الملكي رقم (م/36) وتاريخ 26/9/1423هـ — ثلاث لقطات أرشيفية من بوابة هيئة الخبراء عبر Wayback Machine (2019-2025)، مطابقة مع الموقع الرسمي للهيئة السعودية للمهندسين (saudieng.sa)",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "saudi_engineers",
               "layer": "SAUDI_ENGINEERS_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-saudi-engineers-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (9 مواد؛ 7 أصلية و2 معدلة)",
               "title_en": "Law of the Saudi Council of Engineers — Arabic LLM-ready layer (9 records: 7 original, 2 amended)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 9], "text_status": TOP_STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Saudi Engineers Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
