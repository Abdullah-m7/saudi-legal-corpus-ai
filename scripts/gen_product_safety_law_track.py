#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Product Safety Law track (نظام سلامة المنتجات,
Royal Decree M/36, 29/1/1446H / 5 August 2024G; published Umm al-Qura
Issue 5043, 16/8/2024G).

CRITICAL DECREE-NUMBER CORRECTION -- the coverage-gap-map that flagged this
law cited Royal Decree "M/148, 2024" for BOTH this law and its sibling, the
Standards and Quality Law. That number could not be confirmed anywhere
(direct web search, laws.boe.gov.sa, nezams.com, qanoonsa.com, decreesa.com,
or secondary legal commentary). Every independent source -- including an
OFFICIAL government source (Umm al-Qura Gazette, uqn.gov.sa) -- converges
instead on Royal Decree M/36, dated 29/1/1446H, approving Council of
Ministers Resolution No. 93 (24/1/1446H). "M/148" is NOT used in this track.

RELATIONSHIP TO THE STANDARDS AND QUALITY LAW -- the SAME Royal Decree M/36
contains TWO separate clauses: Clause One (البند أولا) approves THIS law
(نظام سلامة المنتجات, 37 articles / 9 أبواب); Clause Two (البند ثانيا)
approves the Standards and Quality Law (نظام المواصفات والجودة, 24 articles
/ 7 أبواب, track_id: standards_quality) -- a wholly distinct statute on a
different subject, jointly promulgated in the same decree instrument. This
is NOT a decree-number collision across different Hijri years and NOT one
law under two names; it is two genuinely separate laws sharing one joint
enacting decree (a normal, documented Saudi legislative practice). See
sources/product_safety/law/official_source/product_safety_law_official_source.json's
verification_methodology_note for the full account, including the two
official Umm al-Qura Gazette citations (uqn.gov.sa/details?p=26780 for this
law's "البند أولا"; uqn.gov.sa/details?p=26778 for the sibling's "البند
ثانيا") that literally quote the decree and, in passing, this law's own
Article 36 text verbatim.

VERIFICATION TIER: TIER_2. An official government source (Umm al-Qura
Gazette notices for both laws' later Executive Regulations) confirms the
decree/resolution identity and quotes Article 36's text verbatim (matching
this track exactly); the full 37-article text is primarily from qanoonsa.com,
cross-checked word-for-word against nezams.com (independent, non-derivative)
with only two structural gaps found and resolved (see discrepancies below).
laws.boe.gov.sa itself returned connection resets / HTTP 503 on every
attempt this pass; web.archive.org was NOT attempted (org egress-policy
block, not bypassed, per this corpus's convention).

37 records, ALL اصلية (no confirmed amendments as of 2026-07-24), 0 ملغاة,
0 مضافة. 9 أبواب (chapters): التعريفات (1) -- أحكام عامة (2-4) -- التزامات
السلامة العامة (5-15) -- التزامات السلامة الخاصة (16-18) -- جهات تقويم
المطابقة (19-23) -- مراقبة الأسواق (24-30) -- المسؤولية عن الخلل في المنتج
(31-32) -- إيقاع العقوبات (33-35) -- أحكام ختامية (36-37).

TWO SOURCE-SIDE STRUCTURAL GAPS RESOLVED (no wording disputes): (1)
qanoonsa.com's HTML lacks a distinct heading for Article 5 (it is merged
into a paragraph trailing Article 4); Article 5's text is taken from
nezams.com instead, and matches qanoonsa's merged paragraph word-for-word.
(2) nezams.com's HTML is missing the "الباب الرابع: التزامات السلامة
الخاصة" chapter heading between articles 15 and 16 (it jumps straight from
الباب الثالث to الباب الخامس); the chapter_structure used here (with الباب
الرابع covering articles 16-18) is qanoonsa.com's, confirmed correct.

NO NAMED PREDECESSOR REPEAL: Article 37 (closing article) carries only a
generic conflict clause ("ويلغي ما يتعارض معه أحكام") -- no specific prior
law/regulation is named. This is a new, substantively founding statute (the
implementing body, SASO, was separately established by a much older decree,
M/10, 3/3/1392H, which this law does not touch).

Implementing Regulation (Minister of Commerce Decision No. 097, 18/5/1446H,
per SASO Board adoption) is OUT OF SCOPE this pass (one-instrument-per-pass
rule) -- flagged as a documented follow-up candidate.

TASHKEEL: essentially absent in both source sites for this law; any stray
diacritics/curly-quotes/nbsp/double-spaces normalized uniformly (display
layer only, no legal text altered). Arabic governs; no translation,
paraphrase or interpretation performed; read-only over input, deterministic
over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "product_safety", "law", "official_source",
                   "product_safety_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "product_safety", "law", "verified")
RECORDS = os.path.join(OUT_VER, "product_safety_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "product_safety_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "product_safety_arabic_legal_llm",
                        "product_safety_law_legal_llm_001_037.json")

LAW_ID = "sa-product-safety-law-m-36-1446"
LAW_AR = "نظام سلامة المنتجات"
STATUS_UNCHANGED = "UNCHANGED"
KEY_RE = r"product_safety_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم الهيئة المجلس المحافظ اللجنة").split())


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


STATUS_MAIN = ("UQN_OFFICIAL_GAZETTE_DECREE_M36_CITATION_CONFIRMED_X_QANOONSA_PRIMARY_TEXT_"
               "X_NEZAMS_CROSS_VERIFIED_BOE_LAWID_UNREACHABLE")
STATUS_ART5 = ("UQN_OFFICIAL_GAZETTE_DECREE_M36_CITATION_CONFIRMED_X_NEZAMS_PRIMARY_TEXT_"
               "QANOONSA_MARKUP_GAP_AT_ART5_CROSS_VERIFIED_BOE_LAWID_UNREACHABLE")

GOV_NOTE = ("Arabic governs. Decree-number CORRECTED from the coverage-gap-map's unconfirmable "
            "M/148 to the multi-source-confirmed Royal Decree M/36 (29/1/1446H / 5 Aug 2024G), "
            "approving CoM Resolution 93 (24/1/1446H), published Umm al-Qura Issue 5043 "
            "(16/8/2024G). This same decree's Clause Two (البند ثانيا) separately approved the "
            "wholly distinct Standards and Quality Law (track_id: standards_quality) -- two "
            "different statutes jointly promulgated in one decree, not a numbering collision "
            "and not one law under two names. laws.boe.gov.sa was unreachable this pass "
            "(connection reset / HTTP 503; Wayback egress-blocked, NOT bypassed). An official "
            "Umm al-Qura Gazette notice (uqn.gov.sa/details?p=26780) quotes the decree AND this "
            "law's Article 36 verbatim, matching this track exactly -> TIER_2. Full text "
            "primarily from qanoonsa.com, cross-checked against nezams.com; Article 5 sourced "
            "from nezams.com instead (qanoonsa's markup merges it into Article 4); the "
            "chapter_structure's الباب الرابع (arts 16-18) is confirmed via qanoonsa.com (missing "
            "from nezams.com's markup). 37 articles, ALL اصلية, 9 أبواب, no confirmed amendments "
            "(checked 2026-07-24), no named-predecessor repeal (Art 37 is a generic conflict "
            "clause only). See verification_methodology_note and known_unresolved_discrepancies "
            "in the source artifact before relying on this track's text or provenance.")

SRC_AUTH = ("Royal Decree M/36 (29/1/1446H / 5 Aug 2024G), CoM Resolution 93 (24/1/1446H), "
            "published Umm al-Qura Issue 5043 (16/8/2024G). Decree number CORRECTED from the "
            "coverage-gap-map's unconfirmable M/148. Full text from qanoonsa.com, cross-checked "
            "against nezams.com (Article 5 taken from nezams.com due to a qanoonsa markup gap; "
            "chapter 4 heading taken from qanoonsa.com due to a nezams markup gap). An official "
            "Umm al-Qura Gazette notice (uqn.gov.sa/details?p=26780) independently confirms the "
            "decree and quotes Article 36 verbatim. laws.boe.gov.sa unreachable this pass (503 / "
            "connection reset; Wayback egress-blocked, not bypassed) -> TIER_2")

SRC_AUTH_AR = ("المرسوم الملكي رقم م/36 وتاريخ 29/1/1446هـ (الموافق 5 أغسطس 2024م)، وقرار مجلس "
               "الوزراء رقم 93 وتاريخ 24/1/1446هـ (منشور بأم القرى العدد 5043 بتاريخ 16/8/2024م). "
               "رقم المرسوم مصحح من (م/148) غير المؤكد في خريطة الفجوات الأولية. النص الكامل من "
               "qanoonsa.com، متقاطع مع nezams.com (المادة الخامسة من nezams.com لثغرة ترميز في "
               "qanoonsa؛ عنوان الباب الرابع من qanoonsa.com لثغرة ترميز في nezams). إشعار جريدة "
               "أم القرى الرسمية (uqn.gov.sa/details?p=26780) يؤكد المرسوم ويقتبس نص المادة 36 "
               "حرفيا. تعذر الوصول الحي لـlaws.boe.gov.sa هذه الجولة (503 / connection reset؛ "
               "Wayback محظور، لم يُتجاوَز) -- TIER_2")


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
        top_status = STATUS_UNCHANGED
        ver.append({"law_key": "product_safety", "law_component": "law",
                    "language": "ar",
                    "record_layer": "PRODUCT_SAFETY_LAW_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": GOV_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "product-safety-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "product_safety/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام سلامة المنتجات" % a["number_label_ar"]],
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
    json.dump({"law_key": "product_safety",
               "layer": "PRODUCT_SAFETY_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-product-safety-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (37 مادة؛ جميعها أصلية)",
               "title_en": ("Product Safety Law — Arabic LLM-ready layer "
                            "(37 records, all original)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 37], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Product Safety Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
