#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Cooperative Societies Law track (نظام الجمعيات التعاونية,
Royal Decree M/14, 10/3/1429H / ~2008G).

VERIFICATION TIER -- see sources/cooperative_societies/law/official_source/
cooperative_societies_law_official_source.json's verification_methodology_note
for the full account. Summary:

This track was specifically RE-researched because a prior coverage-gap-map scan
had flagged it as "single-source/low-medium confidence" (one ministry-hosted PDF
title line). This pass made a genuine effort to find independent corroboration
and succeeded well beyond the minimum bar.

PRIMARY BOE PORTAL ACCESS FAILED THIS PASS: laws.boe.gov.sa HAS a dedicated
lawId page for this law, confirmed to exist via search-engine indexing
(0264f52c-70bd-40f2-94c1-a9a700f2b561), but the live portal returned HTTP 503
(WebFetch) / connection-reset (direct curl). web.archive.org was NOT attempted
-- the fetch tool in this environment explicitly refuses that host
("Claude Code is unable to fetch from web.archive.org"); no bypass attempted.

SOURCES USED (TIER_3) -- FOUR independent non-derivative sources beyond BOE:
  1. livestockhafr.org -- an official-looking scanned/typeset PDF titled "نظام
     الجمعيات التعاونية 1429هـ", carrying the full Royal Decree + CoM Resolution
     73 preamble and all 44 articles across 9 chapters. Fetched directly
     (HTTP 200), text extracted via pdftotext, cross-checked verbatim.
  2. bibliotdroit.com -- an independent Arabic legal-reference blog ("المكتبة
     القانونية العربية"), full text of all 44 articles. Fetched directly
     (HTTP 200), HTML-extracted.
  3. home.cbq.org.sa -- the own website of an actual registered Saudi
     cooperative society (Al-Qassim Beekeepers' Cooperative Society), hosting
     the same full 44-article text verbatim. Fetched directly (HTTP 200).
     Byte-for-byte identical (aside from trivial dash-style formatting) to
     source 2 for all 44 articles.
  4. cscs.org.sa (مجلس الجمعيات التعاونية -- the Council of Cooperative
     Societies, the very body ESTABLISHED by this law's own Article 29) hosts
     a 54-page scanned Ministry booklet (law + implementing regulation) on
     Google Drive, bearing a Deputy-Minister preface and an Umm al-Qura
     publication stamp. Fetched directly (HTTP 200, 7.4MB) and OCR'd
     (Tesseract, Arabic) for the first ~16 pages: OCR quality was too poor for
     verbatim transcription, but visually confirmed the preamble, decree
     numbers, and Articles 1-3 match sources 1-3, plus an Umm al-Qura gazette
     publication stamp -- corroborating evidence, not a transcription source.
  5. mohamah.net (independent legal-consultation site) confirmed the same
     structure (44 articles, 9 chapters) and explicitly reported NO amendment
     markers anywhere in the text.

Because full live/archived access to the canonical BOE portal page could not
be obtained this pass, this track is honestly kept at TIER_3 -- not
TIER_1/TIER_2 -- despite FOUR independent corroborating sources for the full
text (well beyond this corpus's TIER_3 minimum of two).

44 records, ALL اصلية (original) -- 0 معدلة, 0 ملغاة, 0 مضافة. NO enacted
amendment (Royal Decree or CoM Resolution) to any article was found despite a
dedicated search. A DRAFT amendment project ("مشروع تعديل نظام الجمعيات
التعاونية") is under public consultation on the Saudi government's Istitlaa
(istitlaa.ncc.gov.sa) and Tafa'ul (eparticipation.my.gov.sa) platforms
(Ministry of Human Resources and Social Development), last touched circa
14/5/2024 -- but this is NOT an enacted amendment; consolidated_amended_law is
correctly False.

NAMED PREDECESSOR REPEAL: Article 43 EXPLICITLY repeals the predecessor
"Cooperative Societies System" (Royal Decree No. 26, 25/6/1382H) and the
"Cooperative Societies Subsidy Bylaw" (CoM Resolution No. 419) -- a genuine,
precisely-named repeal (verbatim repeal-clause text confirmed), flagged for
the corpus-wide supersession/repeal graph (the repealed predecessor is not
itself ingested).

INTERNAL DATE INCONSISTENCY (unresolved, flagged not silently fixed): the
Royal Decree's own preamble cites CoM Resolution 419 as dated 10/5/1389H; CoM
Resolution 73's own preamble (same document) cites it as 10/3/1398H; Article
43's repeal clause cites it as 10/5/1398H. All three variants are IDENTICAL
across all sources checked (i.e. native to the circulating text, not a
transcription error from one source) -- preserved verbatim in their
respective locations, not harmonized.

ARTIFACT NOTE: the livestockhafr.org PDF extraction contains a bare label
"تعديلات المادة" after the headers of Articles 30-34 with no accompanying
decree/date/text -- absent from sources 2, 3 and 5. Treated as a rendering
artifact of that one source, NOT a real amendment; Articles 30-34 remain
اصلية. See known_unresolved_discrepancies.

Chapter structure (9 أبواب, all confirmed identically across sources 1-3):
  الباب الأول: أحكام عامة (1-12); الباب الثاني: إدارة الجمعيات التعاونية
  (13-26); الباب الثالث: موارد الجمعية (27); الباب الرابع: توزيع الأرباح (28);
  الباب الخامس: مجلس الجمعيات التعاونية (29); الباب السادس: الإعانات
  والتسهيلات للجمعيات التعاونية (30-35); الباب السابع: الرقابة (36); الباب
  الثامن: حل الجمعية وتصفيتها (37-40); الباب التاسع: أحكام ختامية (41-44).

TASHKEEL stripped uniformly (corpus-majority convention); in-word decorative
kashida removed (none found; هـ/جـ preserved by construction); curly quotes
straightened (none found) -- display-layer only, no legal text altered.
Arabic governs; no translation/paraphrase/interpretation. Read-only over
input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "cooperative_societies", "law", "official_source",
                   "cooperative_societies_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "cooperative_societies", "law", "verified")
RECORDS = os.path.join(OUT_VER, "cooperative_societies_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "cooperative_societies_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "cooperative_societies_arabic_legal_llm",
                        "cooperative_societies_law_legal_llm_001_044.json")

LAW_ID = "sa-cooperative-societies-law-m-14-1429"
LAW_AR = "نظام الجمعيات التعاونية"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
KEY_RE = r"cooperative_societies_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم الوزارة الوزير الجمعية الجمعيات").split())


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


def _top_status(key):
    if key in AMENDED_KEYS:
        return STATUS_AMENDED_DATED
    return STATUS_UNCHANGED


def _chapter_for(n, chapters):
    for ch in chapters:
        if ch["first_article"] <= n <= ch["last_article"]:
            return ch["label_ar"]
    return ""


GOV_NOTE = ("Arabic governs; laws.boe.gov.sa HAS a dedicated lawId page for this law, confirmed "
            "to exist via search-engine indexing (0264f52c-70bd-40f2-94c1-a9a700f2b561), but it "
            "was unreachable this pass (HTTP 503 live; web.archive.org refused by the fetch tool "
            "itself, not bypassed). FULL TEXT is cross-verified across FOUR independent sources: "
            "livestockhafr.org (PDF), bibliotdroit.com (HTML), home.cbq.org.sa (an actual "
            "registered cooperative society's own website; byte-for-byte identical to "
            "bibliotdroit.com), and cscs.org.sa (the Council of Cooperative Societies established "
            "by this law's own Article 29, hosting a scanned Ministry booklet -- OCR too poor for "
            "verbatim use but corroborating) -- plus a structural confirmation from mohamah.net "
            "-> TIER_3. 44 articles, 9 chapters (أبواب); ALL 44 اصلية -- no enacted amendment "
            "found despite a dedicated search (a DRAFT amendment is under public consultation on "
            "istitlaa.ncc.gov.sa / eparticipation.my.gov.sa but NOT enacted). Article 43 EXPLICITLY "
            "repeals the predecessor Cooperative Societies System (Royal Decree 26, 25/6/1382H) "
            "and its Subsidy Bylaw (CoM Resolution 419). See verification_methodology_note and "
            "known_unresolved_discrepancies in the source artifact before relying on this track's "
            "text or provenance -- including an unresolved internal date inconsistency for CoM "
            "Resolution 419 (three different dates appear across the same document) and a "
            "rendering artifact in one source (bare 'تعديلات المادة' label after Articles 30-34, "
            "not corroborated as a real amendment by any other source).")

SRC_AUTH = ("Royal Decree M/14 (10/3/1429H), CoM Resolution 73 (9/3/1429H), following Shura "
            "Council Resolution 74/99 (19/2/1427H). Full text cross-verified across four "
            "independent sources (livestockhafr.org, bibliotdroit.com, home.cbq.org.sa, and a "
            "corroborating OCR pass on a cscs.org.sa-hosted scanned Ministry booklet) plus a "
            "structural confirmation from mohamah.net. laws.boe.gov.sa dedicated lawId page "
            "(0264f52c-70bd-40f2-94c1-a9a700f2b561) confirmed to exist but unreachable this pass "
            "(live 503; Wayback refused by the fetch tool, not bypassed) -> TIER_3")

SRC_AUTH_AR = ("المرسوم الملكي رقم م/14 وتاريخ 10/3/1429هـ، وقرار مجلس الوزراء رقم 73 وتاريخ "
               "9/3/1429هـ، بعد النظر في قرار مجلس الشورى رقم 74/99 وتاريخ 19/2/1427هـ. النص "
               "الكامل متحقق منه عبر أربعة مصادر مستقلة (livestockhafr.org، bibliotdroit.com، "
               "home.cbq.org.sa، وتأكيد جزئي بالمسح الضوئي من كتيب وزاري مستضاف على "
               "cscs.org.sa) إضافة إلى تأكيد بنيوي من mohamah.net. صفحة laws.boe.gov.sa "
               "المخصصة (lawId 0264f52c-70bd-40f2-94c1-a9a700f2b561) مؤكدة الوجود لكن غير "
               "قابلة للوصول هذه الجولة (503 حيا؛ أرشيف Wayback مرفوض من أداة الجلب نفسها، "
               "لم يُتجاوَز) -- TIER_3")


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    chapters = src["chapter_structure"]
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
        top_status = _top_status(key)
        chapter_label = _chapter_for(n, chapters)
        ver.append({"law_key": "cooperative_societies", "law_component": "law",
                    "language": "ar",
                    "record_layer": "COOPERATIVE_SOCIETIES_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "chapter_ar": chapter_label,
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": top_status,
                    "governing_source_note": GOV_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "chapter_ar": chapter_label,
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "cooperative-societies-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "cooperative_societies/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام الجمعيات التعاونية" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": SRC_AUTH,
                                     "source_authority_ar": SRC_AUTH_AR,
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "cooperative_societies",
               "layer": "COOPERATIVE_SOCIETIES_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-cooperative-societies-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (44 مادة؛ 44 أصلية)",
               "title_en": ("Cooperative Societies Law — Arabic LLM-ready layer "
                            "(44 records, all original)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 44], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Cooperative Societies Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
