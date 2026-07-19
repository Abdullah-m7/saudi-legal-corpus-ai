#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Law of the Practice of Engineering Professions track
(نظام مزاولة المهن الهندسية, Royal Decree M/36, 19/4/1438H).

DISTINCT FROM saudi_engineers_law -- decree-number collision re-confirmed:
this law (Royal Decree م/36, 19/4/1438هـ, 2017G, 17 articles: licensing,
professional accreditation, and disciplinary penalties for individual
engineers/firms) is a SEPARATE instrument from this corpus's already-ingested
saudi_engineers_law track (Royal Decree م/36, 26/9/1423هـ, 2002G, 9 articles:
the Saudi Council of Engineers' own organizing/governance statute). Both
happen to share the bare decree number "م/36" purely by numbering
coincidence -- an expected artifact of the Saudi royal-decree numbering
convention, re-confirmed here independently via BOE's own metadata for this
law's page. This law's own Article 1 defines "الهيئة" as "الهيئة السعودية
للمهندسين", i.e. it presupposes the OTHER track's Authority as an
already-existing body rather than repealing or replacing it. track_id
"engineering_practice_law" is used throughout (distinct from
"saudi_engineers_law") to avoid any registry-level naming collision.

VERIFICATION TIER -- see sources/engineering_practice/law/official_source/
engineering_practice_law_official_source.json's verification_methodology_note
for the full account. Summary:

PRIMARY SOURCE: laws.boe.gov.sa, fetched via THREE Wayback Machine snapshots
spanning 14 Nov 2019 - 25 Feb 2026 (live BOE portal unreachable this pass,
connection reset). All 17 "article_item" divs are present in every snapshot,
in the same order, no أبواب/فصول grouping. All 17 articles' main-body text is
BYTE-IDENTICAL across all three time-points; the only difference across
snapshots is that Article 1 gained a "changed-article" class and changelog
popup between the 2019 and 2022 snapshots.

SECOND SOURCE: the Saudi Council of Engineers' own official website
(saudieng.sa -- this law's own administering regulator, a genuinely separate
primary source, not a re-hosted BOE mirror), fetched via a Wayback snapshot
of its own hosted PDF copy (15 Jun 2025). Articles 2-17 match BOE's own text
WORD-FOR-WORD. Article 1 is the sole point of divergence (see below).

ARTICLE 1 -- A GENUINE THREE-WAY DISCREPANCY (handled per this corpus's
awqaf_law Article 6 precedent for a changelog "before"-phrase that does NOT
cleanly match the observed main body): BOE's own changelog quotes Council of
Ministers Resolution 250 (7/4/1444H) substituting "وزارة الشؤون البلدية
والقروية والإسكان" for "وزارة التجارة" -- but BOE's own main body has
consistently read "وزارة التجارة والاستثمار" (NOT the bare "وزارة التجارة"
the changelog quotes as its own "before" phrase) at every one of the three
checked snapshots, including the earliest (2019), predating the amendment by
~3 years. saudieng.sa's own current PDF shows a THIRD wording again ("وزارة
البلديات والإسكان"). No mechanical substitution is performed; this track
ingests BOE's own stable, consistently-displayed main-body text as Article
1's current "text" (legal_status_ar = معدلة, since BOE's own metadata
officially flags it as changed and independent evidence confirms a real
supervising-ministry transfer occurred in substance), and documents the full
three-way divergence in known_unresolved_discrepancies rather than fabricate
a resolution.

17 records: 16 اصلية, 1 معدلة (Article 1), 0 ملغاة, 0 مضافة. Flat structure,
no أبواب/فصول. No inline per-article titles in the BOE source -- no title_ar
field is used.

PREDECESSOR: no predecessor engineering-practice law was found; a full-text
search of this law's own archived HTML for repeal-language markers returned
zero matches anywhere in the preamble or all 17 articles -- a confirmed
negative finding, stronger than even saudi_engineers_law's own Article 9
general conflict-only repeal clause (this law has no repeal clause at all).

COMPANION INSTRUMENTS NOT INGESTED: اللائحة التنفيذية لنظام مزاولة المهن
الهندسية (this law's own Implementing Regulation, Article 16), ميثاق
المهندس (the Engineer's Charter, referenced in Articles 1 and 6), and لائحة
الوظائف الهندسية (the Engineering Positions/Jobs Regulation referenced in
this law's own ratifying Council of Ministers Resolution) were all
identified but NOT ingested this pass (one-law-per-pass precedent) -- see
known_unresolved_discrepancies.

No legal text is altered beyond whitespace normalization (collapsing
incidental double-space/tab artifacts from adjacent inline-element
rendering). Arabic governs; no translation/paraphrase/interpretation.
Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "engineering_practice", "law", "official_source",
                   "engineering_practice_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "engineering_practice", "law", "verified")
RECORDS = os.path.join(OUT_VER, "engineering_practice_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "engineering_practice_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "engineering_practice_arabic_legal_llm",
                        "engineering_practice_law_legal_llm_001_017.json")

LAW_ID = "sa-engineering-practice-law-m36-1438"
LAW_AR = "نظام مزاولة المهن الهندسية"
TOP_STATUS_ORIGINAL = ("BOE_WAYBACK_THREE_TIMEPOINT_NOV2019_NOV2022_FEB2026_TEXT_STABLE_X_"
                       "SAUDIENG_SA_OFFICIAL_PDF_WAYBACK_JUN2025_WORDFORWORD_MATCH_X_"
                       "QANOONSA_QANONIAH_CROSSCHECK_LIVE_BOE_UNREACHABLE")
TOP_STATUS_ART1 = ("BOE_CHANGELOG_COM_RESOLUTION_250_1444H_QUOTED_BUT_BEFORE_PHRASE_"
                   "MISMATCH_X_MAIN_BODY_STABLE_STALE_INGESTED_X_SAUDIENG_SA_OFFICIAL_"
                   "PDF_THIRD_DIVERGENT_WORDING_UNRESOLVED_THREE_WAY_LIVE_BOE_UNREACHABLE")
KEY_RE = r"engineering_practice_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = {"engineering_practice_art_001"}
ADDED_KEYS = set()
REPEALED_KEYS = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك الهيئة المجلس الوزارة الوزير").split())


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
        top_status = TOP_STATUS_ART1 if key in AMENDED_KEYS else TOP_STATUS_ORIGINAL
        ver.append({"law_key": "engineering_practice", "law_component": "law",
                    "language": "ar",
                    "record_layer": "ENGINEERING_PRACTICE_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": top_status,
                    "governing_source_note": ("Arabic governs; this track rests on THREE "
                                              "independently-fetched BOE-via-Wayback-Machine "
                                              "archived snapshots spanning 14 Nov 2019 - 25 Feb "
                                              "2026 as the PRIMARY source (live BOE unreachable "
                                              "this pass, connection reset), cross-verified "
                                              "against the Saudi Council of Engineers' own "
                                              "official website (saudieng.sa, its own hosted PDF "
                                              "of this law, Wayback snapshot 15 Jun 2025) for "
                                              "Articles 2-17 word-for-word. Article 1 is معدلة: "
                                              "BOE's own changelog quotes Council of Ministers "
                                              "Resolution 250 (7/4/1444H) but its own quoted "
                                              "'before' phrase does not match BOE's own stable "
                                              "main-body text, and saudieng.sa's own current PDF "
                                              "shows a THIRD, again-different wording -- this "
                                              "record carries BOE's own stable, consistently-"
                                              "displayed main-body text rather than fabricate a "
                                              "resolution across the three non-reconciling "
                                              "wordings. See verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track's Article 1 "
                                              "text as definitively naming the current supervising "
                                              "ministry."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "engineering-practice-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "engineering_practice/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام مزاولة المهن الهندسية" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree M/36 (19/4/1438H) — "
                                                          "laws.boe.gov.sa via three Wayback "
                                                          "Machine snapshots (2019-2026), "
                                                          "cross-verified against the Saudi "
                                                          "Council of Engineers' own official "
                                                          "website (saudieng.sa); live BOE "
                                                          "unreachable this pass"),
                                     "source_authority_ar": "المرسوم الملكي رقم (م/36) وتاريخ 19/4/1438هـ — ثلاث لقطات أرشيفية من بوابة هيئة الخبراء عبر Wayback Machine (2019-2026)، مطابقة مع الموقع الرسمي للهيئة السعودية للمهندسين (saudieng.sa)",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "engineering_practice",
               "layer": "ENGINEERING_PRACTICE_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-engineering-practice-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (17 مادة؛ 16 أصلية ومادة واحدة معدلة)",
               "title_en": "Law of the Practice of Engineering Professions — Arabic LLM-ready layer (17 records: 16 original, 1 amended)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 17], "text_status": TOP_STATUS_ORIGINAL,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Engineering Practice Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
