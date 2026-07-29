#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Organizing Statute of the General Authority for Transport
(TGA) track (تنظيم هيئة النقل العام / الهيئة العامة للنقل, Council of
Ministers Resolution No. 323, 14/9/1434H, prepared pursuant to Resolution
373/1433H, amended by Resolutions 248/1437H, 707/1438H, 631/1440H, 12/1443H,
586/1444H, and 382-or-386/1446H).

VERIFICATION TIER -- see sources/tga_organizational_statute/law/
official_source/tga_organizational_statute_official_source.json's
verification_methodology_note for the full account. Summary:

PRIMARY SOURCE: laws.boe.gov.sa itself, reached via TWO Wayback Machine
snapshots of its own 'LawDetails' page (Id 9a1c4977-c539-4e01-8c88-
a9a700f2efa9, the exact Id in this track's brief) -- 16 Dec 2024 and 11 Jul
2025 (the most recent available), self-consistent on every article except
one additional Article-5 amendment-history entry the later snapshot alone
carries. laws.boe.gov.sa's LIVE portal returned a TLS connection reset on
every direct attempt this pass (confirmed via curl -v) and WebFetch returned
HTTP 503 -- consistent with this corpus's established BOE-live-unreachable
pattern; the Wayback Machine itself was fully reachable this pass.

CONFIRMED GAP #1: BOE's own page carries NO amendment-history popup at all
for Article 6, despite nezams.com stating Resolution 12 (2/1/1443H) amended
its paragraph 4. This was independently confirmed via a genuinely PRIMARY
channel: a Wayback capture of uqn.gov.sa's own Umm Al-Qura Gazette article
page reproducing the complete decree text verbatim -- a stronger footing
than a typical BOE-stale-gap case elsewhere in this corpus, since the gap
is filled by a second, genuinely different OFFICIAL source, not merely a
secondary aggregator.

CONFIRMED GAP #2: Article 5's most recent amendment (a Ministry-of-Energy
board seat, 17/5/1446H) carries an UNRESOLVED decree-number conflict --
BOE's own page says (382), qanoonsa.com's full-text reproduction of what is
otherwise clearly the same decree says (386) -- and neither source states
the RESULTING reordered text. This track does NOT fabricate a resulting
order: Article 5's ingested text is the last FULLY-QUOTED substitution
(Resolution 586, a 10-member board), with the Energy-Ministry amendment
recorded in history as confirmed-to-exist-but-not-textually-incorporated.

CONFIRMED GAP #3: Resolution 631 (6/11/1440H) instructed a statute-wide
'هيئة النقل العام' -> 'الهيئة العامة للنقل' rename and a 'النقل العام' ->
'النقل' phrase shortening "wherever it appears in this statute" -- neither
substitution appears executed in BOE's own displayed article text, even in
the 2025 snapshot (5+ years after the 2019 decree). This track does not
self-apply either substitution; it reports BOE's own text as-is and flags
the gap, per this corpus's cst_organizational_statute precedent for an
analogous un-executed rename instruction.

16 records: 7 اصلية, 8 معدلة, 0 ملغاة, 1 مضافة (Article 13bis). Flat
structure, no أبواب/فصول. No inline per-article titles in the source -- no
title_ar field is used.

A confirmed BOE source-level typographical defect ('دوان' for 'ديوان' in
Article 13's added paragraph 3, identical across both independent Wayback
snapshots) is preserved verbatim, not silently corrected.

No legal text is altered beyond whitespace/hyphen-style normalization, and
splicing each amendment decree's own quoted replacement/addition text into
the position its own operative clause specifies. Arabic governs; no
translation/paraphrase/interpretation performed on the Arabic text.
Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "tga_organizational_statute", "law", "official_source",
                   "tga_organizational_statute_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "tga_organizational_statute", "law", "verified")
RECORDS = os.path.join(OUT_VER, "tga_organizational_statute_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "tga_organizational_statute_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "tga_organizational_statute_arabic_legal_llm",
                        "tga_organizational_statute_legal_llm_001_016.json")

LAW_ID = "sa-tga-organizational-statute-323-1434"
LAW_AR = "تنظيم هيئة النقل العام ( الهيئة العامة للنقل )"
TOP_STATUS = ("MIXED_TIER_SEE_PER_ARTICLE_STATUS_BOE_WAYBACK_DUAL_SNAPSHOT_DEC2024_JUL2025_X_"
              "NEZAMS_COM_BASE_TEXT_CROSS_VERIFIED_X_UQN_GOV_SA_PRIMARY_GAZETTE_CAPTURE_FOR_"
              "ARTICLE_6_RESOLUTION_12_BOE_STALE_FOR_THAT_ARTICLE_X_ARTICLE_5_ENERGY_MINISTRY_"
              "AMENDMENT_CONFIRMED_TO_EXIST_BUT_NOT_TEXTUALLY_INCORPORATED_LIVE_BOE_TLS_RESET_"
              "THIS_PASS")
KEY_RE = r"tga_organizational_statute_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = {
    "tga_organizational_statute_art_001",
    "tga_organizational_statute_art_002",
    "tga_organizational_statute_art_004",
    "tga_organizational_statute_art_005",
    "tga_organizational_statute_art_006",
    "tga_organizational_statute_art_007",
    "tga_organizational_statute_art_009",
    "tga_organizational_statute_art_013",
}
ADDED_KEYS = {"tga_organizational_statute_art_013_mukarrar"}
REPEALED_KEYS = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام التنظيم اللائحة أحكام يجب يجوز "
            "عليه دون فيما منه منها وإذا حال وله ولها الهيئة المجلس الرئيس بوجه خاص").split())


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
        ver.append({"law_key": "tga_organizational_statute", "law_component": "law",
                    "language": "ar",
                    "record_layer": "TGA_ORGANIZATIONAL_STATUTE_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; this track rests on TWO Wayback "
                                              "Machine captures of laws.boe.gov.sa's own "
                                              "LawDetails page (16 Dec 2024 and 11 Jul 2025), "
                                              "cross-checked against nezams.com (base text + "
                                              "Resolutions 248/707) and, for Article 6 "
                                              "specifically (a confirmed BOE-stale gap), a "
                                              "Wayback capture of uqn.gov.sa's own Umm Al-Qura "
                                              "Gazette article page reproducing Resolution 12's "
                                              "full text verbatim -- a genuinely second PRIMARY "
                                              "source, not a secondary aggregator. Article 5's "
                                              "most recent (Ministry of Energy) amendment carries "
                                              "an unresolved decree-number conflict (382 per BOE, "
                                              "386 per qanoonsa.com) and its resulting text is "
                                              "not available from either source, so it is recorded "
                                              "in history only, not spliced into this article's "
                                              "text -- see verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track's tier as "
                                              "uniform across all eight amended articles. "
                                              "laws.boe.gov.sa's live portal returned a TLS reset "
                                              "on every direct attempt this pass."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "tga-organizational-statute-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "tga_organizational_statute/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من تنظيم هيئة النقل العام" %
                                          a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Council of Ministers Resolution No. "
                                                          "(323), 14/9/1434H — laws.boe.gov.sa "
                                                          "via two Wayback Machine snapshots "
                                                          "(16 Dec 2024, 11 Jul 2025); "
                                                          "nezams.com cross-check of base text + "
                                                          "Resolutions 248/707; uqn.gov.sa (Umm "
                                                          "Al-Qura Gazette) primary confirmation "
                                                          "of Resolution 12 for Article 6, a "
                                                          "confirmed BOE-stale gap; qanoonsa.com "
                                                          "for Article 5's Energy-Ministry "
                                                          "amendment (existence confirmed, exact "
                                                          "decree number and resulting text both "
                                                          "unresolved) -- live BOE portal TLS "
                                                          "reset this pass"),
                                     "source_authority_ar": "قرار مجلس الوزراء رقم (323) وتاريخ 14/9/1434هـ — عبر نسختين مؤرشفتين لدى Wayback Machine من صفحة هيئة الخبراء بمجلس الوزراء ذاتها (16 ديسمبر 2024، 11 يوليو 2025)؛ مطابقة مع nezams.com للنص الأصلي والقرارين 248 و707؛ وتأكيد أولي (جريدة أم القرى، uqn.gov.sa) للقرار (12) بخصوص المادة السادسة (فجوة مؤكدة في بيانات هيئة الخبراء)؛ ومطابقة مع qanoonsa.com لتعديل المادة الخامسة (وزارة الطاقة) مع بقاء رقم القرار والنص الناتج بعد إعادة الترتيب غير محسومين؛ تعذّر الوصول المباشر لبوابة هيئة الخبراء الحية (إعادة ضبط TLS) هذه الجولة",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "tga_organizational_statute",
               "layer": "TGA_ORGANIZATIONAL_STATUTE_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-tga-organizational-statute-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (16 مادة؛ 7 أصلية و8 معدلة و1 مضافة)",
               "title_en": "Organizing Statute of the General Authority for Transport (TGA) — "
                          "Arabic LLM-ready layer (16 records: 7 original, 8 amended, 1 added)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 15], "text_status": TOP_STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready TGA Organizational Statute records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
